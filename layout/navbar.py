import dash_bootstrap_components as dbc
from dash import html

navbar = dbc.NavbarSimple(
    [
        dbc.NavItem(
            dbc.NavLink(
                html.Img(
                    src="assets/github-mark-white.png",
                    alt="Source Code",
                    id="github-logo",
                ),
                href="https://github.com/cmsc-sp25-436-636-team1/online-shopping-trends-consumer-behavior",
                target="_blank",
                className="p-1",
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                dbc.Button(
                    html.Span(
                        "info",
                        className="material-symbols-outlined d-flex nav-span",
                    ),
                    color="dark",
                    id="page-info-btn",
                    n_clicks=0,
                )
            )
        ),
    ],
    brand="Online Shopping Trends & Consumer Behavior",
    brand_href="/",
    id="navbar",
    color="dark",
    dark=True,
)