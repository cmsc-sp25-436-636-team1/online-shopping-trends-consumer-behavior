# layout.py
from dash import html, register_page
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

register_page(
    __name__,
    path='/Home',
    title="Online Shopping Trends & Consumer Behavior",
    description="Dashboard home for Amazon consumer analysis"
)

def section(children, bg="light"):
    cls = {
        "light":  "section section-light",
        "accent": "section section-accent",
        "primary":"section section-primary"
    }[bg]
    return html.Div(children, className=cls)


layout = html.Div([

    # 1) Hero
    section([
        dbc.Container([
            dbc.Row(
                align="center", justify="center", className="g-4",
                children=[
                    # text
                    dbc.Col(
                        [
                            html.Div(
                                html.H1(
                                    "Behavioral Analysis of Amazon’s Consumers",
                                    className="section-title",
                                    style={"color":"#0732EF"}
                                ),
                                **{"data-aos":"fade-right"}
                            ),
                            html.Div(
                                html.P(
                                    "Understand consumer behavior, identify trends, optimize marketing strategies, "
                                    "and improve the overall customer experience on Amazon.",
                                    className="lead text-center",
                                    style={"color":"#0732EF"}
                                ),
                                **{"data-aos":"fade-up", "data-aos-delay":"200"}
                            ),
                        ],
                        width=12, md=6
                    ),
                    # image
                    dbc.Col(
                        html.Div(
                            html.Img(src="/assets/illus.png", className="img-fluid"),
                            **{"data-aos":"zoom-in", "data-aos-delay":"400"}
                        ),
                        width=12, md=6
                    ),
                ]
            )
        ])
    ], bg="light"),


    # 2) Dataset (three buttons under the paragraph)
    section([
    dbc.Container([
        dbc.Row(
            align="center", justify="center", className="g-4",
            children=[
                dbc.Col(
                    html.Div(
                        html.Img(src="/assets/illus2.png", className="img-fluid"),
                        **{"data-aos": "fade-right", "data-aos-delay": "200"}
                    ),
                    xs=12, md=6
                ),

                dbc.Col(
                    [
                        # Title
                        html.Div(
                            html.H2(
                                "About the Dataset",
                                className="section-title",
                                style={"color": "#0732EF"}
                            ),
                            **{"data-aos": "fade-up"}
                        ),

                        html.Div(
                            html.P(
                                "Collected via Google Forms, includes demographics, interaction data, and reviews.",
                                className="lead",
                                style={"color": "#0732EF"}
                            ),
                            **{"data-aos": "fade-up", "data-aos-delay": "200"}
                        ),

                        html.Div(
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Button("Table", color="secondary", className="w-100"),
                                        xs=12, sm=6, md=4
                                    ),
                                    dbc.Col(
                                        dbc.Button("23 Columns", color="secondary", className="w-100"),
                                        xs=12, sm=6, md=4
                                    ),
                                    dbc.Col(
                                        dbc.Button(id="record-count-button", color="secondary", className="w-100"),
                                        xs=12, sm=6, md=4
                                    ),
                                ],
                                className="g-3"
                            ),
                            **{"data-aos": "fade-up", "data-aos-delay": "400"}
                        ),
                    ],
                    xs=12, md=6
                ),
            ]
        )
    ])
], bg="accent"),


    # 3) Target & Action Pairs
    section([
        dbc.Container([

            html.Div(
                html.H2(
                    "Project Motivation",
                    className="section-title",
                    style={"color":"#fff"}
                ),
                **{"data-aos":"fade-up"}
            ),
            html.Div(
                html.P(
                    "Target & Action Pairs",
                    className="text-center",
                    style={"color":"#fff","fontWeight":"500"}
                ),
                **{"data-aos":"fade-up", "data-aos-delay":"200"}
            ),

            # steps
            *[
                html.Div(
                    dbc.Row(
                        [
                            dbc.Col(html.Div(step["num"], className="step-num"), xs=2, sm=1),
                            dbc.Col(html.Div(step["title"], className="step-title"), xs=4, sm=3),
                            dbc.Col(html.Div(step["desc"], className="step-desc"), xs=6, sm=8),
                        ],
                        className="py-3 process-row"
                    ),
                    **{"data-aos":"fade-up", "data-aos-delay":f"{300+i*100}"}
                )
                for i, step in enumerate([
                    {"num":"01","title":"Compare & Trends","desc":"The most common purchase frequency, compare consumer habits between age and gender, and summarize most purchase categories"},
                    {"num":"02","title":"Analyze & correlations","desc":"Between age & gender for purchase frequency and purchase category."},
                    {"num":"03","title":"Analyze & correlations","desc":"Dependence of customer reviews on purchase frequency"},
                    {"num":"04","title":"Compare & Dependency","desc":"Customer reviews on purchase frequency"}
                ])
            ]

        ]) 
    ], bg="primary"),


    # 4) Dashboard CTA section (center‑aligned)
    section([
        dbc.Container([

            # Title
            html.Div(
                html.H2(
                    "Dashboard",
                    className="section-title",
                    style={"color": "#0732EF"}
                ),
                className="text-center",
                **{"data-aos": "fade-up"}
            ),

            # Description
            html.Div(
                html.P(
                    "Dive into our interactive dashboard to explore key insights on Amazon consumer behavior— "
                    "from demographic breakdowns and browsing vs purchase patterns to category trend analyses.",
                    className="dashboard-desc"
                ),
                className="text-center",
                **{"data-aos": "fade-up", "data-aos-delay": "200"}
            ),

            # Illustration
            html.Div(
                html.Img(
                    src="/assets/illus3.png",
                    className="img-fluid",
                    style={"maxWidth": "300px"}
                ),
                className="text-center my-2",
                **{"data-aos": "zoom-in", "data-aos-delay": "600"}
            ),
            
             html.Div(
                dbc.Button(
                    "See Our Dashboard",
                    href="/Dashboard",
                    className="btn-dashboard",
                    color="secondary",
                    style={
                        "borderColor": "#0732EF",
                        "backgroundColor": "#faf9f5",
                        "color": "#0732EF"
                    }
                ),
                className="text-center mb-4",
                **{"data-aos": "fade-up", "data-aos-delay": "400"}
            ),

        ])
    ], bg="light"),


])

@callback(
    Output("record-count-button", "children"),
    Input("record-count-button", "id")  # triggers once on page load
)
def update_record_count(_):
    try:
        with SessionLocal() as session:
            count = session.execute(text("SELECT COUNT(*) FROM amz_customer_behavior")).scalar()
        return f"{count} Records"
    except Exception as e:
        return "Error fetching count"

