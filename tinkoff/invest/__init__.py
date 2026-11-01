from enum import Enum
from datetime import datetime, timezone


class CandleInterval(Enum):
    CANDLE_INTERVAL_DAY = "day"


def now():
    return datetime.now(timezone.utc)


class _Price:
    def __init__(self, units):
        self.units = units


class _LastPrice:
    def __init__(self, price, time):
        self.price = price
        self.time = time


class _LastPricesResponse:
    def __init__(self, last_prices):
        self.last_prices = last_prices


class _Candle:
    def __init__(self, time, close):
        self.time = time
        self.close = close


class MarketDataStub:
    def get_last_prices(self, figi):
        return _LastPricesResponse([])

    def get_all_candles(self, figi, from_, interval):
        return iter([])


class Client:
    def __init__(self, token):
        self.token = token
        self.market_data = MarketDataStub()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def get_all_candles(self, figi, from_, interval):
        return iter([])

