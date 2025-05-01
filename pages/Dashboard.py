from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from layout.components.FigureCard import FigureCard, BigFigureCard
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

category_order = ["Child", "Teenager", "Young Adult", "Adult", "Middle-aged Adult", "Older Adult"]
df["age_category"] = pd.Categorical(df["age_category"], categories=category_order, ordered=True)

gender_color = {
    "Female" : "#E976AA",
    "Male": "#1D76B5",
    "Others": "#dde663",
    "Prefer not to say": "#4F4F4F" 
}

product_category_options = [{"label": c, "value": c} for c in sorted(df["purchase_categories"].unique())]

layout = dbc.Container(fluid=True, style={"min-height": "93vh", "backgroundColor": "#faf9f5"}, children=[

    # ——— Tabs ———
    dbc.Tabs(id="dashboard-tabs", active_tab="tab-consumer-overview", className="mb-1 text-small", children=[

        dbc.Tab(
            label="Consumer Category Overview",
            tab_id="tab-consumer-overview",
            children=[
                dbc.Row(
                    [
                        # Display Mode (% vs Count)
                        dbc.Col(
                            [
                                html.Label("Display Mode"),
                                dbc.RadioItems(
                                    id="overview-display-mode",
                                    options=[
                                        {"label": "% Total Purchases", "value": "percent"},
                                        {"label": "Raw Count",         "value": "count"},
                                    ],
                                    value="percent",
                                    inline=True,
                                ),
                            ],
                            width=3,
                        ),

                        # Gender Filter
                        dbc.Col(
                            [
                                html.Label("Filter by Gender"),
                                dcc.Dropdown(
                                    id="gender-filter-overview",
                                    options=[
                                        {"label": g, "value": g}
                                        for g in df["gender"].unique()
                                    ],
                                    value=["Male", "Female", "Others"],
                                    multi=True,
                                ),
                            ],
                            width=3,
                        ),

                        # Age-Category Filter
                        dbc.Col(
                            [
                                html.Label("Filter by Age Category"),
                                dcc.Dropdown(
                                    id="age-cat-filter-overview",
                                    options=[
                                        {"label": a, "value": a}
                                        for a in df["age_category"].cat.categories
                                    ],
                                    multi=True,
                                ),
                            ],
                            width=3,
                        ),

                        # Product-Category Filter
                        dbc.Col(
                            [
                                html.Label("Filter by Product Category"),
                                dcc.Dropdown(
                                    id="product-cat-filter-overview",
                                    options=product_category_options,
                                    multi=True,
                                ),
                            ],
                            width=3,
                        ),
                    ],
                    className="my-1 text-small",
                    justify="center",
                    align="center",
                    style={"font-size": "smaller"},
                ),

                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                dbc.RadioItems(
                                    id="overview-chart-view",
                                    options=[
                                        {"label": "Overall",            "value": "overview"},
                                        {"label": "Facets",             "value": "compare"},
                                        {"label": "Group",              "value": "shares"},
                                    ],
                                    value="overview",
                                    inline=False,
                                    inputClassName="btn-check",
                                    labelClassName="btn btn-outline-primary",
                                    labelCheckedClassName="btn btn-primary",
                                    labelStyle={
                                        "width": "6rem",    
                                        "height": "2.5rem",   
                                        "padding": "0.5rem", 
                                        "whiteSpace": "nowrap",
                                    },
                                ),
                                className="btn-group-vertical",
                                role="group",
                            ),
                            width="auto",        
                        ),

                        dbc.Col(
                            FigureCard(
                                "Purchase Category Breakdown",
                                caption="Use the toggle on the left to switch views",
                                id="overview-main-chart",
                            ),
                            width=True,           
                        ),
                    ],
                    className="gy-3 align-items-center",
                ),

                dbc.Row(
                    [
                        dbc.Col(
                            FigureCard(
                                "Gender Share (Pie)",
                                caption="Percentage of purchases by gender.",
                                id="fig-summary",
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            FigureCard(
                                "Product Category Share (Pie)",
                                caption="Percentage of purchases by product category.",
                                id="fig-product-pie",
                            ),
                            width=6,
                        ),
                    ],
                    className="gy-3",
                ),
            ],
        ),
 
        dbc.Tab(
            label="Top Purchase Category",
            tab_id="tab-bubble-view",
            children=[
                dbc.Row([
                    dbc.Col([
                        html.Label("View Mode"),
                        dbc.RadioItems(
                            id="bubble-view-toggle",
                            options=[
                                {"label": "Combined View", "value": "combined"},
                                {"label": "Faceted View", "value": "facet"}
                            ],
                            value="combined",
                            inline=True,
                        ),
                    ], width=2),
                    dbc.Col([
                        html.Label("Filter by Gender"),
                        dcc.Dropdown(id="bubble-gender-filter", multi=True, options=[{"label": g, "value": g} for g in df["gender"].unique()],
                            value=["Male", "Female", "Others"], ),
                    ], width=3),

                    dbc.Col([
                        html.Label("Filter by Age Category"),
                        dcc.Dropdown(id="bubble-age-filter", multi=True),
                    ], width=3),

                    dbc.Col([
                        html.Label("Filter by Product Category"),
                        dcc.Dropdown(id="bubble-product-filter", multi=True),
                    ], width=4),

                    
                ], className="my-1", style={"font-size": "smaller"}, justify='center', align='center'),

                dbc.Row([
                    dbc.Col(BigFigureCard(
                        title="Purchase Category Bubble Chart",
                        caption="Bubble size shows frequency; color = gender; axis = age group vs frequency",
                        id="bubble-purchase-view",
                    ), width=12),
                ]),
            ]
        ),

        dbc.Tab(
            label="Demographics",
            tab_id="tab-demographics",
            children=[

                # — Filters + Mode Toggle —
                dbc.Row(
                    [
                         dbc.Col(
                            [
                                html.Label("Display Mode"),
                                dbc.RadioItems(
                                    id="demographics-mode",
                                    options=[
                                        {"label": "Normal",       "value": "normal"},
                                        {"label": "Distribution", "value": "distribution"},
                                    ],
                                    value="normal",
                                    inline=True,
                                ),
                            ],
                            width=4,
                        ),
                         
                        dbc.Col(
                            [
                                html.Label("Filter by Gender"),
                                dcc.Dropdown(
                                    id="gender-filter-demographics",
                                    options=[{"label": g, "value": g} for g in df["gender"].unique()],
                                    value=list(df["gender"].unique()),
                                    multi=True,
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.Label("Filter by Age Category"),
                                dcc.Dropdown(
                                    id="age-cat-filter-demographics",
                                    options=[{"label": a, "value": a} for a in df["age_category"].cat.categories],
                                    value=list(df["age_category"].cat.categories),
                                    multi=True,
                                ),
                            ],
                            width=4,
                        ),
                       
                    ],
                    className="my-1",
                    justify="start",
                    align="center",
                    style={"font-size": "smaller"},
                ),

                # — Age-Category & Age-by-Gender —
                dbc.Row(
                    [
                        dbc.Col(
                            FigureCard(
                                "Purchases by Age Category",
                                caption="Switch above between simple vs. stacked-by-gender.",
                                id="age-cat-chart",
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            FigureCard(
                                "Age by Gender",
                                caption="Box-and-whisker plots of customer ages by gender.",
                                id="age-box",
                            ),
                            width=6,
                        ),
                    ],
                    className="gy-3",
                ),

                # — Purchase & Browsing Frequency —
                dbc.Row(
                    [
                        dbc.Col(
                            FigureCard(
                                "Purchase Frequency",
                                caption="Shows how often customers shop (modeled on selected display mode).",
                                id="freq-gender-bar",
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            FigureCard(
                                "Browsing Frequency",
                                caption="Shows how often customers browse (modeled on selected display mode).",
                                id="browse-gender-bar",
                            ),
                            width=6,
                        ),
                    ],
                    className="gy-3",
                ),
            ],
        ),

        dbc.Tab(
            label="Browse Vs Purchase",
            tab_id="tab-corr",
            children=[
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
                        dbc.Col([
                            html.Label("Filter by Product Category"),
                            dcc.Dropdown(
                                id="product-cat-filter-corr",
                                options=product_category_options,
                                multi=True,
                            ),
                        ], width=4),
                    ],
                    className="my-3",
                    justify='start',
                    align='center',
                    style={"font-size": "smaller"}),
                    dbc.Row([
                        dbc.Col(
                            BigFigureCard(
                                "Browse Vs Purchase Correlation",
                                id="heatmap-behavior",
                                caption="Counts of users by browsing vs purchase frequency."
                            ),
                            width=6
                        ),
                    ],
                    className="gy-3",
                    justify='center',
                    align='center'),
                ],
            ),

        
        dbc.Tab(
        label="Reviews and Frequency",
        tab_id="tab-reviews",
        children=[

            # Row 1: Filters
            dbc.Row([
                dbc.Col([
                    html.Label("Filter by Gender"),
                    dcc.Dropdown(
                        id="gender-filter-rev",
                        options=[{"label": g, "value": g} for g in df["gender"].unique()],
                        multi=True,
                    ),
                ], width=4),
                dbc.Col([
                    html.Label("Filter by Age Category"),
                    dcc.Dropdown(
                        id="age-cat-filter-rev",
                        options=[{"label": a, "value": a}
                                for a in df["age_category"].cat.categories],
                        multi=True,
                    ),
                ], width=4),
            ], className="my-3", style={"font-size": "smaller"}),

            # Row 2: Box plot + heatmap
            dbc.Row([
                dbc.Col(FigureCard(
                    "Review Importance by Purchase Frequency",
                    id="imp-by-freq",
                    caption="Box plots showing how important customer reviews are across different purchase frequencies."
                ), width=6),
                dbc.Col(FigureCard(
                    "Review Reliability Distribution by Purchase Frequency",
                    id="rel-by-freq",
                    caption="A heatmap displaying how frequently users rely on reviews, split by how often they shop."
                ), width=6),
            ], className="gy-3"),

            # Row 3: Importance trend + scatter
            dbc.Row([
                dbc.Col(FigureCard(
                    "Average Review Importance by Purchase Frequency",
                    id="imp-trend",
                    caption="Bar chart showing the average importance assigned to reviews based on purchase frequency."
                ), width=6),
                dbc.Col(FigureCard(
                    "Importance vs Reliability Ratings by Purchase Frequency",
                    id="imp-vs-rel",
                    caption="A dot swarm plot visualizing how importance and reliability ratings vary across purchase habits."
                ), width=6),
            ], className="gy-3"),
        ]
    )

        
    ]),
])

