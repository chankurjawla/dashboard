import importlib
import streamlit as st
import os
import pandas as pd
import altair as alt

# Custom Modules
from processor import clean_data
from metrics import populatemetrics
import ui_components4 as ui 


# --- 1. Global Setup ---
st.set_page_config(page_title="Pi Finance Dash", layout="wide", page_icon="-")
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

# A.3. Filter category list (case-insensitive search for safety)
home_related_category = [
    cat for cat in unique_categories 
    if any(word in str(cat).lower() for word in word_filter)
]

# A.4. Filter the DataFrame using .isin()
df_raw = df_all_cats[df_all_cats["Category"].isin(home_related_category)].copy()

# --- 2. Render Sidebar ---
# Returns filtered data, year, and the layout mode (Side-by-Side or Stacked)
current_year = ui.render_sidebar(df_raw)[1]
df_filtered = df_raw
# --- 3. Header & Metrics ---

populatemetrics(df_filtered,current_year)

st.divider()

# --- 4. Monthly Trend ---
ui.render_monthly_trend(df_filtered, current_year)
