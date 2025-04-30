from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from layout.components.FigureCard import FigureCard
from dash.exceptions import PreventUpdate
import dash
from dash import callback, Input, Output, State, ctx, no_update
from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError
from dash.exceptions import PreventUpdate
from datetime import datetime

dash.register_page(
    __name__,
    path='/Submit',
    title="Submit The Survey",
    description="Dashboard home for Amazon consumer analysis"
)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Load data once globally
with SessionLocal() as session:
    df = pd.read_sql("SELECT * FROM amz_customer_behavior", con=session.bind)

gender_options = df['gender'].dropna().unique().tolist()
purchase_freq_options = df['purchase_frequency'].dropna().unique().tolist()
browsing_freq_options = df['browsing_frequency'].dropna().unique().tolist()
search_method_options = df['product_search_method'].dropna().unique().tolist()
exploration_options = df['search_result_exploration'].dropna().unique().tolist()
add_to_cart_options = df['add_to_cart_browsing'].dropna().unique().tolist()
cart_completion_options = df['cart_completion_frequency'].dropna().unique().tolist()
cart_abandonment_options = df['cart_abandonment_factors'].dropna().unique().tolist()
save_for_later_options = df['saveforlater_frequency'].dropna().unique().tolist()
review_left_options = df['review_left'].dropna().unique().tolist()
review_reliability_options = df['review_reliability'].dropna().unique().tolist()
review_helpful_options = df['review_helpfulness'].dropna().unique().tolist()
rec_freq_options = df['personalized_recommendation_frequency'].dropna().unique().tolist()
rec_helpful_options = df['recommendation_helpfulness'].dropna().unique().tolist()
service_appreciation_options = df['service_appreciation'].dropna().unique().tolist()
improvement_areas_options = df['improvement_areas'].dropna().unique().tolist()
purchase_categories = df['purchase_categories'].dropna().unique().tolist()
rating_accuracy_options = df['rating_accuracy'].dropna().unique().tolist()
shopping_satisfaction_options = df['shopping_satisfaction'].dropna().unique().tolist()


# Use the correct column name: 'purchase_categories'
all_categories = df['purchase_categories'].dropna().astype(str).str.split(';')
flat_list = [item.strip() for sublist in all_categories for item in sublist if isinstance(sublist, list)]
unique_categories = sorted(set(flat_list))

unique_categories[:10]

product_category_options = [{"label": c, "value": c} for c in unique_categories]

