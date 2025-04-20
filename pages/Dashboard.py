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
from dash.exceptions import PreventUpdate

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Load data once globally
with SessionLocal() as session:
    df = pd.read_sql("SELECT * FROM amz_customer_behavior", con=session.bind)

import dash
dash.register_page(__name__, path='/Dashboard', title="Dashboard")

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

layout = dbc.Container(fluid=True, style={"min-height": "93vh", "backgroundColor": "#faf9f5"}, children=[

    # ——— Tabs ———
    dbc.Tabs(id="dashboard-tabs", active_tab="tab-demographics", className="mb-3", children=[

        dbc.Tab(label="Demographics", tab_id="tab-demographics", children=[
            dbc.Row([
                dbc.Col(FigureCard("Purchases by Age Category",
                                   caption="Counts of transactions aggregated into your predefined age brackets, revealing which age groups contribute most to overall purchasing volume",            
                                   id="age-cat-bar"), width=6),
                dbc.Col(FigureCard("Gender Breakdown", 
                                   caption="A pie chart showing each gender’s share of the customer base, quickly highlighting any skew in male/female representation"
                                   ,id="gender-pie"), width=6),
                
            ], className="gy-3"),

            dbc.Row([
                dbc.Col(FigureCard("Age by Gender", 
                                   caption="Box‑and‑whisker plots of customer ages split by gender, displaying medians, interquartile ranges, and outliers for direct comparison",
                                   id="age-box"), width=6),
                dbc.Col(FigureCard("Purchase Frequency by Gender", caption="Grouped bar chart comparing how often each gender shops (e.g., “Multiple times a week” vs. “Once a month”), illustrating behavioral differences across demographic segments",
                                   id="freq-gender-bar"), width=6),
            ], className="gy-3"),
        ]),
              
        dbc.Tab(
            label="Browse Vs Purchase",
            tab_id="tab-corr",
            children=[

                # Row 1: filters inside the tab
                dbc.Row([
                    dbc.Col([
                        html.Label("Filter by Gender"),
                        dcc.Dropdown(
                            id="gender-filter-corr",
                            options=[{"label": g, "value": g} for g in df["gender"].unique()],
                            multi=True,
                        ),
                    ], width=4),
                    dbc.Col([
                        html.Label("Filter by Age Category"),
                        dcc.Dropdown(
                            id="age-cat-filter-corr",
                            options=[{"label": a, "value": a}
                                    for a in df["age_category"].cat.categories],
                            multi=True,
                        ),
                    ], width=4),
                ], className="my-3",  justify='center', align='center'),

                # Row 2: the heatmap
                dbc.Row([
                    dbc.Col(
                        FigureCard(
                            "Browse Vs Purchase Correlation",
                            id="heatmap-behavior",
                            caption="Counts of users by browsing vs purchase frequency."
                        ),
                        width=6
                    ),
                ], className="gy-3", justify='center', align='center'),
            ],
        ),
        
    ]),
])


