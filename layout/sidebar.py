# components/Sidebar.py

import dash_bootstrap_components as dbc
from dash import html

def sidebar():
    return html.Div(
        [
            html.H4("Table of Content", className="mb-3"),
            html.Hr(),
            dbc.Nav(
                [
                    html.A("Overview", href="#overview", className="link-underline link-underline-opacity-0"),
                    html.A("Age", href="#age", className="link-underline link-underline-opacity-0"),
                    html.A("Gender", href="#gender", className="link-underline link-underline-opacity-0"),
                    html.A("Purchase vs Browsing Frequency", href="#purfreq", className="link-underline link-underline-opacity-0"),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        className="sidebar sticky-top p-3 container",
        style={"minHeight": "100vh"},
    )


