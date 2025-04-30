from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import os
import plotly.graph_objects as go
import networkx as nx
from collections import Counter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from layout.components.FigureCard import BigFigureCard
import dash

# 1) Register page at /Network
dash.register_page(
    __name__,
    path="/Network",
    title="Behavior Network",
    description="Animated, dynamic-layout buildup of co-occurrence graph with controls and legend"
)

# 2) Load full dataset
load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)
with SessionLocal() as session:
    df = pd.read_sql("SELECT * FROM amz_customer_behavior", con=session.bind)

# 3) Extract helper
def extract(row):
    attrs = []
    if row.purchase_frequency:    attrs.append(f"Purchase: {row.purchase_frequency}")
    if row.browsing_frequency:    attrs.append(f"Browse: {row.browsing_frequency}")
    if row.gender:               attrs.append(f"Gender: {row.gender}")
    # return sorted pairs
    return [tuple(sorted((attrs[i], attrs[j])))
            for i in range(len(attrs)) for j in range(i+1, len(attrs))]

records = [extract(r) for _, r in df.iterrows()]

# 4) Build frames
cum_pairs = Counter()
frames = []

# blank frame
frames.append(go.Frame(name="0", data=[
    dict(x=[], y=[], hovertext=[]),
    dict(x=[], y=[], text=[], hovertext=[], marker=dict(size=[], color=[])),
    dict(x=[], y=[], hovertext=[], hovertemplate="%{hovertext}<extra></extra>",
         mode="markers", marker=dict(size=10, color="rgba(0,0,0,0)"), showlegend=False)
]))

