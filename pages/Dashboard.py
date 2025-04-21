from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from layout.components.FigureCard import FigureCard
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
    "Other": "#dde663",
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
                dbc.Row([
                    dbc.Col([
                        html.Label("Display Mode"),
                        dbc.RadioItems(
                            id="overview-display-mode",
                            options=[
                                {"label": "% Total Purchases", "value": "percent"},
                                {"label": "Raw Count", "value": "count"},
                            ],
                            value="percent",
                            inline=True,
                        )
                    ], width="3"),
                    # Gender Filter
                    dbc.Col([
                        html.Label("Filter by Gender"),
                        dcc.Dropdown(
                            id="gender-filter-overview",
                            options=[{"label": g, "value": g} for g in df["gender"].unique()],
                            value=["Male", "Female", "Others"], 
                            multi=True,
                        ),
                    ], width=3),

                    # Age Category Filter
                    dbc.Col([
                        html.Label("Filter by Age Category"),
                        dcc.Dropdown(
                            id="age-cat-filter-overview",
                            options=[{"label": a, "value": a} for a in df["age_category"].cat.categories],
                            multi=True,
                        ),
                    ], width=3),

                    # Product Category Filter
                    dbc.Col([
                        html.Label("Filter by Product Category"),
                        dcc.Dropdown(
                            id="product-cat-filter-overview",
                            options=product_category_options,
                            multi=True,
                        ),
                    ], width=3),
                ], className="my-1", style={"font-size": "smaller"}, justify='center', align='center'),


                dbc.Row([
                    dbc.Col(FigureCard("Purchase Category Distribution",
                                       caption="Shows the overall purchase category share. It is computed by the count of events in each category divided by all purchases in the survey", 
                                       id="fig-overview"), width=6),
                    dbc.Col(FigureCard("Purchase Category by Gender (%)", 
                                       caption="Compare Genders view that shows four horizontal bar charts side-by-side that show what share each category represents of that gender’s total purchases",
                                       id="fig-compare"), width=6),
                ], className="gy-3"),

                dbc.Row([
                    dbc.Col(FigureCard("Purchase Category Grouped By Gender", 
                                       caption="Shows the same percentages as “Compare Genders” view but presented as a grouped bar chart instead of facets",
                                       id="fig-shares"), width=6),
                    dbc.Col(FigureCard("Gender Share (Pie)", 
                                       caption="Pie chart of the genders’ share of all purchases from the responses in the survey",
                                       id="fig-summary"), width=6),
                ], className="gy-3"),
            ]
        ),
        
        dbc.Tab(label="Demographics", tab_id="tab-demographics", children=[

            # Row 1: Age Category bar + Stacked Age/Gender bar
            dbc.Row([
                dbc.Col(FigureCard(
                    "Purchases by Age Category",
                    caption="Counts of purchases grouped by predefined age brackets, revealing which age groups contribute most to overall purchasing volume.",
                    id="age-cat-bar"), width=6),
                dbc.Col(FigureCard(
                    "Purchases by Age Category (Stacked by Gender)",
                    caption="Stacked bar chart showing how each gender contributes to purchases within each age group.",
                    id="gender-pie"), width=6),
            ], className="gy-3"),

            # Row 2: Age by Gender Box + Purchase Frequency by Gender
            dbc.Row([
                dbc.Col(FigureCard(
                    "Age by Gender",
                    caption="Box‑and‑whisker plots of customer ages split by gender, displaying medians, interquartile ranges, and outliers for direct comparison.",
                    id="age-box"), width=6),
                dbc.Col(FigureCard(
                    "Purchase Frequency by Gender",
                    caption="Grouped bar chart comparing how often each gender shops, illustrating behavioral differences across demographic segments.",
                    id="freq-gender-bar"), width=6),
            ], className="gy-3"),
        ]),

              
        dbc.Tab(
            label="Browse Vs Purchase",
            tab_id="tab-corr",
            children=[

                # Row 1: filters inside the tab
                dbc.Row([
                    dbc.Col([
                        html.Label("Filter by gender"),
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
                ], className="my-3",  justify='center', align='center'),

                # Row 2: the heatmap
                dbc.Row([
                    dbc.Col(
                        FigureCard(
                            "Browse Vs Purchase Correlation",
                            id="heatmap-behavior",
                            caption="Counts of users by browsing vs purchase frequency."
                        ),
                        width=6
                    ),
                ], className="gy-3", justify='center', align='center'),
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
            ], className="my-3"),

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
    Output({"type": "graph", "index": "age-cat-bar"},     "figure"),
    Output({"type": "graph", "index": "gender-pie"},      "figure"),
    Output({"type": "graph", "index": "age-box"},         "figure"),
    Output({"type": "graph", "index": "freq-gender-bar"}, "figure"),
    Input("dashboard-tabs", "active_tab"),
)
def update_demographics_tab(active_tab): 
    if active_tab != "tab-demographics":
        raise PreventUpdate

    # 1) Purchases by Age Category (unique customers)
    age_counts = (
        df.groupby("age_category")["id"]
          .nunique()
          .reset_index(name="purchase_count")
    )
    fig_age_cat_bar = px.bar(
        age_counts,
        x="age_category",
        y="purchase_count",
        template="plotly_white",
        height=240,
    )
    fig_age_cat_bar.update_layout(
        xaxis_title="Age Category",
        yaxis_title="Number of Unique Customers",
        margin=dict(l=40, r=20, t=20, b=120),
    )
    fig_age_cat_bar.update_traces(
        hovertemplate=
          "<b>Age Group</b>: %{x}<br>" +
          "<b>Customers</b>: %{y:,}<extra></extra>"
    )

    age_gender_counts = (
        df.groupby(["age_category", "gender"])["id"]
          .nunique()
          .reset_index(name="purchase_count")
    )

    fig_gender_age_stacked = px.bar(
        age_gender_counts,
        x="age_category",
        y="purchase_count",
        color="gender",
        barmode="stack",
        template="plotly_white",
        height=240,
    )
    fig_gender_age_stacked.update_layout(
        xaxis_title="Age Category",
        yaxis_title="Number of Unique Customers",
        legend_title="Gender",
        margin=dict(l=40, r=20, t=20, b=120),
    )
    fig_gender_age_stacked.update_traces(
        hovertemplate=(
            "<b>Age Group</b>: %{x}<br>"
            "<b>Gender</b>: %{legendgroup}<br>"
            "<b>Customers</b>: %{y:,}<extra></extra>"
        )
    )

    # 3) Age by gender (drop duplicate IDs)
    df_age = df.drop_duplicates(subset="id")[["gender", "age"]]
    fig_age_box = px.box(
        df_age,
        x="gender",
        y="age",
        template="plotly_white",
        height=240,
    )
    fig_age_box.update_layout(
        xaxis_title="gender",
        yaxis_title="Age",
        margin=dict(l=40, r=20, t=20, b=120),
    )
    fig_age_box.update_traces(
        hovertemplate=
          "<b>gender</b>: %{x}<br>" +
          "<b>Age</b>: %{y}<extra></extra>"
    )

    # 4) Purchase Frequency by gender (unique customers)
    freq_gender = (
    df.groupby(["gender", "purchase_frequency"])["id"]
      .nunique()
      .reset_index(name="count")
    )

    fig_freq_gender_bar = px.bar(
        freq_gender,
        x="purchase_frequency",
        y="count",
        color="gender",
        barmode="group",
        template="plotly_white",
        height=240,
        custom_data=["gender"]          
    )

    fig_freq_gender_bar.update_layout(
        xaxis_title="Purchase Frequency",
        yaxis_title="Number of Unique Customers",
        margin=dict(l=40, r=20, t=20, b=200),
        xaxis_tickangle=-45,
        legend_title="gender"
    )

    fig_freq_gender_bar.update_traces(
        hovertemplate=
        "<b>Purchase Frequency</b>: %{x}<br>" +
        "<b>Customers</b>: %{y:,}<br>" +
        "<b>gender</b>: %{customdata[0]}<extra></extra>"
    )

    return (
        fig_age_cat_bar,
        fig_gender_age_stacked,
        fig_age_box,
        fig_freq_gender_bar,
    )

    
    
@callback(
    Output({"type": "graph", "index": "heatmap-behavior"}, "figure"),
    Input("dashboard-tabs",        "active_tab"),
    Input("gender-filter-corr",    "value"),
    Input("age-cat-filter-corr",   "value"),
)
def update_correlation_heatmap(active_tab, genders, age_cats):
    if active_tab != "tab-corr":
        raise PreventUpdate

    dff = df.copy()
    if genders:
        dff = dff[dff["gender"].isin(genders)]
    if age_cats:
        dff = dff[dff["age_category"].isin(age_cats)]

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
        hovertemplate=
          "<b>Browsing</b>: %{y}<br>" +
          "<b>Purchase</b>: %{x}<br>" +
          "<b>Users</b>: %{z:,}<extra></extra>"
    )
    return fig

