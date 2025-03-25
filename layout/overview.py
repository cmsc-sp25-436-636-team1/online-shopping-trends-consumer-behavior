import json
import dash_bootstrap_components as dbc
from dash import html, dcc

from .components.MetricCard import MetricCard
from .components.FigureCard import FigureCard
from layout.table_overview import table

overview = dbc.Row(
    dbc.Col(
        [
            dbc.Row(
                [
                    dbc.Col(html.H1("Overview"), width=12),
                ]
            ),
            dbc.Row(
                [
                   dbc.Col(html.P("""This is a dataset collected for analyzing the behavioral analysis of Amazon's consumers consists of a comprehensive collection of customer interactions,
                                  browsing patterns within the Amazon ecosystem. It includes a wide range of variables such as customer demographics, user interaction, and reviews. 
                                  The dataset aims to provide insights into customer preferences, shopping habits, and decision-making processes on the Amazon platform. 
                                  By analyzing this dataset, researchers and analysts can gain a deeper understanding of consumer behavior, identify trends, optimize marketing strategies, and improve the overall customer experience on Amazon."""), 
                           width=12),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(MetricCard("Dataset Type", id="dataset-type", value="Table"), width=4),
                    dbc.Col(MetricCard("Attributes (Columns)", id="dataset-type", value="24"), width=4),
                    dbc.Col(MetricCard("Keys (Records)", id="dataset-type", value="602"), width=4),
                ]
            ),
            table,
            
            
        ],
    ),
    id="overview",
)