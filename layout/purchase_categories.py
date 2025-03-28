import json
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, callback_context
import os
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .components.MetricCard import MetricCard
from .components.FigureCard import FigureCard
import numpy as np
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Load data
with SessionLocal() as session:
    df = pd.read_sql("SELECT * FROM amz_customer_behavior", con=session.bind)
    
columns = ['age', 'gender', 'purchase_frequency', 'purchase_categories']

# Transforming the age data by creating 10 year bins
bins = [0, 10, 20, 30, 40, 50, 60, 70]
ab_labels = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70']
df['age_bin'] = pd.cut(df['age'], bins=bins, labels=ab_labels, right=False)

# Splitting multiple purchase categories into separate rows
df["purch_cat_list"] = df["purchase_categories"].str.split(";")
df_sep_cat = df.explode("purch_cat_list").copy()

# Setting up order and labels for purchase frequency
x_axis = ["Multiple times a week", "Once a week", "Few times a month", "Once a month", "Less than once a month"]

# Discrete color map based on gender
bubble_colors = {"female": "#e976aa", "male": "#1d76b5", "others": "#a4a4a4", "prefer not to say": "#4f4f4f"}

# Grouping by relevant categories to get count of occurrences
df_with_counts = (
    df_sep_cat.groupby(["age_bin", "purchase_frequency", "gender", "purch_cat_list"], observed=True)
    .size()
    .reset_index(name="count")
)

# Assign categorical codes for jitter
df_with_counts['purchase_frequency'] = pd.Categorical(df_with_counts['purchase_frequency'], categories=x_axis, ordered=True)
df_with_counts['age_bin'] = pd.Categorical(df_with_counts['age_bin'], categories=ab_labels, ordered=True)

# Add random jitter to reduce overlap
df_with_counts['xspacing'] = df_with_counts['purchase_frequency'].cat.codes + np.random.uniform(-0.1, 0.1, len(df_with_counts))
df_with_counts['yspacing'] = df_with_counts['age_bin'].cat.codes + np.random.uniform(-0.3, 0.3, len(df_with_counts))

# Create the scatter plot
fig = px.scatter(
    df_with_counts,
    x='xspacing',
    y='yspacing',
    size='count',
    # title='Top Purchase Categories based on Age, Gender, and Purchase Frequency',
    color='gender',
    color_discrete_map=bubble_colors,
    hover_name='purch_cat_list',
    hover_data={'count': True, 'purch_cat_list': False, 'gender': True, 'xspacing': False, 'yspacing': False}
)

# Customize layout
fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
fig.update_layout(xaxis=dict(tickmode='array', tickvals=list(range(len(x_axis))), ticktext=x_axis))
fig.update_layout(yaxis=dict(tickmode='array', tickvals=list(range(len(ab_labels))), ticktext=ab_labels))
fig.update_layout(xaxis_title='Purchase Frequency')
fig.update_layout(yaxis_title='Age Group')

# Add caption
fig.add_annotation(
    x=0.5,
    y=-0.2,
    xref='paper',
    yref='paper',
    # text='The figure above displays the top purchase categories based on age group, purchase frequency, and gender. The x axis displays the purchase frequency with</br></br>'
    #      ' the y axis displaying the age group. The bubbles are colored according to gender with an accompanying legend on the side. The size of the bubble increases</br>'
    #      ' based on the more matches there are for age group, gender, purchase frequency, and purchase category. Hover over the bubbles for more detailed information!',
    showarrow=False,
    align='center',
    font=dict(size=8)
)


purchase_categories_card = FigureCard(
    id="purchase_categories_card-figure",
    title="Top Purchase Categories based on Age, Gender, and Purchase Frequency",        
    figure=fig,              
    description="This chart shows how many purchases were made by each age group."
)


#Color Picker
#Female: #e976aa
#Male: #1d76b5
#Other: #a4a4a4
#Prefer Not To Say: #4f4f4f
    
purchase_categories = dbc.Row(
    [
        dbc.Col(html.H1("Top Purchase Categories Breakdown"), width=12),
        html.P("""
               The figure blow displays the top purchase categories based on age group, purchase frequency, and gender. The x axis displays the purchase frequency with</br></br>'
         ' the y axis displaying the age group. The bubbles are colored according to gender with an accompanying legend on the side. The size of the bubble increases</br>'
         ' based on the more matches there are for age group, gender, purchase frequency, and purchase category. Hover over the bubbles for more detailed information!
               """),
        dbc.Col(purchase_categories_card, width=12),
    ],
    id="purchase_categories"
)