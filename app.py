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
from pages import shop_navbar

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css','https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.css']
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
external_scripts=[
        'https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js'
    ]
server = Flask(__name__)

@server.route('/')
def index_redirect():
    return redirect('/Home')


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR, dbc_css, dbc.icons.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200",
        "https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap",
        'https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.css'],
        external_scripts=external_scripts,
        title="Online Shopping Trends & Consumer Behavior",
        use_pages=True, suppress_callback_exceptions=True, server=server)

app.layout = dbc.Container([
    dcc.Location(id='app-location-id'),
    html.Div([

        dbc.Row(id='app-navbar-row-output')

    ], style={'margin': '0'}),
    dash.page_container
], class_name='m-0 g-0 w-100', id='PlsFix', fluid=True)


server = app.server


@app.callback(

    Output(component_id='app-navbar-row-output', component_property='children'),
    [Input(component_id='app-location-id', component_property='pathname')]
    
)
def pathnameCallback(path):

    pathname_pill_pair = {'/Home': 'Home', 
                          '/Dashboard' : 'Dashboard', 
                          "/": 'Home',
                          "/Submit": 'Submit',
                          }

    return_children = [
        dbc.Col([
            shop_navbar.navbar_named(pathname_pill_pair[path]),

        ], width=12)
        ]

    return return_children
    
if __name__ == '__main__':
    app.run(debug=True)