@callback(
    Output({"type": "graph", "index": "age-cat-chart"},     "figure"),
    Output({"type": "graph", "index": "age-box"},           "figure"),
    Output({"type": "graph", "index": "freq-gender-bar"},   "figure"),
    Output({"type": "graph", "index": "browse-gender-bar"}, "figure"),
    Input("dashboard-tabs",                "active_tab"),
    Input("gender-filter-demographics",    "value"),
    Input("age-cat-filter-demographics",   "value"),
    Input("demographics-mode",             "value"),
)
def update_demographics_tab(active_tab, genders, age_cats, mode):
    if active_tab != "tab-demographics":
        raise PreventUpdate

    # 1) filter
    dff = df.copy()
    if genders:
        dff = dff[dff["gender"].isin(genders)]
    if age_cats:
        dff = dff[dff["age_category"].isin(age_cats)]

    # 2) Age-Category chart
    if mode == "normal":
        age_counts = (
            dff.groupby("age_category")["id"]
               .nunique()
               .reset_index(name="count")
        )
        fig_age_cat = px.bar(
            age_counts,
            x="age_category",
            y="count",
            template="plotly_white",
            height=300,
        )
        fig_age_cat.update_layout(
            xaxis_title="Age Category",
            yaxis_title="Unique Customers",
            margin=dict(l=40, r=20, t=20, b=60),
        )
        fig_age_cat.update_traces(
            hovertemplate="<b>Age Group</b>: %{x}<br><b>Customers</b>: %{y:,}<extra></extra>"
        )
    else:  # distribution
        age_gender = (
            dff.groupby(["age_category", "gender"])["id"]
               .nunique()
               .reset_index(name="count")
        )
        fig_age_cat = px.bar(
            age_gender,
            x="age_category",
            y="count",
            color="gender",
            barmode="stack",
            template="plotly_white",
            height=300,
            color_discrete_map=gender_color,
        )
        fig_age_cat.update_layout(
            xaxis_title="Age Category",
            yaxis_title="Unique Customers",
            legend_title="Gender",
            margin=dict(l=40, r=20, t=20, b=60),
        )
        fig_age_cat.update_traces(
            hovertemplate=(
                "<b>Age Group</b>: %{x}<br>"
                "<b>Gender</b>: %{legendgroup}<br>"
                "<b>Customers</b>: %{y:,}<extra></extra>"
            )
        )

    # 3) Age by Gender (always the same)
    df_age = dff.drop_duplicates(subset="id")[["gender", "age"]]
    fig_age_box = px.box(
        df_age,
        x="gender",
        y="age",
        template="plotly_white",
        height=300,
    )
    fig_age_box.update_layout(
        xaxis_title="Gender",
        yaxis_title="Age",
        margin=dict(l=40, r=20, t=20, b=60),
    )
    fig_age_box.update_traces(
        hovertemplate="<b>Gender</b>: %{x}<br><b>Age</b>: %{y}<extra></extra>"
    )

    # 4) Purchase Frequency
    if mode == "normal":
        freq_total = (
            dff.groupby("purchase_frequency")["id"]
               .nunique()
               .reset_index(name="count")
        )
        fig_freq = px.bar(
            freq_total,
            x="purchase_frequency",
            y="count",
            template="plotly_white",
            height=300,
            category_orders={"purchase_frequency": [
                "Less than once a month",
                "Once a month",
                "Few times a month",
                "Once a week",
                "Multiple times a week",
            ]},
        )
        fig_freq.update_layout(
            xaxis_title="Purchase Frequency",
            yaxis_title="Unique Customers",
            xaxis_tickangle=-45,
            margin=dict(l=40, r=20, t=20, b=60),
            showlegend=False,
        )
        fig_freq.update_traces(
            hovertemplate="<b>Purchase Frequency</b>: %{x}<br><b>Customers</b>: %{y:,}<extra></extra>"
        )
    else:
        freq_gender = (
            dff.groupby(["gender", "purchase_frequency"])["id"]
               .nunique()
               .reset_index(name="count")
        )
        fig_freq = px.bar(
            freq_gender,
            x="purchase_frequency",
            y="count",
            color="gender",
            barmode="group",
            template="plotly_white",
            height=300,
            color_discrete_map=gender_color,
            category_orders={"purchase_frequency": [
                "Less than once a month",
                "Once a month",
                "Few times a month",
                "Once a week",
                "Multiple times a week",
            ]},
        )
        fig_freq.update_layout(
            xaxis_title="Purchase Frequency",
            yaxis_title="Unique Customers",
            xaxis_tickangle=-45,
            legend_title="Gender",
            margin=dict(l=40, r=20, t=20, b=60),
        )
        fig_freq.update_traces(
            customdata=freq_gender[["gender"]].values,
            hovertemplate=(
                "<b>Purchase Frequency</b>: %{x}<br>"
                "<b>Customers</b>: %{y:,}<br>"
                "<b>Gender</b>: %{customdata[0]}<extra></extra>"
            )
        )

    # 5) Browsing Frequency
    if mode == "normal":
        browse_total = (
            dff.groupby("browsing_frequency")["id"]
               .nunique()
               .reset_index(name="count")
        )
        fig_browse = px.bar(
            browse_total,
            x="browsing_frequency",
            y="count",
            template="plotly_white",
            height=300,
            category_orders={"browsing_frequency": [
                "Less than once a month",
                "Once a month",
                "Few times a month",
                "Once a week",
                "Multiple times a week",
            ]},
        )
        fig_browse.update_layout(
            xaxis_title="Browsing Frequency",
            yaxis_title="Unique Customers",
            xaxis_tickangle=-45,
            margin=dict(l=40, r=20, t=20, b=60),
            showlegend=False,
        )
        fig_browse.update_traces(
            hovertemplate="<b>Browsing Frequency</b>: %{x}<br><b>Customers</b>: %{y:,}<extra></extra>"
        )
    else:
        browse_gender = (
            dff.groupby(["gender", "browsing_frequency"])["id"]
               .nunique()
               .reset_index(name="count")
        )
        fig_browse = px.bar(
            browse_gender,
            x="browsing_frequency",
            y="count",
            color="gender",
            barmode="group",
            template="plotly_white",
            height=300,
            color_discrete_map=gender_color,
            category_orders={"browsing_frequency": [
                "Less than once a month",
                "Once a month",
                "Few times a month",
                "Once a week",
                "Multiple times a week",
            ]},
        )
        fig_browse.update_layout(
            xaxis_title="Browsing Frequency",
            yaxis_title="Unique Customers",
            xaxis_tickangle=-45,
            legend_title="Gender",
            margin=dict(l=40, r=20, t=20, b=60),
        )
        fig_browse.update_traces(
            customdata=browse_gender[["gender"]].values,
            hovertemplate=(
                "<b>Browsing Frequency</b>: %{x}<br>"
                "<b>Customers</b>: %{y:,}<br>"
                "<b>Gender</b>: %{customdata[0]}<extra></extra>"
            )
        )

    return fig_age_cat, fig_age_box, fig_freq, fig_browse

