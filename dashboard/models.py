from django.conf import settings
from django.db import models


class Share(models.Model):
    """Акция"""

    figi = models.CharField(max_length=255, unique=True)
    isin = models.CharField(max_length=255)
    name = models.CharField(max_length=255, verbose_name="Наименование компании")
    ticker = models.CharField(max_length=10, unique=True, verbose_name="Тикер")
    currency = models.CharField(max_length=20, verbose_name="Валюта")
    uid = models.CharField(max_length=255, unique=True)
    last_price = models.FloatField(blank=True, null=True, verbose_name="Текущая цена")
    is_trend_high = models.BooleanField(
        blank=True, null=True, verbose_name="Растет цена"
    )
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"


class Position(models.Model):
    """Позиция пользователя в акции"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="positions",
        verbose_name="Пользователь",
    )
    share = models.ForeignKey(
        Share,
        on_delete=models.CASCADE,
        related_name="positions",
        verbose_name="Акция",
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    purchase_price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Цена покупки"
    )
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата покупки")

    class Meta:
        verbose_name = "Позиция"
        verbose_name_plural = "Позиции"
        unique_together = ("user", "share")