@callback(
    Output({"type": "graph", "index": "age-cat-bar"},     "figure"),
    Output({"type": "graph", "index": "gender-pie"},      "figure"),
    Output({"type": "graph", "index": "age-box"},         "figure"),
    Output({"type": "graph", "index": "freq-gender-bar"}, "figure"),
    Input("dashboard-tabs", "active_tab"),
)
def update_demographics_tab(active_tab): 
    if active_tab != "tab-demographics":
        raise PreventUpdate

    # 1) Purchases by Age Category (unique customers)
    age_counts = (
        df.groupby("age_category")["id"]
          .nunique()
          .reset_index(name="purchase_count")
    )
    fig_age_cat_bar = px.bar(
        age_counts,
        x="age_category",
        y="purchase_count",
        template="plotly_white",
        height=240,
    )
    fig_age_cat_bar.update_layout(
        xaxis_title="Age Category",
        yaxis_title="Number of Unique Customers",
        margin=dict(l=40, r=20, t=20, b=120),
    )
    fig_age_cat_bar.update_traces(
        hovertemplate=
          "<b>Age Group</b>: %{x}<br>" +
          "<b>Customers</b>: %{y:,}<extra></extra>"
    )

    # 2) Gender Breakdown (unique customers)
    gender_counts = (
        df.groupby("gender")["id"]
          .nunique()
          .reset_index(name="count")
    )
    fig_gender_pie = px.pie(
        gender_counts,
        names="gender",
        values="count",
        hole=0.4,
        height=240,
    )
    fig_gender_pie.update_layout(
        margin=dict(l=20, r=20, t=20, b=120),
        legend_title="Gender"
    )
    fig_gender_pie.update_traces(
        hovertemplate=
          "<b>Gender</b>: %{label}<br>" +
          "<b>Customers</b>: %{value:,}<extra></extra>"
    )

    # 3) Age by Gender (drop duplicate IDs)
    df_age = df.drop_duplicates(subset="id")[["gender", "age"]]
    fig_age_box = px.box(
        df_age,
        x="gender",
        y="age",
        template="plotly_white",
        height=240,
    )
    fig_age_box.update_layout(
        xaxis_title="Gender",
        yaxis_title="Age",
        margin=dict(l=40, r=20, t=20, b=120),
    )
    fig_age_box.update_traces(
        hovertemplate=
          "<b>Gender</b>: %{x}<br>" +
          "<b>Age</b>: %{y}<extra></extra>"
    )

    # 4) Purchase Frequency by Gender (unique customers)
    freq_gender = (
    df.groupby(["gender", "purchase_frequency"])["id"]
      .nunique()
      .reset_index(name="count")
    )

    fig_freq_gender_bar = px.bar(
        freq_gender,
        x="purchase_frequency",
        y="count",
        color="gender",
        barmode="group",
        template="plotly_white",
        height=240,
        custom_data=["gender"]          # <— inject gender into each point’s customdata
    )

    fig_freq_gender_bar.update_layout(
        xaxis_title="Purchase Frequency",
        yaxis_title="Number of Unique Customers",
        margin=dict(l=40, r=20, t=20, b=200),
        xaxis_tickangle=-45,
        legend_title="Gender"
    )

    fig_freq_gender_bar.update_traces(
        hovertemplate=
        "<b>Purchase Frequency</b>: %{x}<br>" +
        "<b>Customers</b>: %{y:,}<br>" +
        "<b>Gender</b>: %{customdata[0]}<extra></extra>"
    )

    return (
        fig_age_cat_bar,
        fig_gender_pie,
        fig_age_box,
        fig_freq_gender_bar,
    )
    
    
@callback(
    Output({"type": "graph", "index": "heatmap-behavior"}, "figure"),
    Input("dashboard-tabs",        "active_tab"),
    Input("gender-filter-corr",    "value"),
    Input("age-cat-filter-corr",   "value"),
)
def update_correlation_heatmap(active_tab, genders, age_cats):
    if active_tab != "tab-corr":
        raise PreventUpdate

    dff = df.copy()
    if genders:
        dff = dff[dff["gender"].isin(genders)]
    if age_cats:
        dff = dff[dff["age_category"].isin(age_cats)]

    heat_data = pd.crosstab(
        index=dff["browsing_frequency"],
        columns=dff["purchase_frequency"]
    )

    fig = px.imshow(
        heat_data,
        text_auto=True,
        aspect="auto",
        template="plotly_white",
        color_continuous_scale="Viridis",
        height=400,
    )
    fig.update_layout(
        xaxis_title="Purchase Frequency",
        yaxis_title="Browsing Frequency",
        margin=dict(l=40, r=20, t=30, b=80),
    )
    fig.update_traces(
        hovertemplate=
          "<b>Browsing</b>: %{y}<br>" +
          "<b>Purchase</b>: %{x}<br>" +
          "<b>Users</b>: %{z:,}<extra></extra>"
    )
    return fig

