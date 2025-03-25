import dash_bootstrap_components as dbc
from dash import html

# Table Header
table_header = [
    html.Thead(html.Tr([html.Th("Column"), html.Th("Descriptions")]))
]

table_rows = [
    ("age", "Age"),
    ("gender", "Gender"),
    ("purchase_frequency", "How frequently do you make purchases on Amazon?"),
    ("purchase_categories", "What product categories do you typically purchase on Amazon?"),
    ("personalized_recommendation_frequency", "Have you ever made a purchase based on personalized product recommendations from Amazon?"),
    ("browsing_frequency", "How often do you browse Amazon's website or app?"),
    ("product_search_method", "How do you search for products on Amazon?"),
    ("search_result_exploration", "Do you tend to explore multiple pages of search results or focus on the first page?"),
    ("customer_reviews_importance", "How important are customer reviews in your decision-making process?"),
    ("add_to_cart_browsing", "Do you add products to your cart while browsing on Amazon?"),
    ("cart_completion_frequency", "How often do you complete the purchase after adding products to your cart?"),
    ("cart_abandonment_factors", "What factors influence your decision to abandon a purchase in your cart?"),
    ("saveforlater_frequency", "Do you use Amazon's 'Save for Later' feature, and if so, how often?"),
    ("review_left", "Have you ever left a product review on Amazon?"),
    ("review_reliability", "How much do you rely on product reviews when making a purchase?"),
    ("review_helpfulness", "Do you find helpful information from other customers' reviews?"),
    ("personalized_recommendation_frequency_int (*)", "How often do you receive personalized product recommendations from Amazon?"),
    ("recommendation_helpfulness", "Do you find the recommendations helpful?"),
    ("rating_accuracy", "How would you rate the relevance and accuracy of the recommendations you receive?"),
    ("shopping_satisfaction", "How satisfied are you with your overall shopping experience on Amazon?"),
    ("service_appreciation", "What aspects of Amazon's services do you appreciate the most?"),
    ("improvement_areas", "Are there any areas where you think Amazon can improve?")
]

# Build Table Body
table_body = [
    html.Tbody([
        html.Tr([html.Td(var), html.Td(question)]) for var, question in table_rows
    ]),
    html.P("*: Renamed due to duplicate column name.")
]

# Combine header and body
table = dbc.Table(table_header + table_body, bordered=True, hover=True, responsive=True, striped=True)