@callback(
    Output({"type": "graph", "index": "heatmap-behavior"}, "figure"),
    Input("dashboard-tabs",             "active_tab"),
    Input("gender-filter-corr",         "value"),
    Input("age-cat-filter-corr",        "value"),
    Input("product-cat-filter-corr",    "value"),   # new input
)
def update_correlation_heatmap(active_tab, genders, age_cats, product_values):
    if active_tab != "tab-corr":
        raise PreventUpdate

    dff = df.copy()
    if genders:
        dff = dff[dff["gender"].isin(genders)]
    if age_cats:
        dff = dff[dff["age_category"].isin(age_cats)]
    if product_values:
        # df was exploded on purchase_categories, so this filters correctly
        dff = dff[dff["purchase_categories"].isin(product_values)]

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
        hovertemplate=(
          "<b>Browsing</b>: %{y}<br>"
          "<b>Purchase</b>: %{x}<br>"
          "<b>Users</b>: %{z:,}<extra></extra>"
        )
    )
    return fig

@callback(
    Output({"type": "graph",     "index": "overview-main-chart"}, "figure"),
    Output({"type": "fig-title", "index": "overview-main-chart"}, "children"),
    Output({"type": "fig-caption", "index": "overview-main-chart"}, "children"),
    Output({"type": "graph", "index": "fig-summary"},     "figure"),
    Output({"type": "graph", "index": "fig-product-pie"}, "figure"),
    Input("gender-filter-overview",     "value"),
    Input("age-cat-filter-overview",    "value"),
    Input("product-cat-filter-overview","value"),
    Input("overview-display-mode",      "value"),
    Input("overview-chart-view",        "value"),
    Input("dashboard-tabs",             "active_tab"),
)
def update_consumer_overview_tab(genders, ages, products, display_mode, view, active_tab):
    if active_tab != "tab-consumer-overview":
        raise PreventUpdate

    # 1) filter
    dff = df.copy()
    if genders:
        dff = dff[dff["gender"].isin(genders)]
    if ages:
        dff = dff[dff["age_category"].isin(ages)]
    if products:
        dff = dff[dff["purchase_categories"].isin(products)]

    # 2) prepare aggregates
    # — overall per category —
    overall = (
        dff.groupby("purchase_categories")
           .agg(RawCount=('purchase_categories','size'),
                AvgAge=('age','mean'))
           .reset_index()
    )
    overall["Pct of Purchases"] = overall["RawCount"] / overall["RawCount"].sum() * 100
    overall["AvgAge"] = overall["AvgAge"].round().astype("Int64")

    # — per-gender facets & grouped —
    summary = (
        dff.groupby(["gender","purchase_categories"])
           .agg(RawCount=('purchase_categories','size'),
                AvgAge=('age','mean'))
           .reset_index()
    )
    summary["Pct of Purchases"] = (
        summary["RawCount"]
        / summary.groupby("gender")["RawCount"].transform("sum")
        * 100
    )
    summary["AvgAge"] = summary["AvgAge"].round().astype("Int64")

    # — gender totals for pie —
    gender_totals = (
        dff.groupby("gender")
           .agg(RawCount=('purchase_categories','size'))
           .reset_index()
    )
    gender_totals["Pct of Purchases"] = (
        gender_totals["RawCount"] / gender_totals["RawCount"].sum() * 100
    )

    # — product-category pie —
    prod_totals = (
        dff.groupby("purchase_categories")
           .agg(RawCount=('purchase_categories','size'))
           .reset_index()
    )
    prod_totals["Pct of Purchases"] = (
        prod_totals["RawCount"] / prod_totals["RawCount"].sum() * 100
    )

    # 3) (Re)build the three “overview” variants
    metric = "Pct of Purchases" if display_mode=="percent" else "RawCount"
    label  = "% of Total Purchases" if display_mode=="percent" else "Raw Count"
    fmt    = ".1f%" if display_mode=="percent" else None

    # --- 1) Overall distribution ---
    fig_overall = px.bar(
        overall,
        x=metric, y="purchase_categories",
        orientation="h",
        labels={"purchase_categories":"Purchase Category", metric:label},
    )
    fig_overall.update_layout(xaxis_tickformat=fmt)
    fig_overall.update_traces(
        customdata=overall[["RawCount","Pct of Purchases","AvgAge"]].values,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Count: %{customdata[0]}<br>"
            "Share: %{customdata[1]:.1f}%<br>"
            "Avg Age: %{customdata[2]}<extra></extra>"
        )
    )

    # --- 2) Faceted by gender ---
    fig_compare = px.bar(
        summary,
        x=metric, y="purchase_categories",
        color="gender", facet_col="gender",
        orientation="h",
        color_discrete_map=gender_color,
        labels={"purchase_categories":"Purchase Category", metric:label},
    )
    fig_compare.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig_compare.update_layout(legend_title_text="Gender", xaxis_tickformat=fmt)
    for trace in fig_compare.data:
        g = trace.name
        sub = summary[summary["gender"]==g]
        trace.customdata   = sub[["RawCount","Pct of Purchases","AvgAge"]].values
        trace.hovertemplate=(
            f"<b>%{{y}}</b><br>"
            f"Gender: {g}<br>"
            "Count: %{customdata[0]}<br>"
            "Share: %{customdata[1]:.1f}%<br>"
            "Avg Age: %{customdata[2]}<extra></extra>"
        )

    # --- 3) Grouped by gender ---
    fig_shares = px.bar(
        summary,
        x=metric, y="purchase_categories",
        color="gender", barmode="group",
        color_discrete_map=gender_color,
        orientation="h",
        labels={"purchase_categories":"Purchase Category", metric:label},
    )
    fig_shares.update_layout(legend_title_text="Gender", xaxis_tickformat=fmt)
    for trace in fig_shares.data:
        g = trace.name
        sub = summary[summary["gender"]==g]
        trace.customdata    = sub[["RawCount","Pct of Purchases","AvgAge"]].values
        trace.hovertemplate = (
            f"<b>%{{y}}</b><br>"
            f"Gender: {g}<br>"
            "Count: %{customdata[0]}<br>"
            "Share: %{customdata[1]:.1f}%<br>"
            "Avg Age: %{customdata[2]}<extra></extra>"
        )

    # pick the one to show
    main_map = {
        "overview": fig_overall,
        "compare":  fig_compare,
        "shares":   fig_shares,
    }
    fig_main = main_map[view]
    
    title_map = {
        "overview": "Purchase Category Distribution Summary",
        "compare":  "Purchase Category Facecet Breakdown by Gender",
        "shares":   "Purchase Category Grouped By Gender",
    }
    caption_map = {
        "overview": "Shows the overall purchase category share. It is computed by the count of events in each category divided by all purchases in the survey",
        "compare":  "Compare Genders view that shows horizontal bar charts side-by-side that show what share each category represents of that gender’s total purchases",
        "shares":   "Shows the same percentages as “Compare Genders” view but presented as a grouped bar chart instead of facets",
    }
    title   = title_map[view]
    caption = caption_map[view]

    # 4) Gender‐share pie
    fig_gender_pie = px.pie(
        gender_totals,
        values="Pct of Purchases",
        names="gender",
        color="gender",
        hole=0.4,
        color_discrete_map=gender_color,
    )
    fig_gender_pie.update_traces(textinfo="percent+label", textfont_size=16)

    # 5) Product‐category pie
    fig_prod_pie = px.pie(
        prod_totals,
        values="Pct of Purchases",
        names="purchase_categories",
        hole=0.4,
        template="plotly_white",
    )
    fig_prod_pie.update_layout(
        legend_title="Product Category",
    )
    fig_prod_pie.update_traces(textinfo="percent+label", textfont_size=14)

    return fig_main, title, caption, fig_gender_pie, fig_prod_pie


