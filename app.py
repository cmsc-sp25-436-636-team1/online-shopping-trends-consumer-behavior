from dash import Dash, html, dcc, Input, Output, State, MATCH, ALL
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import dash
from layout.navbar import navbar
# from layout.filters import filters
from layout.dashboard import dashboard
from layout.about import about
from layout.overview import overview
from layout.age import age
from layout.gender import gender 
from layout.purchase_vs_browse import purchase_vs_browse 
from layout.sidebar import sidebar
from layout.gender import register_callbacks

# Load environment variables from .env
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



with SessionLocal() as session:
    df = pd.read_sql("SELECT * FROM amz_customer_behavior", con=session.bind)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server 

app = Dash(
    __name__,
    title="Online Shopping Trends & Consumer Behavior",
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200",  # Icons
        "https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap",  # Font
    ],
)
server = app.server

app.layout = html.Div(
    [

        navbar,
        
        dbc.Col(
            dbc.Row(
            [
                dbc.Col(sidebar(), width=3, style={"padding": "0"}),
                dbc.Col(
                    dbc.Container(
                        dbc.Stack(
                            [
                                overview,
                                about,
                                age,
                                gender,
                                purchase_vs_browse,
                            ],
                            gap=3,
                        ),
                        id="content",
                        className="p-3",
                    ),
                    width=9,
                ),
            ],className="gx-0",
            ),
            width=8,
            className="mx-auto"
        ),
    ],
    id="page",
)

@app.callback(Output("about-modal", "is_open"), Input("page-info-btn", "n_clicks"))
def show_about_modal(n):
    if n == 0:
        raise dash.exceptions.PreventUpdate()
    return True

@app.callback(
    Output({"type": "graph-modal", "index": MATCH}, "is_open"),
    Input({"type": "graph-info-btn", "index": MATCH}, "n_clicks"),
)
def show_graph_info_modals(n):
    if n == 0:
        raise dash.exceptions.PreventUpdate()
    return True

register_callbacks(app)


if __name__ == '__main__':
    app.run(debug=True)