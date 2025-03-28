from dash import html, dcc, Input, Output, State, callback, no_update, register_page
import dash_bootstrap_components as dbc

# from .Home_Page_Pills import pills_array

register_page(__name__, path='/Home',
              title="Online Shopping Trends & Consumer Behavior Analysis  - Home",
              description="Online Shopping Trends & Consumer Behavior.",
              image="HomePageMetaImage.png")

layout = html.Div([

    dbc.Container([

        dbc.Row(className='home-page-row-banner', children=[

            dbc.Col([

                dbc.Row([

                    dbc.Col([

                        html.Div(
                            
                            [html.H1('Welcome!', className='home-banner-title-text'),
                            html.P('An Analytics Dashboard for E-commerce Trends and Consumer Behaviors', style={'color': 'rgb(199, 199, 200)', 'fontWeight': 100})]
                            
                        , style={'display': 'inline-block'}, className='home-page-title-text-box')

                    ],lg=4, md=6, sm=12, xs=12, width=12, className='d-flex align-items-start justify-content-sm-center justify-content-md-start justify-content-center title-animate'),


                    dbc.Col([

                        html.Div([

                            html.H2('An Analytics App on E-commerce Trends and Consumer Behaviors', id='home-page-header', style={'color': '#E89C31'}),
                            html.Hr(className='my-2'),
                            html.Small('''Explore this Web app to find and compare the most common purchase frequency, compare consumer habits between age and gender, and summarize most purchase categories.
                                   You can also analyze and find correlations between age & gender for purchase frequency and purchase category.
                                   Observe correlation between browsing frequency & purchase frequency.
                                   Compare the dependence of customer reviews on purchase frequency. ''', className='mb-3', id='airports-graph-desc',
                                   style={'color': 'rgb(199, 199, 200)'}),


                    ], className='p-4 rounded-3 home-page-example-animate-box flex-fill', id='home-visual-div')

                    ],lg=6, md=6, sm=12, xs=12, width=8, className='d-flex align-items-start title-animate')


                ], style={'height': '100%'}, justify='around')

            ], width=12, className='home-banner-main-column')

        ]),

        dbc.Row([

            dbc.Col([

                html.A(html.Span([html.I(className='bi bi-info-square home-page-info-img')], className='mb-3'), href='/Overview'),
                html.H5('Overview'),
                html.Small('Explore the dataset and individual highlight features of the dataset!')

            ], width=12, xs=12, sm=6, md=3, lg=2, xl=2, xxl=2, className='home-page-info-col mt-3'),

            dbc.Col([

                html.A(html.Span([html.I(className='bi bi-easel2 home-page-info-img')], className='mb-3'), href='/Dashboard'),
                html.H5('Dashboard'),
                html.Small('Find trend by looking at all the dataset feature all at once!')

            ], width=12, xs=12, sm=6, md=3, lg=2, xl=2, xxl=2, className='home-page-info-col mt-3'),

        ], justify='evenly', className='my-4')

    ], fluid=True)

], style={'margin': 0})