@callback(
    Output({"type": "graph", "index": "bubble-purchase-view"}, "figure"),
    Output({"type": "fig-title", "index": "bubble-purchase-view"}, "children"),
    Output({"type": "fig-caption", "index": "bubble-purchase-view"}, "children"),
    Output("bubble-gender-filter", "options"),
    Output("bubble-age-filter", "options"),
    Output("bubble-product-filter", "options"),
    Input("bubble-gender-filter", "value"),
    Input("bubble-age-filter", "value"),
    Input("bubble-product-filter", "value"),
    Input("bubble-view-toggle", "value"),
    Input("dashboard-tabs", "active_tab"),
)
def update_bubble_chart(genders, ages, products, view_mode, active_tab):
    if active_tab != "tab-bubble-view":
        raise PreventUpdate

    df_copy = df.copy()
    df_copy["purch_cat_list"] = df_copy["purchase_categories"].astype(str).str.split(";")
    df_sep_cat = df_copy.explode("purch_cat_list")
    df_sep_cat["purch_cat_list"] = df_sep_cat["purch_cat_list"].str.strip()

    gender_options = [{"label": g, "value": g} for g in sorted(df_sep_cat["gender"].dropna().unique())]
    age_order = list(df["age_category"].cat.categories)
    age_options = [{"label": a, "value": a} for a in age_order if a in df_sep_cat["age_category"].unique()]
    product_options = [{"label": p, "value": p} for p in sorted(df_sep_cat["purch_cat_list"].dropna().unique())]

    if genders:
        df_sep_cat = df_sep_cat[df_sep_cat["gender"].isin(genders)]
    if ages:
        df_sep_cat = df_sep_cat[df_sep_cat["age_category"].isin(ages)]
    if products:
        df_sep_cat = df_sep_cat[df_sep_cat["purch_cat_list"].isin(products)]

    x_axis = ["Less than once a month", "Once a month", "Few times a month", "Once a week", "Multiple times a week"]

    df_with_counts = (
        df_sep_cat.groupby(["age_category", "purchase_frequency", "gender", "purch_cat_list"], observed=True)
        .size().reset_index(name="count")
    )

    df_with_counts["purchase_frequency"] = pd.Categorical(df_with_counts["purchase_frequency"], categories=x_axis, ordered=True)
    df_with_counts["age_category"] = pd.Categorical(df_with_counts["age_category"], categories=age_order, ordered=True)

    df_with_counts["xspacing"] = df_with_counts["purchase_frequency"].cat.codes + np.random.uniform(-0.1, 0.1, len(df_with_counts))
    df_with_counts["yspacing"] = df_with_counts["age_category"].cat.codes + np.random.uniform(-0.3, 0.3, len(df_with_counts))

    df_with_counts["hover_text"] = df_with_counts.apply(
        lambda row: f'{row["count"]} {row["gender"]}s in {row["age_category"]} group<br>'
                    f'buy {row["purch_cat_list"]} {row["purchase_frequency"]}', axis=1
    )

    common_args = dict(
        x="xspacing",
        y="yspacing",
        size="count",
        size_max=40,
        color="gender",
        color_discrete_map=gender_color,
        hover_name="hover_text",
        hover_data={"count": False, "purch_cat_list": False, "gender": False, "xspacing": False, "yspacing": False},
        height=600,
    )

    if view_mode == "facet":
        fig = px.scatter(df_with_counts, facet_col="purch_cat_list", facet_col_spacing=0.08,
                         facet_row_spacing=0.1, facet_col_wrap=3, **common_args)
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig.for_each_xaxis(
            lambda x: x.update(
                tickmode="array",
                tickvals=list(range(len(x_axis))),
                ticktext=x_axis,
                tickfont=dict(size=8),
                title=dict(text="Purchase Frequency", font=dict(size=10)),
                showticklabels=True,
                matches=None
            )
        )

        fig.for_each_yaxis(
            lambda y: y.update(
                tickmode='array',
                tickvals=list(range(len(age_order))),
                ticktext=age_order,
                tickfont=dict(size=8),
                title=dict(text='Age Category', font=dict(size=10)),
                showticklabels=True,
                matches=None
            )
        )
        title = "Faceted View of Top Purchase Categories"
        caption = "A faceted view of purchase categories to compare trends of purchase frequency and age group against gender with the area of the bubble related to the number of matches for those three variables."

    else:
        fig = px.scatter(df_with_counts, **common_args)
        fig.update_layout(
            xaxis=dict(tickmode="array", tickvals=list(range(len(x_axis))), ticktext=x_axis, title="Purchase Frequency"),
            yaxis=dict(tickmode="array", tickvals=list(range(len(age_order))), ticktext=age_order, title="Age Category")
        )
        title = "Combined View of Top Purchase Categories"
        caption = "A single view to compare trends of purchase frequency and age group against gender and purchase category with the area of the bubble related to the number of matches for those four variables."

    fig.update_layout(
        legend_title_text="Gender",
        margin=dict(l=40, r=20, t=40, b=60),
    )

    return fig, title, caption, gender_options, age_options, product_options

