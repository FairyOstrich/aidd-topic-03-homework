from django.db import models


class Share(models.Model):
    """Акция"""

    figi = models.CharField(max_length=255, unique=True)
    isin = models.CharField(max_length=255)
    name = models.CharField(max_length=255, verbose_name="Наименование компании")
    ticker = models.CharField(max_length=10, unique=True, verbose_name="Тикер")
    currency = models.CharField(max_length=20, verbose_name="Валюта")
    uid = models.CharField(max_length=255, unique=True)
    is_demo = models.BooleanField(default=False, verbose_name="Демо-инструмент")
    last_price = models.FloatField(blank=True, null=True, verbose_name="Текущая цена")
    is_trend_high = models.BooleanField(
        blank=True, null=True, verbose_name="Растет цена"
    )
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"


class PriceHistory(models.Model):
    share = models.ForeignKey(
        Share, on_delete=models.CASCADE, related_name="price_history"
    )
    price = models.DecimalField(max_digits=20, decimal_places=9)
    recorded_at = models.DateTimeField()

    class Meta:
        ordering = ["recorded_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["share", "recorded_at"],
                name="unique_share_price_history_timestamp",
            )
        ]
        indexes = [models.Index(fields=["share", "recorded_at"])]
        verbose_name = "История цены"
        verbose_name_plural = "История цен"
