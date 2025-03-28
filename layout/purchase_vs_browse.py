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

df['purchase_frequency'] = df['purchase_frequency'].astype(str).str.strip()
df['browsing_frequency'] = df['browsing_frequency'].astype(str).str.strip()


heatmap_data = pd.crosstab(df['browsing_frequency'], df['purchase_frequency'])

fig_heatmap = px.imshow(
    heatmap_data,
    text_auto=True,
    aspect='auto',
    color_continuous_scale='Greens',
    labels=dict(x="Purchase Frequency", y="Browsing Frequency", color="Count"),
)

purchase_vs_browse = dbc.Row([

    dbc.Col(html.H1("Purchase vs Browsing Frequency"),id="purfreq", width=12),
    html.P("""
           For the heatmap, with interactivity support, you can hover over each cell to see the value.
           We can see that the common case is that people like to browse a few times a week and like to purchase a few times a month.

           """),
    dbc.Col(
        FigureCard(
            id="heatmap-purchase-browsing",
            title="Heatmap: Purchase vs Browsing Frequency",
            figure=fig_heatmap,
            description="This heatmap shows how browsing frequency correlates with how often users make purchases."
        ),
        width=12
    )
    
    ]
)

