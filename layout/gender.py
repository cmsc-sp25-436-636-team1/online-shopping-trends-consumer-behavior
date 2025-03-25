import json
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, callback_context
import os
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .components.MetricCard import MetricCard
from .components.FigureCard import FigureCard

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Load data
with SessionLocal() as session:
    df = pd.read_sql("SELECT * FROM amz_customer_behavior", con=session.bind)

# Clean column names
df.columns = df.columns.str.strip().str.lower()

# Preprocess data
df['purchase_categories'] = df['purchase_categories'].astype(str)
df = df.assign(purchase_categories=df['purchase_categories'].str.split(';'))
df = df.explode('purchase_categories')
df['purchase_categories'] = df['purchase_categories'].str.strip()
grouped = df.groupby(['purchase_categories', 'gender']).size().reset_index(name='purchase_count')
summary = grouped.groupby('gender')['purchase_count'].sum().reset_index(name='total_purchases')

# Build figures
fig_overview = px.bar(
    grouped,
    x='purchase_count',
    y='purchase_categories',
    color='gender',
    orientation='h',
    title="Overview: Purchase Categories by Gender",
    template="plotly_white"
)

fig_compare = px.bar(
    grouped,
    x='purchase_count',
    y='purchase_categories',
    color='gender',
    facet_col='gender',
    orientation='h',
    title="Compare Purchase Categories by Gender",
    template="plotly_white"
)

fig_summary = px.pie(
    summary,
    values='total_purchases',
    names='gender',
    title="Total Purchases by Gender",
    template="plotly_white"
)

toggle_buttons = dbc.Row(
    dbc.Col(
        dbc.ButtonGroup(
            [
                dbc.Button("Overview", id='btn-overview', n_clicks=0),
                dbc.Button("Compare Genders", id='btn-compare', n_clicks=0),
                dbc.Button("Summary", id='btn-summary', n_clicks=0),
            ],
            className="mb-3"
        ),
        width="auto", 
        className="text-center"
    ),
    justify="center",
)


storyboard_container = html.Div(id='storyboard-container')

gender = dbc.Container(
    [
        html.H2("Amazon Consumer Behavior Storyboard"),
        toggle_buttons,
        storyboard_container
    ],
    id="purchase-storyboard",
    className="p-3"
)

def register_callbacks(app):
    @app.callback(
        Output('storyboard-container', 'children'),
        Input('btn-overview', 'n_clicks'),
        Input('btn-compare', 'n_clicks'),
        Input('btn-summary', 'n_clicks'),
    )
    def update_storyboard(btn1, btn2, btn3):
        ctx = callback_context
        if not ctx.triggered:
            button_id = 'btn-overview'
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'btn-compare':
            return FigureCard(
                id="compare-purchase",
                title="Compare Purchase Categories by Gender",
                figure=fig_compare,
                description="Faceted chart showing how purchase categories differ between genders."
            )
        elif button_id == 'btn-summary':
            return FigureCard(
                id="gender-summary",
                title="Total Purchases by Gender",
                figure=fig_summary,
                description="Pie chart summarizing the total number of purchases by gender."
            )
        else:
            return FigureCard(
                id="overview-purchase",
                title="Overview: Purchase Categories by Gender",
                figure=fig_overview,
                description="A comparison of purchase categories by gender across all responses."
            )