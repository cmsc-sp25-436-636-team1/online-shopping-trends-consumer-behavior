import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
class FigureCard(dbc.Card):
    def __init__(self, title, id, figure=None, caption=""):
        super().__init__(
            children=[
                html.Div(
                    [
                        html.Div(
                            [
                                html.H5(title, className="m-0"),
                                html.P(caption, className="m-0 text-muted"),
                            ],
                            className="d-flex flex-column justify-content-center"
                        ),
                    ],
                    className="d-flex justify-content-between align-items-center p-3",
                ),

                # Graph area
                dbc.Spinner(
                    dcc.Graph(
                        id={"type": "graph", "index": id},
                        figure=figure,
                        style={"height": "100%", "padding-bottom": "1 rem"},
                        responsive=True,
                    ),
                    size="lg",
                    color="dark",
                    delay_show=750,
                ),
            ],
            className="mb-3 figure-card",
        )
