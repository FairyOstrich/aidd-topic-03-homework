from datetime import timedelta

from plotly.graph_objs import Scatter
from plotly.offline import plot

from config.settings import TINKOFF_TOKEN
from dashboard.services.market_data import price_to_float


def get_graph(share):
    try:
        from tinkoff.invest import CandleInterval, Client
        from tinkoff.invest.utils import now
    except ImportError as exc:
        raise RuntimeError(
            "Tinkoff SDK is missing. Install the optional requirements in "
            "requirements-market.txt."
        ) from exc

    with Client(TINKOFF_TOKEN) as client:
        x_data, y_data = [], []
        for candle in client.get_all_candles(
            figi=share.figi,
            from_=now() - timedelta(days=180),
            interval=CandleInterval.CANDLE_INTERVAL_DAY,
        ):
            x_data.append(candle.time.date())
            y_data.append(price_to_float(candle.close))
    plot_div = plot(
        [
            Scatter(
                x=x_data,
                y=y_data,
                mode="lines",
                name="test",
                opacity=0.8,
                marker_color="red",
            )
        ],
        output_type="div",
        show_link=False,
        link_text="",
    )
    return plot_div
