import json
import dash_bootstrap_components as dbc
from dash import html, dcc
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

fig_age_cat = px.bar(
    age_cat_counts.sort_values("Age_Categories"),
    x="Age_Categories",
    y="purchase_count",
    title="Derived Age Categories Data",
    labels={"purchase_count": "# purchases"},
    text="purchase_count",
    template="plotly_white"
)

fig_age_cat_sorted = px.bar(
    age_cat_counts.sort_values("purchase_count", ascending=False),
    x="Age_Categories",
    y="purchase_count",
    title="Sorted Derived Age Categories Data",
    labels={"purchase_count": "# purchases"},
    text="purchase_count",
    template="plotly_white"
)


fig = px.bar(age_counts, x="age", y="purchase_count", title="Purchases by Age", template="plotly_white",
)


age = dbc.Row(
    children=[
        dbc.Col(
            dbc.Row(
                [
                    dbc.Col(html.H1("Age"), width=12),
                ]
            ),
        ),
        dbc.Col(
            FigureCard(
                id="age",
                title="Purchases by Age",
                figure=fig,
                description="This chart shows how many purchases were made by each age group."
            ),
            width=12,
        ),
        dbc.Col(
            FigureCard(
                id="age-categories",
                title="Derived Age Categories Data",
                figure=fig_age_cat,
                description="Grouped ages into categories like Teenager, Adult, etc., and counted purchases."
            ),
            width=12,
        ),
        dbc.Col(
            FigureCard(
                id="age-categories-sorted",
                title="Sorted Derived Age Categories Data",
                figure=fig_age_cat_sorted,
                description="Same age categories sorted by number of purchases."
            ),
            width=12,
        ),
    ],
    id="age",
)