from dash import Input, Output, callback
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import numpy as np

@callback(
    Output({"type": "graph", "index": "imp-by-freq"},  "figure"),
    Output({"type": "graph", "index": "rel-by-freq"},  "figure"),
    Output({"type": "graph", "index": "imp-trend"},    "figure"),
    Output({"type": "graph", "index": "imp-vs-rel"},   "figure"),
    Input("dashboard-tabs",         "active_tab"),
    Input("gender-filter-rev",      "value"),
    Input("age-cat-filter-rev",     "value"),
)
def update_reviews_tab(active_tab, genders, age_cats):
    if active_tab != "tab-reviews":
        raise PreventUpdate

    # 1) apply filters
    dff = df.copy()
    if genders:
        dff = dff[dff["gender"].isin(genders)]
    if age_cats:
        dff = dff[dff["age_category"].isin(age_cats)]

    # 2) enforce purchase-frequency order
    FREQ_ORDER = [
        "Less than once a month",
        "Once a month",
        "Few times a month",
        "Once a week",
        "Multiple times a week",
    ]
    dff["purchase_frequency"] = pd.Categorical(
        dff["purchase_frequency"], categories=FREQ_ORDER, ordered=True
    )

    # a) Review Importance by Purchase Frequency (box)
    fig_imp_by_freq = px.box(
        dff,
        x="purchase_frequency",
        y="customer_reviews_importance",
        template="plotly_white",
        height=300,
    )
    fig_imp_by_freq.update_layout(
        xaxis_title="Purchase Frequency",
        yaxis_title="Review Importance",
        margin=dict(l=40, r=20, t=20, b=80),
    )
    fig_imp_by_freq.update_traces(
        hovertemplate="<b>Freq</b>: %{x}<br><b>Importance</b>: %{y}<extra></extra>"
    )

    # b) Review Reliability Distribution by Purchase Frequency (heatmap)
    rel_levels = sorted(dff["review_reliability"].dropna().unique())
    heat_rel = pd.crosstab(
        index=dff["purchase_frequency"],
        columns=dff["review_reliability"],
    ).reindex(index=FREQ_ORDER, columns=rel_levels, fill_value=0)

    fig_rel_by_freq = px.imshow(
        heat_rel,
        text_auto=True,
        aspect="auto",
        template="plotly_white",
        color_continuous_scale="Viridis",
        height=300,
    )
    fig_rel_by_freq.update_layout(
        xaxis_title="Review Reliability",
        yaxis_title="Purchase Frequency",
        margin=dict(l=40, r=20, t=20, b=80),
    )
    fig_rel_by_freq.update_xaxes(categoryorder="array", categoryarray=rel_levels)
    fig_rel_by_freq.update_yaxes(categoryorder="array", categoryarray=FREQ_ORDER)
    fig_rel_by_freq.update_traces(
        hovertemplate="<b>Freq</b>: %{y}<br><b>Reliability</b>: %{x}<br><b>Count</b>: %{z}<extra></extra>"
    )

    # c) Average Review Importance by Purchase Frequency (bar)
    avg_imp = (
        dff.groupby("purchase_frequency")["customer_reviews_importance"]
           .mean()
           .reset_index(name="avg_importance")
    )
    fig_imp_trend = px.bar(
        avg_imp,
        x="purchase_frequency",
        y="avg_importance",
        template="plotly_white",
        height=300,
    )
    fig_imp_trend.update_layout(
        xaxis_title="Purchase Frequency",
        yaxis_title="Average Importance",
        margin=dict(l=40, r=20, t=20, b=80),
    )
    fig_imp_trend.update_traces(
        hovertemplate="<b>Freq</b>: %{x}<br><b>Avg Importance</b>: %{y:.2f}<extra></extra>"
    )

    # d) Importance vs Reliability Ratings — jittered scatter
    df_scatter = dff.copy()
    # jitter x around the categorical code
    df_scatter["xf"] = (
        df_scatter["purchase_frequency"].cat.codes.astype(float)
        + np.random.uniform(-0.2, 0.2, len(df_scatter))
    )
    # jitter y around the importance scale 1–5
    df_scatter["yf"] = (
        df_scatter["customer_reviews_importance"].astype(float) - 1
        + np.random.uniform(-0.1, 0.1, len(df_scatter))
    )

    fig_imp_vs_rel = px.scatter(
        df_scatter,
        x="xf",
        y="yf",
        color="review_reliability",
        template="plotly_white",
        height=300,
        hover_data=["purchase_frequency", "customer_reviews_importance", "review_reliability"],
        color_discrete_map=None,  # or your custom map
    )
    # restore original tick labels
    fig_imp_vs_rel.update_xaxes(
        tickmode="array",
        tickvals=list(range(len(FREQ_ORDER))),
        ticktext=FREQ_ORDER,
        title_text="Purchase Frequency",
    )
    fig_imp_vs_rel.update_yaxes(
        tickmode="array",
        tickvals=[0, 1, 2, 3, 4],
        ticktext=[1, 2, 3, 4, 5],
        title_text="Review Importance",
    )
    fig_imp_vs_rel.update_traces(marker=dict(size=6, opacity=0.6))

    return fig_imp_by_freq, fig_rel_by_freq, fig_imp_trend, fig_imp_vs_rel
