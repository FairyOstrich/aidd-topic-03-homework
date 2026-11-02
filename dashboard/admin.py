from django.contrib import admin

from dashboard.models import PriceHistory, Share


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ("figi", "isin", "name", "ticker", "currency", "is_demo")
    search_fields = ("figi", "isin", "name", "ticker")
    fields = (
        "figi",
        "isin",
        "name",
        "ticker",
        "currency",
        "uid",
        "is_demo",
        "last_price",
        "is_trend_high",
    )


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ("share", "price", "recorded_at")
    list_filter = ("share",)
    date_hierarchy = "recorded_at"
    ordering = ("-recorded_at",)
    readonly_fields = ("share", "price", "recorded_at")
