from plotly.graph_objs import Scatter
from plotly.offline import plot


def get_graph(price_history):
    x_data = [entry.recorded_at for entry in price_history]
    y_data = [float(entry.price) for entry in price_history]
    plot_div = plot(
        {
            "data": [
                Scatter(
                    x=x_data,
                    y=y_data,
                    mode="lines",
                    name="Цена",
                    opacity=0.8,
                    marker_color="red",
                )
            ],
            "layout": {
                "title": "История цены",
                "xaxis": {"title": "Время"},
                "yaxis": {"title": "Цена"},
            },
        },
        output_type="div",
        show_link=False,
        link_text="",
    )
    return plot_div
