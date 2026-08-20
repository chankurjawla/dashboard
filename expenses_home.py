import sys
import os

# 1. Fix module resolution path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import importlib
import streamlit as st
import pandas as pd
import altair as alt

# Custom Modules
from processor import clean_data
from metrics import populatemetrics
import ui_components4 as ui
from chart_factory import render_dynamic_chart
from render_chart import render_chart

# NOTE: Remove st.set_page_config from here! It must live inside main app.py

datafile = 'transactiondata.csv'

@st.cache_data(show_spinner=False)
def load_data():
    if os.path.exists(datafile):
        return clean_data(datafile)
    return None

df_all_cats = load_data()
if df_all_cats is None:
    st.error("Error: 'transactiondata.csv' not found.")
    st.stop()

# A.1. Get unique categories as a list
unique_categories = df_all_cats["Category"].unique().tolist()

# A.2. Keywords to search for
word_filter = ["home"]

# A.3. Filter category list (case-insensitive on BOTH sides)
home_related_category = [
    cat for cat in unique_categories 
    if any(word.lower() in str(cat).lower() for word in word_filter)
]

# A.4. Filter the DataFrame using .isin()
df_raw = df_all_cats[df_all_cats["Category"].isin(home_related_category)].copy()

from datetime import datetime

# 1. Get the current calendar year
current_year = datetime.now().year

# 2. Extract unique years from the DataFrame
raw_years = df_raw['Year'].dropna().unique().tolist()

# 3. Combine, deduplicate, and sort descending
all_years = sorted(set(raw_years + [current_year]), reverse=True)
current_year = max(all_years)

# --- 2. Header & Metrics ---
populatemetrics(df_raw, current_year)

st.divider()

df_monthly = (
    df_raw.groupby("MonthYear", as_index=False)["Amount"]
    .sum()
    .assign(MonthYear=lambda df: pd.to_datetime(df["MonthYear"], format="%Y/%m"))
    .sort_values("MonthYear")
    # Convert to clean formatted string after sorting
    .assign(MonthYear=lambda df: df["MonthYear"].dt.strftime("%b %Y"))  # e.g., 'Jan 2024'
    .reset_index(drop=True)
)

st.divider()

tab1, tab2= st.tabs(["By Category", "Monthly"])
with tab1:
    render_chart(
    df=df_raw,
    x_col="Category",
    y_col="Amount",
    chart_title="Spending By Category",
    chart_type="bar",
    sort_col = "Amount",
    color_col = "Category"
    )
with tab2:
    render_chart(
    df=df_monthly,
    x_col="MonthYear",
    y_col="Amount",
    chart_title=f"Monthly Spending Trend",
    chart_type="line",
    )


st.divider()