@callback(
    Output({"type": "graph", "index": "fig-overview"}, "figure"),
    Output({"type": "graph", "index": "fig-compare"}, "figure"),
    Output({"type": "graph", "index": "fig-shares"}, "figure"),
    Output({"type": "graph", "index": "fig-summary"}, "figure"),
    Input("gender-filter-overview", "value"),
    Input("age-cat-filter-overview", "value"),
    Input("product-cat-filter-overview", "value"),
    Input("overview-display-mode", "value"),  # new toggle input
    Input("dashboard-tabs", "active_tab"),
)
def update_consumer_overview_tab(gender_values, age_values, product_values, display_mode, active_tab):
    if active_tab != "tab-consumer-overview":
        raise PreventUpdate

    dff = df.copy()
    if gender_values:
        dff = dff[dff["gender"].isin(gender_values)]
    if age_values:
        dff = dff[dff["age_category"].isin(age_values)]
    if product_values:
        dff = dff[dff["purchase_categories"].isin(product_values)]

    # Aggregates
    overall_summary = (
        dff.groupby("purchase_categories")
        .agg(RawCount=('purchase_categories', 'size'), AvgAge=('age', 'mean'))
        .reset_index()
    )
    overall_summary['Pct of Purchases'] = (
        overall_summary['RawCount'] / overall_summary['RawCount'].sum() * 100
    )
    overall_summary['AvgAge'] = overall_summary['AvgAge'].round().astype('Int64')

    summary_df = (
        dff.groupby(['gender', 'purchase_categories'])
        .agg(RawCount=('purchase_categories', 'size'), AvgAge=('age', 'mean'))
        .reset_index()
    )
    summary_df['Pct of Purchases'] = (
        summary_df['RawCount'] / summary_df.groupby('gender')['RawCount'].transform('sum') * 100
    )
    summary_df['AvgAge'] = summary_df['AvgAge'].round().astype('Int64')

    gender_summary_df = (
        dff.groupby("gender")
        .agg(RawCount=('purchase_categories', 'size'), AvgAge=('age', 'mean'))
        .reset_index()
    )
    gender_summary_df['Pct of Purchases'] = (
        gender_summary_df['RawCount'] / gender_summary_df['RawCount'].sum() * 100
    )
    gender_summary_df['AvgAge'] = gender_summary_df['AvgAge'].round().astype('Int64')

    # Determine mode
    metric_col = "Pct of Purchases" if display_mode == "percent" else "RawCount"
    metric_label = "% of Total Purchases" if display_mode == "percent" else "Raw Count"
    x_tickformat = ".1f%" if display_mode == "percent" else None

    # --- Overview Chart
    fig_overview = px.bar(
        overall_summary,
        x=metric_col, y='purchase_categories', orientation='h',
        labels={'purchase_categories': 'Purchase Categories', metric_col: metric_label},
    )
    fig_overview.update_layout(xaxis_tickformat=x_tickformat)
    fig_overview.update_traces(
        customdata=overall_summary[['RawCount', 'Pct of Purchases', 'AvgAge']].values,
        hovertemplate="<b>%{y}</b><br>Count: %{customdata[0]}<br>Share: %{customdata[1]:.1f}%<br>Avg Age: %{customdata[2]}<extra></extra>"
    )

    # --- Compare Chart (facets)
    fig_compare = px.bar(
        summary_df,
        x=metric_col, y='purchase_categories', color='gender', facet_col='gender',
        color_discrete_map=gender_color, orientation='h',
        labels={'purchase_categories': 'Purchase Categories', metric_col: metric_label},
    )
    fig_compare.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig_compare.update_layout(legend_title_text="Gender", xaxis_tickformat=x_tickformat)
    for trace in fig_compare.data:
        gender = trace.name
        sub = summary_df[summary_df['gender'] == gender]
        trace.customdata = sub[['RawCount', 'Pct of Purchases', 'AvgAge']].values
        trace.hovertemplate = (
            f"<b>%{{y}}</b><br>Gender: {gender}<br>Count: %{{customdata[0]}}<br>Share: %{{customdata[1]:.1f}}%<br>Avg Age: %{{customdata[2]}}<extra></extra>"
        )

    # --- Grouped Bar
    fig_shares = px.bar(
        summary_df,
        x=metric_col, y='purchase_categories', color='gender', barmode='group',
        color_discrete_map=gender_color, orientation='h',
        labels={'purchase_categories': 'Purchase Categories', metric_col: metric_label},
    )

    fig_shares.update_layout(legend_title_text="Gender", xaxis_tickformat=x_tickformat)
    for trace in fig_shares.data:
        gender = trace.name
        sub = summary_df[summary_df['gender'] == gender]
        trace.customdata = sub[['RawCount', 'Pct of Purchases', 'AvgAge']].values
        trace.hovertemplate = (
            f"<b>Category:</b> %{{y}}<br>Gender: {gender}<br>Count: %{{customdata[0]}}<br>Share: %{{customdata[1]:.1f}}%<br>Avg Age: %{{customdata[2]}}<extra></extra>"
        )

    # --- Pie Chart (always shows percent)
    fig_summary = px.pie(
        gender_summary_df,
        values='Pct of Purchases', names='gender', color='gender',
        color_discrete_map=gender_color, hole=0.4
    )
    fig_summary.update_traces(
        textinfo='percent+label', textfont_size=18,
        hoverinfo='label+percent+value'
    )
    fig_summary.update_layout(legend_title_text="Gender")

    return fig_overview, fig_compare, fig_shares, fig_summary



