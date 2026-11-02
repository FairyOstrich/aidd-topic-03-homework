from datetime import datetime, timedelta
from datetime import timezone as datetime_timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from dashboard.models import PriceHistory, Share


class DashboardTests(APITestCase):
    def setUp(self) -> None:
        self.apple_share = Share.objects.create(
            figi="BBG000B9XRY4",
            isin="US0378331005",
            name="Apple",
            ticker="AAPL",
            currency="usd",
            uid="a9eb4238-eba9-488c-b102-b6140fd08e38",
            last_price=100.50,
            is_trend_high=True,
        )

        self.second_company = {
            "figi": "BBG000B9XRY5",
            "isin": "US0378331004",
            "name": "Company_test",
            "ticker": "TESTTEST",
            "currency": "usd",
            "uid": "a9eb4238-eba9-488c-b102-b6140fd08e39",
            "last_price": 1.50,
            "is_trend_high": False,
        }

    def test_share_list_html(self):
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "История цен")
        self.assertContains(
            response,
            reverse("dashboard:detail", args=[self.apple_share.pk]),
        )

    def test_share_list(self):
        response = self.client.get("/api/v1/shares/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        apple_share = response.json().get("results")[0]
        self.assertEqual(apple_share["id"], self.apple_share.id)
        self.assertEqual(apple_share["figi"], self.apple_share.figi)
        self.assertEqual(apple_share["isin"], self.apple_share.isin)
        self.assertEqual(apple_share["name"], self.apple_share.name)
        self.assertEqual(apple_share["ticker"], self.apple_share.ticker)
        self.assertEqual(apple_share["currency"], self.apple_share.currency)

    def test_share_detail(self):
        response = self.client.get("/api/v1/shares/")
        share_detail = response.json().get("results")[0]
        response = self.client.get(f"/api/v1/shares/{share_detail['id']}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_share_detail_invalid(self):
        response = self.client.get("/api/v1/shares/2/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_share_update(self):
        response = self.client.get("/api/v1/shares/")
        share_detail = response.json().get("results")[0]
        response = self.client.put(
            f"/api/v1/shares/{share_detail['id']}/",
            {
                "id": share_detail["id"],
                "figi": self.apple_share.figi,
                "isin": self.apple_share.isin,
                "name": f"{self.apple_share.name}_test",
                "ticker": self.apple_share.ticker,
                "currency": self.apple_share.currency,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(body["figi"], self.apple_share.figi)
        self.assertEqual(body["name"], f"{self.apple_share.name}_test")

    def test_share_update_invalid(self):
        response = self.client.get("/api/v1/shares/")
        share_detail = response.json().get("results")[0]
        response = self.client.put(
            f"/api/v1/shares/{share_detail['id']}/",
            {
                "figi": self.apple_share.figi,
                "name": f"{self.apple_share.name}_test",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_share_create(self):
        response = self.client.post(
            "/api/v1/shares/", self.second_company, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        body = response.json()
        self.assertEqual(body["figi"], self.second_company["figi"])
        self.assertEqual(body["name"], self.second_company["name"])
        self.assertEqual(body["ticker"], self.second_company["ticker"])

        response = self.client.get("/api/v1/shares/")
        self.assertEqual(len(response.data["results"]), 2)

    def test_share_create_invalid(self):
        response = self.client.post(
            "/api/v1/shares/", {"figi": "BBG000B9XRY5"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_share_delete(self):
        response = self.client.get("/api/v1/shares/")
        share_detail = response.json().get("results")[0]
        response = self.client.delete(f"/api/v1/shares/{share_detail['id']}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get("/api/v1/shares/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_share_delete_invalid(self):
        response = self.client.delete("/api/v1/shares/3/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MarketDataTests(TestCase):
    def test_price_conversion_includes_fractional_units(self):
        from dashboard.services.market_data import price_to_decimal, price_to_float

        price = SimpleNamespace(units=12, nano=345_000_000)
        self.assertAlmostEqual(price_to_float(price), 12.345)
        self.assertEqual(price_to_decimal(price), Decimal("12.345"))

    @patch("dashboard.tasks.get_last_data")
    def test_price_update_sets_trend_and_refreshes_timestamp(self, get_last_data):
        share = Share.objects.create(
            figi="figi-task",
            isin="isin-task",
            name="Task test",
            ticker="TASK",
            currency="usd",
            uid="uid-task",
            last_price=100.0,
            is_trend_high=False,
        )
        recorded_at = timezone.now()
        get_last_data.return_value = (Decimal("101.25"), recorded_at)
        old_timestamp = datetime(2000, 1, 1, tzinfo=datetime_timezone.utc)
        Share.objects.filter(pk=share.pk).update(updated_at=old_timestamp)

        from dashboard.tasks import update_last_price

        update_last_price()

        share.refresh_from_db()
        self.assertEqual(share.last_price, 101.25)
        self.assertTrue(share.is_trend_high)
        self.assertGreater(share.updated_at, old_timestamp)
        history = PriceHistory.objects.get(share=share)
        self.assertEqual(history.price, Decimal("101.25"))
        self.assertEqual(history.recorded_at, recorded_at)
        get_last_data.assert_called_once()

    @patch("dashboard.tasks.get_last_data")
    def test_price_update_does_not_duplicate_same_market_timestamp(self, get_last_data):
        share = Share.objects.create(
            figi="figi-repeat",
            isin="isin-repeat",
            name="Repeated quote",
            ticker="REPEAT",
            currency="usd",
            uid="uid-repeat",
        )
        recorded_at = timezone.now()
        get_last_data.side_effect = [
            (Decimal("10.25"), recorded_at),
            (Decimal("10.50"), recorded_at),
        ]

        from dashboard.tasks import update_last_price

        update_last_price()
        update_last_price()

        self.assertEqual(PriceHistory.objects.filter(share=share).count(), 1)
        self.assertEqual(PriceHistory.objects.get(share=share).price, Decimal("10.50"))


class PriceHistoryViewTests(TestCase):
    def setUp(self):
        self.share = Share.objects.create(
            figi="figi-history",
            isin="isin-history",
            name="History test",
            ticker="HISTORY",
            currency="usd",
            uid="uid-history",
        )
        self.now = timezone.now()
        PriceHistory.objects.create(
            share=self.share,
            price=Decimal("100.00"),
            recorded_at=self.now - timedelta(days=2),
        )
        PriceHistory.objects.create(
            share=self.share,
            price=Decimal("101.25"),
            recorded_at=self.now,
        )
        PriceHistory.objects.create(
            share=self.share,
            price=Decimal("80.00"),
            recorded_at=self.now - timedelta(days=40),
        )

    def test_detail_filters_period_and_reports_price_changes(self):
        response = self.client.get(
            reverse("dashboard:detail", args=[self.share.pk]), {"period": "7d"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["history_count"], 2)
        self.assertEqual(response.context["change"], Decimal("1.25"))
        self.assertEqual(response.context["change_percent"], Decimal("1.25"))
        self.assertContains(response, "История рыночных цен")
        self.assertContains(response, "1.25%")

    def test_detail_reports_empty_period(self):
        PriceHistory.objects.filter(share=self.share).delete()
        response = self.client.get(
            reverse("dashboard:detail", args=[self.share.pk]), {"period": "1d"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["history_count"], 0)
        self.assertIsNone(response.context["change"])
        self.assertContains(response, "История пока недоступна")

    @override_settings(TINKOFF_TOKEN="test-token")
    @patch(
        "dashboard.views.get_historical_prices",
        return_value=[
            (Decimal("50.25"), timezone.now() - timedelta(days=1)),
            (Decimal("51.75"), timezone.now()),
        ],
    )
    def test_detail_loads_real_history_when_no_snapshots_exist(self, get_prices):
        share = Share.objects.create(
            figi="figi-backfill",
            isin="isin-backfill",
            name="Backfill test",
            ticker="BACKFILL",
            currency="usd",
            uid="uid-backfill",
        )

        response = self.client.get(
            reverse("dashboard:detail", args=[share.pk]), {"period": "7d"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["history_count"], 2)
        self.assertEqual(PriceHistory.objects.filter(share=share).count(), 2)
        self.assertContains(response, "51.75")
        get_prices.assert_called_once_with(share)
