from dash import html, dcc, Input, Output, State, callback, ctx, no_update
import dash_bootstrap_components as dbc
import plotly_express as px
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import dash
import pandas as pd
from layout.components.FigureCard import FigureCard

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Load data
with SessionLocal() as session:
    df = pd.read_sql("SELECT * FROM amz_customer_behavior", con=session.bind)
    
dash.register_page(__name__, 
                   path='/Dashboard',
                   title="Dashboard",)

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Label("Filter by Gender"),
            dcc.Dropdown(id="gender-filter", options=[], multi=True)
        ], width=3),
        dbc.Col([
            html.Label("Filter by Age"),
            dcc.Dropdown(id="age-filter", options=[], multi=True)
        ], width=3),
    ], className="my-3"),

    dbc.Row([
        dbc.Col(FigureCard("Purchase Frequency Distribution", id="purchase-freq"), width=6),
        dbc.Col(FigureCard("Browsing Frequency by Age", id="browsing-age"), width=6),
    ]),
    dbc.Row([
        dbc.Col(FigureCard("Customer Review Importance", id="review-importance"), width=6),
        dbc.Col(FigureCard("Top Cart Abandonment Factors", id="cart-abandon"), width=6),
    ]),
    dbc.Row([
        dbc.Col(FigureCard("Recommendation Helpfulness vs Frequency", id="reco-compare"), width=6),
        dbc.Col(FigureCard("Shopping Satisfaction", id="satisfaction"), width=6),
    ]),
], fluid=True)

@callback(
    Output("gender-filter", "options"),
    Output("age-filter", "options"),
    Input("gender-filter", "id")  # dummy trigger
)
def populate_filter_options(_):
    genders = df["gender"].dropna().unique()
    ages = df["age"].dropna().unique()
    return (
        [{"label": g, "value": g} for g in genders],
        [{"label": str(a), "value": a} for a in sorted(ages)]
    )

# Graph Update Callback
@callback(
    Output({"type": "graph", "index": "purchase-freq"}, "figure"),
    Output({"type": "graph", "index": "browsing-age"}, "figure"),
    Output({"type": "graph", "index": "review-importance"}, "figure"),
    Output({"type": "graph", "index": "cart-abandon"}, "figure"),
    Output({"type": "graph", "index": "reco-compare"}, "figure"),
    Output({"type": "graph", "index": "satisfaction"}, "figure"),
    Input("gender-filter", "value"),
    Input("age-filter", "value"),
)
def update_graphs(genders, ages):
    filtered = df.copy()
    if genders:
        filtered = filtered[filtered["gender"].isin(genders)]
    if ages:
        filtered = filtered[filtered["age"].isin(ages)]

    # Plot 1: Purchase Frequency
    fig1 = px.histogram(filtered, x="purchase_frequency", title="Purchase Frequency")

    # Plot 2: Browsing Frequency by Age
    fig2 = px.box(filtered, x="age", y="browsing_frequency", title="Browsing Frequency by Age")

    # Plot 3: Customer Review Importance
    fig3 = px.histogram(filtered, x="customer_reviews_importance", title="Customer Review Importance")

    # Plot 4: Cart Abandonment Factors
    top_factors = filtered["cart_abandonment_factors"].value_counts().nlargest(10).reset_index()
    top_factors.columns = ["factor", "count"]
    fig4 = px.bar(top_factors, x="factor", y="count", title="Top Cart Abandonment Factors")

    # Plot 5: Recommendation Helpfulness vs Frequency
    fig5 = px.histogram(
        filtered,
        x="personalized_recommendation_frequency",
        color="recommendation_helpfulness",
        barmode="group",
        title="Recommendation Frequency vs Helpfulness"
    )

    # Plot 6: Shopping Satisfaction
    fig6 = px.histogram(filtered, x="shopping_satisfaction", title="Shopping Satisfaction")

    return fig1, fig2, fig3, fig4, fig5, fig6

