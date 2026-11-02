import math
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import PriceHistory, Share


class Command(BaseCommand):
    help = "Create a clearly labeled synthetic share and 180 days of demo prices"

    def handle(self, *args, **options):
        share, _ = Share.objects.get_or_create(
            figi="DEMO-SHARE-HISTORY",
            defaults={
                "isin": "XX0000000000",
                "name": "Демонстрационная акция (синтетические данные)",
                "ticker": "DEMO",
                "currency": "USD",
                "uid": "DEMO-SHARE-HISTORY-UID",
                "is_demo": True,
            },
        )
        if not share.is_demo:
            share.is_demo = True
            share.save(update_fields=["is_demo"])

        if not PriceHistory.objects.filter(share=share).exists():
            end = timezone.now()
            rows = []
            for day in range(180, -1, -1):
                price = Decimal("100") + Decimal(day) * Decimal("0.08")
                price += Decimal(str(round(math.sin(day / 12) * 3, 6)))
                rows.append(
                    PriceHistory(
                        share=share,
                        price=price,
                        recorded_at=end - timedelta(days=day),
                    )
                )
            PriceHistory.objects.bulk_create(rows, ignore_conflicts=True)
            share.last_price = float(rows[-1].price)
            share.save(update_fields=["last_price", "updated_at"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo price history is ready: {share.ticker} ({share.pk})"
            )
        )
