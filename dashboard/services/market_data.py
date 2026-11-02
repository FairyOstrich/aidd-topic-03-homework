from datetime import timedelta
from decimal import Decimal

from config.settings import TINKOFF_TOKEN, logger


def get_last_data(share):
    try:
        from tinkoff.invest import Client
    except ImportError as exc:
        raise RuntimeError(
            "Tinkoff SDK is missing. Install the optional requirements in "
            "requirements-market.txt."
        ) from exc

    with Client(TINKOFF_TOKEN) as client:
        resp = client.market_data.get_last_prices(figi=[share.figi])
        resp = resp.last_prices.pop()
        logger.info(f"Get last data for share with id {share.id}")
        price = price_to_decimal(resp.price)
        return price, resp.time


def get_historical_prices(share, days=180):
    try:
        from tinkoff.invest import CandleInterval, Client
        from tinkoff.invest.utils import now
    except ImportError as exc:
        raise RuntimeError(
            "Tinkoff SDK is missing. Install the optional requirements in "
            "requirements-market.txt."
        ) from exc

    with Client(TINKOFF_TOKEN) as client:
        return [
            (price_to_decimal(candle.close), candle.time)
            for candle in client.get_all_candles(
                figi=share.figi,
                from_=now() - timedelta(days=days),
                interval=CandleInterval.CANDLE_INTERVAL_DAY,
            )
        ]


def price_to_decimal(price):
    return Decimal(price.units) + Decimal(price.nano) / Decimal(1_000_000_000)


def price_to_float(price):
    return float(price_to_decimal(price))
