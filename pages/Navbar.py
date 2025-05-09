from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly_express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def navbar_named(page_name):

    ## Adding in condition for Home Page Margin

    nav_class = ''

    if page_name == 'Home':

        nav_class = 'w-95vw'

    else: 

        nav_class = 'w-95vw h-5vh'

    named_navbar = page_name

    navbar = dbc.Navbar(
    dbc.Container([

        dbc.Row([

            dbc.Col(html.Span(html.I(className='bi bi-cart-fill', style={'fontSize': '2em', 'color': '#0732EF'})), style={'display':'inline-block'}),
            dbc.Col(html.Span([html.H5('Online Shopping Trends')],className='nav-header-span-class'))

        ], class_name='g-2', align='center'),

        dbc.Row([

           dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Home", href="/Home")),
                    dbc.NavItem(dbc.NavLink("Dashboard", href="/Dashboard")),
                    dbc.NavItem(dbc.NavLink("Submit", href="/Submit")),
                    dbc.NavItem(dbc.NavLink("Network", href="/Network")),
                ],
                navbar=True,
                style={"alignItems": "center"},
                horizontal="end",
                class_name="navbar-top",
            )

        ])

        

    ], class_name='m-0 mw-100', fluid=False), class_name=nav_class
)

    return navbar