import json
import dash_bootstrap_components as dbc
from dash import html, dcc
import os
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from dash import html, dcc, Output, Input, callback_context

# Import your custom FigureCard component
from .components.FigureCard import FigureCard

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Load data
with SessionLocal() as session:
    df = pd.read_sql("SELECT * FROM amz_customer_behavior", con=session.bind)

# Prepare figures
age_counts = df.groupby("age")["id"].count().reset_index()
age_counts.columns = ["age", "purchase_count"]

def categorize_age(age):
    if age < 13:
        return "Child"
    elif age < 20:
        return "Teenager"
    elif age < 36:
        return "Young Adult"
    elif age < 51:
        return "Adult"
    elif age < 66:
        return "Middle-aged Adult"
    else:
        return "Older Adult"

df["Age_Categories"] = df["age"].apply(categorize_age)
age_cat_counts = df.groupby("Age_Categories")["id"].count().reset_index()
age_cat_counts.columns = ["Age_Categories", "purchase_count"]

category_order = [
    "Child", "Teenager", "Young Adult", "Adult", "Middle-aged Adult", "Older Adult"
]
age_cat_counts["Age_Categories"] = pd.Categorical(
    age_cat_counts["Age_Categories"], categories=category_order, ordered=True
)

fig_default = px.bar(
    age_counts,
    x="age",
    y="purchase_count",
    title="Purchases by Age",
    template="plotly_white",
    labels={"purchase_count": "# purchases"}
)

fig_age_cat = px.bar(
    age_cat_counts.sort_values("Age_Categories"),
    x="Age_Categories",
    y="purchase_count",
    title="Derived Age Categories Data",
    text="purchase_count",
    template="plotly_white",
    labels={"purchase_count": "# purchases"}
)

fig_age_cat_sorted = px.bar(
    age_cat_counts.sort_values("purchase_count", ascending=False),
    x="Age_Categories",
    y="purchase_count",
    title="Sorted Derived Age Categories Data",
    text="purchase_count",
    template="plotly_white",
    labels={"purchase_count": "# purchases"}
)

toggle_buttons = dbc.Row(
    dbc.Col(
        dbc.ButtonGroup(
            [
                dbc.Button("Default", id='btn-age-default', n_clicks=0),
                dbc.Button("Grouped", id='btn-age-group', n_clicks=0),
                dbc.Button("Sort Grouped", id='btn-age-sort-group', n_clicks=0),
            ],
            className="mb-3"
        ),
        width="auto", 
        className="text-center"
    ),
    justify="left",
)

age_card = FigureCard(
    id="age-figure",
    title="Age Data Transformation",        
    figure=fig_default,              
    description="This chart shows how many purchases were made by each age group."
)

age = dbc.Row(
    [
        dbc.Col(html.H1("Age Data Breakdown"), width=12),
        html.P("""
               For the task of Analyze & produce, Trends between age & gender for purchase frequency and purchase category and find Distribution of age and gender with # of purchases. In our dataset, Age (Customer’s age in years (quantitative/ integer))  would be the appropriate candidate for data transformation. 
               From the quantitative data attribute, we could group them by bins (range 0-10, 10-20, 20-30, etc). Keys are now bins, values are counts. On top of that, we could make it semantic by converting Age from quantitative to ordinal. 
               For example, we could derived
                0-10: Child
                10-20: Teenager
                20-30: Young adult 
                30-40: Adult
                40-50: Middle-age
                50+: Older Adult

               """),
        toggle_buttons,
        dbc.Col(age_card, width=12),
    ],
    id="age"
)

def register_age_callbacks(app):
    @app.callback(
        Output({"type": "graph", "index": "age-figure"}, "figure"),  # Use MATCH or literal match
        [
            Input("btn-age-default", "n_clicks"),
            Input("btn-age-group", "n_clicks"),
            Input("btn-age-sort-group", "n_clicks"),
        ]
    )
    def update_age_figure(n_default, n_group, n_sort_group):
        ctx = callback_context
        if not ctx.triggered:
            return fig_default
        button_id = ctx.triggered[0]["prop_id"].split('.')[0]

        if button_id == "btn-age-default":
            return fig_default
        elif button_id == "btn-age-group":
            return fig_age_cat
        elif button_id == "btn-age-sort-group":
            return fig_age_cat_sorted
        else:
            return fig_default
