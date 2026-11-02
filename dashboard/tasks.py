from decimal import Decimal

from django.db import transaction

from config.celery import app
from config.settings import logger
from dashboard.models import PriceHistory, Share
from dashboard.services.market_data import get_last_data


@app.task
def update_last_price():
    shares = Share.objects.all()

    for share in shares:
        try:
            market_price, recorded_at = get_last_data(share)
            history_price = Decimal(str(market_price))
            last_price = float(history_price)

            with transaction.atomic():
                share.is_trend_high = (
                    share.last_price is None or last_price >= share.last_price
                )
                share.last_price = last_price
                share.save(update_fields=["last_price", "is_trend_high", "updated_at"])
                PriceHistory.objects.update_or_create(
                    share=share,
                    recorded_at=recorded_at,
                    defaults={"price": history_price},
                )
        except Exception as e:
            logger.error(e)
