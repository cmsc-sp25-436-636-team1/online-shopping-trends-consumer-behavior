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