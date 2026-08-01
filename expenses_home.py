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

# --- 2. Render Sidebar ---
# Safely capture return values
sidebar_output = ui.render_sidebar(df_raw)
df_filtered = sidebar_output[0]
current_year = sidebar_output[1]

# --- 3. Header & Metrics ---
populatemetrics(df_filtered, current_year)

st.divider()

# --- 4. Monthly Trend ---
ui.render_monthly_trend(df_filtered, current_year)