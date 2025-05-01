import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

class FigureCard(dbc.Card):
    def __init__(self, title, id, figure=None, caption=""):
        super().__init__(
            children=[
                # Header area with dynamic title & caption placeholders
                html.Div(
                    [
                        # Title <h5> with pattern‐matching id
                        html.P(
                            title,
                            id={"type": "fig-title", "index": id},
                            className="m-0 font-size-bold"
                        ),
                        # Caption <p> with pattern‐matching id
                        html.P(
                            caption,
                            id={"type": "fig-caption", "index": id},
                            className="m-0 text-muted",
                            style={"font-size": "small"}
                        ),
                    ],
                    className="d-flex flex-column justify-content-center p-3",
                ),

                # Graph area (unchanged)
                dbc.Spinner(
                    dcc.Graph(
                        id={"type": "graph", "index": id},
                        figure=figure,
                        style={"height": "30vh", "padding-bottom": "1rem"},
                        responsive=True,
                    ),
                    size="lg",
                    color="dark",
                    delay_show=750,
                ),
            ],
            className="mb-3 figure-card",
        )

        
class BigFigureCard(dbc.Card):
    def __init__(self, title, id, figure=None, caption=""):
        super().__init__(
            children=[
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(id={"type": "fig-title", "index": id}, children=title, className="m-0 font-size-bold"),
                                html.P(id={"type": "fig-caption", "index": id}, children=caption, className="m-0 text-muted", style={"font-size": "small"}),
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
                        style={"height": "70vh", "padding-bottom": "1 rem"},
                        responsive=True,
                    ),
                    size="lg",
                    color="dark",
                    delay_show=750,
                ),
            ],
            className="mb-3 figure-card-big",
        )