@callback(
    Output({"type": "graph", "index": "imp-by-freq"},   "figure"),
    Output({"type": "graph", "index": "rel-by-freq"},   "figure"),
    Output({"type": "graph", "index": "imp-trend"},     "figure"),
    Output({"type": "graph", "index": "imp-vs-rel"},    "figure"),
    Input("dashboard-tabs",       "active_tab"),
    Input("gender-filter-rev",    "value"),
    Input("age-cat-filter-rev",   "value"),
)
def update_reviews_tab(active_tab, genders, age_cats):
    if active_tab != "tab-reviews":
        raise PreventUpdate

    df_rev = df.drop_duplicates("id")[[
        "id","gender","age_category","purchase_frequency",
        "customer_reviews_importance","review_reliability"
    ]].copy()

    df_rev["customer_reviews_importance"] = pd.to_numeric(
        df_rev["customer_reviews_importance"], errors="coerce"
    )

    if genders:
        df_rev = df_rev[df_rev["gender"].isin(genders)]
    if age_cats:
        df_rev = df_rev[df_rev["age_category"].isin(age_cats)]

    freq_order = [
      "Multiple times a week","Once a week",
      "Few times a month","Once a month",
      "Less than once a month",
    ]
    df_rev["purchase_frequency"] = pd.Categorical(
        df_rev["purchase_frequency"],
        categories=freq_order,
        ordered=True
    )

    # 1) Importance by Frequency (Box Plot)
    fig1 = px.box(
        df_rev, x="purchase_frequency",
        y="customer_reviews_importance",
        template="plotly_white", height=240
    )
    fig1.update_layout(
        title="Review Importance by Purchase Frequency",
        xaxis_title="Purchase Frequency",
        yaxis_title="Review Importance",
        margin=dict(l=40, r=20, t=40, b=120),
    )
    fig1.update_traces(
        hovertemplate="<b>%{x}</b><br>Importance: %{y:.2f}<extra></extra>"
    )

    # 2) Reliability by Frequency (Count Heatmap)
    rel_ct = pd.crosstab(
        df_rev["purchase_frequency"],
        df_rev["review_reliability"]
    )
    fig2 = px.imshow(
        rel_ct, text_auto=True, aspect="auto",
        template="plotly_white",
        color_continuous_scale="Viridis",
        height=240,
    )
    fig2.update_layout(
        title="Review Reliability Distribution by Purchase Frequency",
        xaxis_title="Review Reliability",
        yaxis_title="Purchase Frequency",
        margin=dict(l=40, r=20, t=40, b=120),
    )
    fig2.update_traces(
        hovertemplate=(
            "<b>Frequency</b>: %{y}<br>"
            "<b>Reliability</b>: %{x}<br>"
            "<b>Count</b>: %{z}<extra></extra>"
        )
    )

    # 3) Importance Distribution by Frequency (Bar Chart)
    imp_dist = (
        df_rev.groupby("purchase_frequency")["customer_reviews_importance"]
              .mean()
              .reset_index(name="avg_importance")
    )
    fig3 = px.bar(
        imp_dist,
        x="purchase_frequency",
        y="avg_importance",
        template="plotly_white",
        height=240,
    )
    fig3.update_layout(
        title="Average Review Importance by Purchase Frequency",
        xaxis_title="Purchase Frequency",
        yaxis_title="Average Importance",
        margin=dict(l=40, r=20, t=40, b=120),
    )
    fig3.update_traces(
        hovertemplate="<b>%{x}</b><br>Avg Importance: %{y:.2f}<extra></extra>"
    )

    # 4) Importance vs Reliability (Swarm-style Dot Scatter)
    fig4 = px.strip(
        df_rev,
        x="customer_reviews_importance",
        y="review_reliability",
        color="purchase_frequency",
        template="plotly_white",
        height=240,
    )
    fig4.update_layout(
        title="Importance vs Reliability Ratings by Purchase Frequency",
        xaxis_title="Review Importance",
        yaxis_title="Review Reliability",
        legend_title="Frequency",
        margin=dict(l=40, r=20, t=40, b=120),
    )
    fig4.update_traces(
        hovertemplate=(
            "<b>Importance</b>: %{x}<br>"
            "<b>Reliability</b>: %{y}<br>"
            "<b>Frequency</b>: %{legendgroup}<extra></extra>"
        )
    )


    return fig1, fig2, fig3, fig4
