from dash import Dash, html, dcc, Input, Output, State, MATCH, ALL
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import dash
from flask import Flask, redirect

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
from pages import shop_navbar

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

server = Flask(__name__)

@server.route('/')
def index_redirect():
    return redirect('/Home')

app = Dash(
    __name__,
    title="Online Shopping Trends & Consumer Behavior",
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200",  # Icons
        "https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap",  # Font
    ],
)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR, dbc_css, dbc.icons.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200",
        "https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap"], 
        use_pages=True, suppress_callback_exceptions=True, server=server)

app.layout = dbc.Container([
    dcc.Location(id='app-location-id'),
    html.Div([

        dbc.Row(id='app-navbar-row-output')

    ], style={'margin': '0'}),
    dash.page_container
], class_name='m-0 g-0 w-100', id='PlsFix', fluid=True)


server = app.server

# app.layout = html.Div(
#     [
#         dcc.Location(id='url', refresh=False),
#         navbar,
        
#         dbc.Col(
#             dbc.Row(
#             [
#                 dbc.Col(sidebar(), width=2, style={"padding": "0"}),
#                 dbc.Col(
#                     dbc.Col(
#                         dbc.Stack(
#                             [
#                                 overview,
#                                 about,
#                                 age,
#                                 gender,
#                                 purchase_vs_browse,
#                                 purchase_categories
#                             ],
#                             gap=3,
#                         ),
#                         id="content",
#                         className="p-3",
#                     ),
#                     width=10,
#                 ),
#             ],className="gx-0",
#             ),
#             width=12,
#             className="mx-auto"
#         ),
#     ],
#     id="page",
# )


@app.callback(

    Output(component_id='app-navbar-row-output', component_property='children'),
    [Input(component_id='app-location-id', component_property='pathname')]
    
)
def pathnameCallback(path):

    pathname_pill_pair = {'/Home': 'Home', 
                          '/Overview': 'Overview', 
                          '/Dashboard' : 'Dashboard', 
                          "/": 'Home',
                          }

    return_children = [
        dbc.Col([
            shop_navbar.navbar_named(pathname_pill_pair[path]),

        ], width=12)
        ]

    return return_children
    
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
register_age_callbacks(app)


    
@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run(debug=True)