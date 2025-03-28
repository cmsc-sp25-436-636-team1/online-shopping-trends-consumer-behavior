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

from layout.navbar import navbar
from layout.about import about
from layout.overview import overview
from layout.age import age
from layout.gender import gender 
from layout.purchase_vs_browse import purchase_vs_browse 
from layout.purchase_categories import purchase_categories 
from layout.sidebar import sidebar
from layout.gender import register_callbacks
from layout.age import register_age_callbacks


load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Load data
with SessionLocal() as session:
    df = pd.read_sql("SELECT * FROM amz_customer_behavior", con=session.bind)
    
dash.register_page(__name__, 
                   path='/Overview',
                   title="Overview",)

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

layout = dbc.Container([
    dbc.Col(
        dbc.Row(
        [
            dbc.Col(sidebar(), width=2, style={"padding": "0"}),
            dbc.Col(
                dbc.Col(
                    dbc.Stack(
                        [
                            overview,
                            about,
                            age,
                            gender,
                            purchase_vs_browse,
                            purchase_categories
                        ],
                        gap=3,
                    ),
                    id="content",
                    className="p-3",
                ),
                width=10,
            ),
        ],className="gx-0",
        ),
        width=12,
        className="mx-auto"
    ),

], fluid=True)

