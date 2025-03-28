import json
import dash_bootstrap_components as dbc
from dash import html, dcc

from .components.MetricCard import MetricCard
from .components.FigureCard import FigureCard

with open("assets/figure_descriptions.json", "r") as f:
    figure_descriptions = json.load(f)

dashboard = dbc.Row(
    dbc.Col(
        [
         
        ],
    ),
    id="dashboard",
)