for idx, pairs in enumerate(records, start=1):
    cum_pairs.update(pairs)
    G_i = nx.Graph()
    for (u, v), w in cum_pairs.items():
        if w > 0:
            G_i.add_edge(u, v, weight=w)

    pos_i = nx.spring_layout(G_i, weight="weight", k=0.5, iterations=20)

    # optional zoom bounds
    xs = [x for x, y in pos_i.values()]; ys = [y for x, y in pos_i.values()]
    xmin, xmax = min(xs)-1, max(xs)+1
    ymin, ymax = min(ys)-1, max(ys)+1

    # build edge coords + hovertext
    edge_x, edge_y, edge_hover = [], [], []
    mid_x, mid_y, mid_hover = [], [], []
    for u, v in G_i.edges():
        x0, y0 = pos_i[u]; x1, y1 = pos_i[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        key = tuple(sorted((u, v)))
        count = cum_pairs.get(key, 0)
        txt = f"{u} ↔ {v}  |  co-occurrences: {count}"
        edge_hover.append(txt)
        # midpoint
        mid_x.append((x0 + x1)/2)
        mid_y.append((y0 + y1)/2)
        mid_hover.append(txt)

    # build node coords + hover + size/color
    score = Counter()
    for (u, v), w in cum_pairs.items():
        score[u] += w; score[v] += w
    max_s = max(score.values()) or 1

    node_x, node_y, node_text, node_hover, node_sizes, node_colors = [], [], [], [], [], []
    for node in G_i.nodes():
        node_x.append(pos_i[node][0]); node_y.append(pos_i[node][1])
        node_text.append(node)
        node_hover.append(f"{node}  |  occurrences: {score[node]}")
        node_sizes.append(10 + (score[node]/max_s)*40)
        node_colors.append(
            "#1f77b4" if node.startswith("Purchase") else
            "#ff7f0e" if node.startswith("Browse") else
            "#2ca02c"
        )

    frames.append(go.Frame(name=str(idx), data=[
        dict(x=edge_x, y=edge_y, hovertext=edge_hover),
        dict(x=node_x, y=node_y, text=node_text, hovertext=node_hover,
             marker=dict(size=node_sizes, color=node_colors)),
        dict(x=mid_x, y=mid_y, hovertext=mid_hover,
             hovertemplate="%{hovertext}<extra></extra>",
             mode="markers", marker=dict(size=10, color="rgba(0,0,0,0)"), showlegend=False)
    ]))

# 5) Base traces
edge_trace = go.Scatter(
    x=[], y=[], mode="lines",
    line=dict(width=2, color="#888"),
    hoverinfo="text", hovertext=[], hovertemplate="%{hovertext}<extra></extra>",
    showlegend=False
)
node_trace = go.Scatter(
    x=[], y=[], mode="markers+text",
    text=[], textposition="top center",
    hovertext=[], hovertemplate="%{hovertext}<extra></extra>",
    marker=dict(size=[], color=[], line=dict(width=1, color="#333")),
    showlegend=False
)
midpoint_trace = go.Scatter(
    x=[], y=[], mode="markers",
    marker=dict(size=10, color="rgba(0,0,0,0)"),
    hovertext=[], hovertemplate="%{hovertext}<extra></extra>",
    showlegend=False
)

# 6) Legend traces
legend_traces = [
    go.Scatter(x=[None], y=[None], mode="markers",
               marker=dict(size=12, color="#1f77b4"), name="Purchase"),
    go.Scatter(x=[None], y=[None], mode="markers",
               marker=dict(size=12, color="#ff7f0e"), name="Browse"),
    go.Scatter(x=[None], y=[None], mode="markers",
               marker=dict(size=12, color="#2ca02c"), name="Gender")
]

# 7) Assemble figure
fig = go.Figure(
    data=[edge_trace, node_trace, midpoint_trace] + legend_traces,
    frames=frames
)
fig.update_layout(
    # title="Dynamic spring-layout: adding one record at a time",
    margin=dict(l=20, r=20, t=50, b=80),
    xaxis=dict(visible=False, autorange=False, range=[xmin, xmax]),
    yaxis=dict(visible=False, autorange=False, range=[ymin, ymax]),
    hovermode="closest",
    legend=dict(x=0.99, y=0.99, xanchor="right", yanchor="top"),
    sliders=[{
        "pad": {"t": 50},
        "currentvalue": {"prefix": "Record # "},
        "steps": [
            {"args": [[f.name], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
             "label": f.name, "method": "animate"}
            for f in frames
        ]
    }],
    updatemenus=[{
        "type": "buttons", "direction": "left", "pad": {"t": 50},
        "x": 0.5, "y": -0.2, "xanchor": "center", "yanchor": "top",
        "buttons": [
            {"label": "▶ Play",  "method": "animate",
             "args": [None, {"frame": {"duration": 200, "redraw": True}, "fromcurrent": True}]},
            {"label": "■ Pause", "method": "animate",
             "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]}
        ]
    }]
)

# 8) Dash layout
layout = html.Div([
    dbc.Container([
        dbc.Row([
           dbc.Col([
                html.H2("Network Visualization"),
                html.H5("Force-directed Layout"),
                html.P(
                    """
                    Force-Directed Layouts, also known as Spring-Embedded Layouts, are a class of algorithms for drawing graphs in an aesthetically pleasing way. The idea behind these algorithms is to consider the graph as a physical system, where nodes repel each other like charged particles, while edges attract their nodes like springs.
                    """
                ),
                 html.P(
                    """
                    This layout is excellent for visualizing the overall structure of the network, especially to identify clusters or communities within your data.                    
                    """
                ),
                html.H5("Implementation"),
                html.P(
                    """
                    Every time two attributes (say “Female” and “Browse: daily”) co-occur, we record that as an edge between node u and node v, carrying a weight equal to how often they’ve appeared together. If they haven’t co-occurred, we skip adding the edge.                    
                    """
                ),
                html.P(
                    """
                    Using the Fruchterman-Reingold algorithm, NetworkX treats each edge like a spring whose stiffness is the weight. Heavier springs pull harder.                    
                    """
                ),
                html.H5("Visualization Explained"),
                html.P(
                    "This animated spring-layout network visualizes the relationships between customer gender, "
                    "purchase frequency, and browsing frequency. Each node represents a specific attribute (e.g. “Female”, "
                    "“Browse: Multiple times a day”), and the distance between nodes is proportional to how often those "
                    "attributes co-occur in the data. Larger nodes indicate higher overall occurrence of that attribute."
                ),
                html.H5("Animation"),
                html.P(
                    "Use the slider or Play/Pause buttons to step through each record one at a time and watch the network "
                    "grow. Hover over a node to see its total occurrence count, or near an edge’s midpoint to see the exact "
                    "co-occurrence count between those two attributes."
                ),
                html.H5("Reference"),
                html.P(
                    """"""
                )
            ], width=4),
            dbc.Col(
                BigFigureCard("Gender, Purchase Frequency, Browsing Frequency Dynamic Behavior Spring-layout Network",
                              caption='Animated spring-layout network showing how co-occurrences between customer gender, purchase frequency, and browsing frequency accumulate record by record. Node size scales with the total number of occurrences of each attribute; invisible midpoint markers capture edge hover-tooltips indicating co-occurrence counts.',
                              id="network-graph", figure=fig),
                width=8
            )
        ], className="gy-3 p-3")
    ], fluid=True, style={"min-height": "93vh", "backgroundColor": "#faf9f5"})
])
