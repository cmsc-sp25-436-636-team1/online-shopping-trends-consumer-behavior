from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from layout.components.FigureCard import FigureCard

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Load data once globally
with SessionLocal() as session:
    df = pd.read_sql("SELECT * FROM amz_customer_behavior", con=session.bind)

import dash
dash.register_page(__name__, path='/Dashboard', title="Amazon Dashboard")

# Preprocessing
df['purchase_categories'] = df['purchase_categories'].astype(str).str.split(';')
df = df.explode('purchase_categories')
df['purchase_categories'] = df['purchase_categories'].str.strip()
df['purchase_frequency'] = df['purchase_frequency'].astype(str).str.strip()
df['browsing_frequency'] = df['browsing_frequency'].astype(str).str.strip()

category_order = ["Child", "Teenager", "Young Adult", "Adult", "Middle-aged Adult", "Older Adult"]
df['age_category'] = pd.Categorical(df['age_category'], categories=category_order, ordered=True)

bins = [0, 10, 20, 30, 40, 50, 60, 70]
bin_labels = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70']
df['age_bin'] = pd.cut(df['age'], bins=bins, labels=bin_labels, right=False)

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Label("Filter by Gender"),
            dcc.Dropdown(id="gender-filter", options=[{"label": g, "value": g} for g in df["gender"].unique()], multi=True)
        ], width=3),
        dbc.Col([
            html.Label("Filter by Age Category"),
            dcc.Dropdown(id="age-cat-filter", options=[{"label": a, "value": a} for a in df["age_category"].unique()], multi=True)
        ], width=3),
    ], className="my-3"),

    dbc.Row([
        dbc.Col(FigureCard("Purchases by Age Category", id="age-cat-bar"), width=3),
        dbc.Col(FigureCard("Cart Completion Frequency", id="cart-completion"), width=3),
        dbc.Col(FigureCard("Shopping Satisfaction (Pie)", id="satisfaction-pie"), width=3),
        dbc.Col(FigureCard("Heatmap: Browse vs Purchase", id="heatmap-behavior"), width=3),
    ], className="gy-3"),
    dbc.Row([
        dbc.Col(FigureCard("Gendered Purchase Overview", id="gendered-bar"), width=6),
        dbc.Col(FigureCard("Bubble: Categories vs Age & Frequency", id="bubble"), width=6),
    ], className="gy-3"),
    dbc.Row([
        dbc.Col(FigureCard("Purchase Categories by Gender", id="gender-cat-facet"), width=6),
        dbc.Col(FigureCard("Review Importance vs Reliability", id="review-scatter"), width=6),
    ], className="gy-3"),
], fluid=True)

@callback(
    Output({"type": "graph", "index": "age-cat-bar"}, "figure"),
    Output({"type": "graph", "index": "cart-completion"}, "figure"),
    Output({"type": "graph", "index": "satisfaction-pie"}, "figure"),
    Output({"type": "graph", "index": "heatmap-behavior"}, "figure"),
    Output({"type": "graph", "index": "gendered-bar"}, "figure"),
    Output({"type": "graph", "index": "bubble"}, "figure"),
    Output({"type": "graph", "index": "gender-cat-facet"}, "figure"),
    Output({"type": "graph", "index": "review-scatter"}, "figure"),
    Input("gender-filter", "value"),
    Input("age-cat-filter", "value")
)
def update_figs(genders, age_cats):
    filtered = df.copy()
    if genders:
        filtered = filtered[filtered["gender"].isin(genders)]
    if age_cats:
        filtered = filtered[filtered["age_category"].isin(age_cats)]

    age_counts = filtered.groupby("age_category")["id"].count().reset_index(name="purchase_count")
    fig1 = px.bar(age_counts, x="age_category", y="purchase_count", template="plotly_white", height=240)

    completion = filtered['cart_completion_frequency'].value_counts().reset_index()
    completion.columns = ['frequency', 'count']
    fig2 = px.bar(completion, x='frequency', y='count', template='plotly_white', height=240)

    sat_data = filtered["shopping_satisfaction"].value_counts().reset_index(name="count")
    sat_data.columns = ["satisfaction", "count"]
    fig3 = px.pie(sat_data, names="satisfaction", values="count", hole=0.4, height=240)

    heatmap_data = pd.crosstab(filtered['browsing_frequency'], filtered['purchase_frequency'])
    fig4 = px.imshow(heatmap_data, text_auto=True, color_continuous_scale="Greens", height=240)

    gender_group = filtered.groupby(['purchase_categories', 'gender']).size().reset_index(name='purchase_count')
    fig5 = px.bar(gender_group, x='purchase_count', y='purchase_categories', color='gender', orientation='h', template="plotly_white", height=280)

    x_axis = ["Multiple times a week", "Once a week", "Few times a month", "Once a month", "Less than once a month"]
    df_sep = filtered.copy()
    df_sep["purch_cat_list"] = df_sep["purchase_categories"]
    df_bubble = (
        df_sep.groupby(["age_bin", "purchase_frequency", "gender", "purch_cat_list"], observed=True)
        .size().reset_index(name="count")
    )
    df_bubble['purchase_frequency'] = pd.Categorical(df_bubble['purchase_frequency'], categories=x_axis, ordered=True)
    df_bubble['age_bin'] = pd.Categorical(df_bubble['age_bin'], categories=bin_labels, ordered=True)
    df_bubble['xspacing'] = df_bubble['purchase_frequency'].cat.codes + np.random.uniform(-0.1, 0.1, len(df_bubble))
    df_bubble['yspacing'] = df_bubble['age_bin'].cat.codes + np.random.uniform(-0.3, 0.3, len(df_bubble))
    fig6 = px.scatter(df_bubble, x='xspacing', y='yspacing', size='count', color='gender', hover_name='purch_cat_list', height=300)
    fig6.update_layout(xaxis=dict(tickmode='array', tickvals=list(range(len(x_axis))), ticktext=x_axis))
    fig6.update_layout(yaxis=dict(tickmode='array', tickvals=list(range(len(bin_labels))), ticktext=bin_labels))

    fig7 = px.bar(gender_group, x='purchase_count', y='purchase_categories', color='gender', facet_col='gender', orientation='h', template="plotly_white", height=300)

    fig8 = px.strip(filtered, x="customer_reviews_importance", y="review_reliability", color="gender", height=280)

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8
