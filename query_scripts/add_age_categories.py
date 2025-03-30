import json
import dash_bootstrap_components as dbc
from dash import html, dcc
import os
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()


# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Load data
with SessionLocal() as session:
    df = pd.read_sql("SELECT * FROM amz_customer_behavior", con=session.bind)

# with engine.connect() as conn:
#     conn.execute(text("ALTER TABLE amz_customer_behavior ADD COLUMN age_category TEXT;"))
#     conn.commit()
    
# Prepare figures
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

df["age_category"] = df["age"].apply(categorize_age)

# Update each row
with engine.begin() as conn:
    for index, row in df.iterrows():
        conn.execute(
            text("UPDATE amz_customer_behavior SET age_category = :age_cat WHERE id = :id"),
            {"age_cat": row["age_category"], "id": row["id"]}
        )