layout = dbc.Container(className="py-4", children=[
    html.H2("Amazon Customer Behavior Survey Submission", className="mb-4"),

    # Row 1: Age & Gender
    dbc.Row([
        dbc.Col([
            html.Label("1. What is your age?"),
            dcc.Input(id="age", type="number", placeholder="Enter your age", className="form-control mb-3")
        ], width=6),
        dbc.Col([
            html.Label("2. What is your gender?"),
            dcc.Dropdown(id="gender", options=[{"label": g, "value": g} for g in gender_options], placeholder="Select...", className="mb-3")
        ], width=6)
    ], className="mb-2"),

    # Row 2
    dbc.Row([
        dbc.Col([
            html.Label("3. How frequently do you make purchases on Amazon?"),
            dcc.Dropdown(id="purchase_frequency", options=[{"label": x, "value": x} for x in purchase_freq_options], placeholder="Select...", className="mb-3")
        ], width=6),
        dbc.Col([
            html.Label("4. What product categories do you typically purchase on Amazon?"),
            dcc.Dropdown(id="purchase_categories", options=product_category_options, multi=True, placeholder="Select categories", className="mb-3")
        ], width=6)
    ], className="mb-2"),

    # Row 3
    dbc.Row([
        dbc.Col([
            html.Label("5. How often do you receive personalized product recommendations?"),
            dcc.Dropdown(id="personalized_recommendation_frequency", options=[{"label": x, "value": x} for x in rec_freq_options], placeholder="Select...", className="mb-3")
        ], width=6),
        dbc.Col([
            html.Label("6. How often do you browse Amazon's website or app?"),
            dcc.Dropdown(id="browsing_frequency", options=[{"label": x, "value": x} for x in browsing_freq_options], placeholder="Select...", className="mb-3")
        ], width=6)
    ], className="mb-2"),

    # Row 4
    dbc.Row([
        dbc.Col([
            html.Label("7. How do you search for products on Amazon?"),
            dcc.Dropdown(id="product_search_method", options=[{"label": x, "value": x} for x in search_method_options], placeholder="Select...", className="mb-3")
        ], width=6),
        dbc.Col([
            html.Label("8. Do you tend to explore multiple pages or focus on the first?"),
            dcc.Dropdown(id="search_result_exploration", options=[{"label": x, "value": x} for x in exploration_options], placeholder="Select...", className="mb-3")
        ], width=6)
    ], className="mb-2"),

    # Row 5
    dbc.Row([
        dbc.Col([
            html.Label("9. How important are customer reviews in your decisions? (1-5)"),
            dcc.Slider(id="customer_reviews_importance", min=1, max=5, step=1, marks=None, tooltip={"always_visible": True}, className="mb-3")
        ], width=6),
        dbc.Col([
            html.Label("10. Do you add products to cart while browsing?"),
            dcc.Dropdown(id="add_to_cart_browsing", options=[{"label": x, "value": x} for x in add_to_cart_options], placeholder="Select...", className="mb-3")
        ], width=6)
    ], className="mb-2"),

    # Row 6
    dbc.Row([
        dbc.Col([
            html.Label("11. How often do you complete purchases from your cart?"),
            dcc.Dropdown(id="cart_completion_frequency", options=[{"label": x, "value": x} for x in cart_completion_options], placeholder="Select...", className="mb-3")
        ], width=6),
        dbc.Col([
            html.Label("12. What factors influence you to abandon cart?"),
            dcc.Dropdown(id="cart_abandonment_factors", options=[{"label": x, "value": x} for x in cart_abandonment_options], multi=True, placeholder="Select...", className="mb-3")
        ], width=6)
    ], className="mb-2"),

    # Row 7
    dbc.Row([
        dbc.Col([
            html.Label("13. How often do you use 'Save for Later'?"),
            dcc.Dropdown(id="saveforlater_frequency", options=[{"label": x, "value": x} for x in save_for_later_options], placeholder="Select...", className="mb-3")
        ], width=6),
        dbc.Col([
            html.Label("14. Have you ever left a product review?"),
            dcc.Dropdown(id="review_left", options=[{"label": x, "value": x} for x in review_left_options], placeholder="Select...", className="mb-3")
        ], width=6)
    ], className="mb-2"),

    # Row 8
    dbc.Row([
        dbc.Col([
            html.Label("15. How much do you rely on reviews when shopping?"),
            dcc.Dropdown(id="review_reliability", options=[{"label": x, "value": x} for x in review_reliability_options], placeholder="Select...", className="mb-3")
        ], width=6),
        dbc.Col([
            html.Label("16. Do you find helpful info in other customer reviews?"),
            dcc.Dropdown(id="review_helpfulness", options=[{"label": x, "value": x} for x in review_helpful_options], placeholder="Select...", className="mb-3")
        ], width=6)
    ], className="mb-2"),

    # Row 9
    dbc.Row([
        dbc.Col([
            html.Label("17. Do you find Amazon's product recommendations helpful?"),
            dcc.Dropdown(id="recommendation_helpfulness", options=[{"label": x, "value": x} for x in rec_helpful_options], placeholder="Select...", className="mb-3")
        ], width=6),
        dbc.Col([
            html.Label("18. How would you rate the accuracy of the recommendations? (1-5)"),
            dcc.Slider(id="rating_accuracy", min=1, max=5, step=1, marks=None, tooltip={"always_visible": True}, className="mb-3")
        ], width=6)
    ], className="mb-2"),

    # Row 10
    dbc.Row([
        dbc.Col([
            html.Label("19. How satisfied are you with your shopping experience? (1-5)"),
            dcc.Slider(id="shopping_satisfaction", min=1, max=5, step=1, marks=None, tooltip={"always_visible": True}, className="mb-3")
        ], width=6),
        dbc.Col([
            html.Label("20. What aspects of Amazon's services do you appreciate most?"),
            dcc.Dropdown(id="service_appreciation", options=[{"label": x, "value": x} for x in service_appreciation_options], multi=True, placeholder="Select...", className="mb-3")
        ], width=6)
    ], className="mb-2"),

    # Row 11
    dbc.Row([
        dbc.Col([
            html.Label("21. Are there any areas where Amazon can improve?"),
            dcc.Dropdown(id="improvement_areas", options=[{"label": x, "value": x} for x in improvement_areas_options], multi=True, placeholder="Select...", className="mb-3")
        ], width=12)
    ], className="mb-2"),

    html.Div([
        dbc.Button("Submit", id="submit-button", color="primary", className="mt-3"),
        html.Div(id="form-submit-message", className="text-success mt-2"),
        dcc.Location(id="redirect", refresh=True)
    ])


])

