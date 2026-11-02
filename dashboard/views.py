from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View

from config.settings import logger

from .forms import ShareModelForm
from .models import PriceHistory, Share
from .services.graph import get_graph
from .services.market_data import get_historical_prices

PRICE_HISTORY_PERIODS = {
    "1d": ("День", 1),
    "7d": ("7 дней", 7),
    "30d": ("30 дней", 30),
    "90d": ("90 дней", 90),
    "180d": ("180 дней", 180),
    "all": ("Всё время", None),
}


class IsUserAuthenticatedMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated

    @staticmethod
    def handle_no_permission():
        return redirect("dashboard:index")


class ShareListView(ListView):
    """Список акций"""

    model = Share
    template_name = "dashboard/list.html"
    paginate_by = 100
    ordering = ["name"]


class ShareDetailView(View):
    def get(self, request, pk):
        try:
            share = Share.objects.get(id=pk)
        except Share.DoesNotExist as exc:
            raise Http404("Акция не найдена") from exc

        history_error = None
        if not share.is_demo and settings.TINKOFF_TOKEN:
            if not PriceHistory.objects.filter(share=share).exists():
                try:
                    prices = get_historical_prices(share)
                    PriceHistory.objects.bulk_create(
                        [
                            PriceHistory(
                                share=share, price=price, recorded_at=recorded_at
                            )
                            for price, recorded_at in prices
                        ],
                        ignore_conflicts=True,
                    )
                except Exception:
                    logger.exception(
                        "Could not load historical prices for share %s", share.pk
                    )
                    history_error = (
                        "Не удалось загрузить котировки. Проверьте токен и "
                        "доступность Tinkoff Invest API."
                    )

        period = request.GET.get("period", "180d")
        if period not in PRICE_HISTORY_PERIODS:
            period = "30d"
        period_days = PRICE_HISTORY_PERIODS[period][1]
        history = PriceHistory.objects.filter(share=share).order_by("recorded_at")
        if period_days is not None:
            history = history.filter(
                recorded_at__gte=timezone.now() - timedelta(days=period_days)
            )

        first_record = history.first()
        last_record = history.last()
        change = None
        change_percent = None
        if first_record and last_record:
            change = last_record.price - first_record.price
            if first_record.price:
                change_percent = change / first_record.price * Decimal("100")

        return render(
            request,
            "dashboard/detail.html",
            {
                "plot_div": get_graph(history),
                "share": share,
                "period": period,
                "periods": PRICE_HISTORY_PERIODS,
                "history_count": history.count(),
                "first_record": first_record,
                "last_record": last_record,
                "change": change,
                "change_percent": change_percent,
                "history_error": history_error,
                "market_data_configured": bool(settings.TINKOFF_TOKEN),
            },
        )


class ShareCreateView(IsUserAuthenticatedMixin, CreateView):
    """Добавление инструмента"""

    template_name = "dashboard/create.html"
    form_class = ShareModelForm
    success_url = reverse_lazy("dashboard:index")


class ShareUpdateView(IsUserAuthenticatedMixin, UpdateView):
    """Редактирование инструмента"""

    model = Share
    template_name = "dashboard/create.html"
    form_class = ShareModelForm
    success_url = reverse_lazy("dashboard:index")


class ShareDeleteView(IsUserAuthenticatedMixin, DeleteView):
    """Удаление задачи"""

    model = Share
    template_name = "dashboard/delete.html"
    success_url = reverse_lazy("dashboard:index")
