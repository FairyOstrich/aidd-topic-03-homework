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
        price = price_to_float(resp.price)
        return price, resp.time


def price_to_float(price):
    return price.units + price.nano / 1_000_000_000