def categorize_age(age):
    if age < 13:
        return "Child"
    elif age < 20:
        return "Teenager"
    elif age < 36:
        return "Young Adult"
    elif age < 51:
        return "Adult"
    elif age < 66:
        return "Middle-aged Adult"
    else:
        return "Older Adult"
    
@callback(
    Output("form-submit-message", "children"),
    Output("redirect", "href"),  # NEW
    Input("submit-button", "n_clicks"),
    State("age", "value"),
    State("gender", "value"),
    State("purchase_frequency", "value"),
    State("purchase_categories", "value"),
    State("personalized_recommendation_frequency", "value"),
    State("browsing_frequency", "value"),
    State("product_search_method", "value"),
    State("search_result_exploration", "value"),
    State("customer_reviews_importance", "value"),
    State("add_to_cart_browsing", "value"),
    State("cart_completion_frequency", "value"),
    State("cart_abandonment_factors", "value"),
    State("saveforlater_frequency", "value"),
    State("review_left", "value"),
    State("review_reliability", "value"),
    State("review_helpfulness", "value"),
    State("recommendation_helpfulness", "value"),
    State("rating_accuracy", "value"),
    State("shopping_satisfaction", "value"),
    State("service_appreciation", "value"),
    State("improvement_areas", "value"),
)
def submit_survey(n_clicks, age, gender, purchase_frequency, product_categories,
                  personalized_freq, browsing_freq, search_method, exploration,
                  review_importance, add_to_cart, cart_completion, cart_abandonment,
                  save_for_later, review_left, review_reliability, review_helpful,
                  rec_helpful, rating_accuracy, shopping_satisfaction,
                  service_appreciation, improvement_areas):

    if not n_clicks:
        raise PreventUpdate

    # Combine selected product categories into a single string
    combined_categories = ", ".join(product_categories) if product_categories else None
    age_category = categorize_age(age)

    # Construct the insert query
    insert_sql = """
        INSERT INTO amz_customer_behavior (
            timestamp, age, age_category, gender, purchase_frequency, purchase_categories,
            personalized_recommendation_frequency, browsing_frequency, product_search_method,
            search_result_exploration, customer_reviews_importance, add_to_cart_browsing,
            cart_completion_frequency, cart_abandonment_factors, saveforlater_frequency,
            review_left, review_reliability, review_helpfulness, recommendation_helpfulness,
            rating_accuracy, shopping_satisfaction, service_appreciation, improvement_areas
        ) VALUES (
            :timestamp, :age, :age_category, :gender, :purchase_frequency, :purchase_categories,
            :personalized_recommendation_frequency, :browsing_frequency, :product_search_method,
            :search_result_exploration, :customer_reviews_importance, :add_to_cart_browsing,
            :cart_completion_frequency, :cart_abandonment_factors, :saveforlater_frequency,
            :review_left, :review_reliability, :review_helpfulness, :recommendation_helpfulness,
            :rating_accuracy, :shopping_satisfaction, :service_appreciation, :improvement_areas
        )
    """

    values = {
        "timestamp": datetime.now(),
        "age": age,
        "age_category": age_category,
        "gender": gender,
        "purchase_frequency": purchase_frequency,
        "purchase_categories": combined_categories,
        "personalized_recommendation_frequency": personalized_freq,
        "browsing_frequency": browsing_freq,
        "product_search_method": search_method,
        "search_result_exploration": exploration,
        "customer_reviews_importance": review_importance,
        "add_to_cart_browsing": add_to_cart,
        "cart_completion_frequency": cart_completion,
        "cart_abandonment_factors": cart_abandonment,
        "saveforlater_frequency": save_for_later,
        "review_left": review_left,
        "review_reliability": review_reliability,
        "review_helpfulness": review_helpful,
        "recommendation_helpfulness": rec_helpful,
        "rating_accuracy": rating_accuracy,
        "shopping_satisfaction": shopping_satisfaction,
        "service_appreciation": service_appreciation,
        "improvement_areas": improvement_areas,
    }

    try:
        with SessionLocal() as session:
            session.execute(text(insert_sql), values)
            session.commit()
        return "✅ Your response has been submitted. Thank you!", "/Submit"
    except Exception as e:
        return f"❌ Submission failed: {str(e)}", no_update