import importlib
import streamlit as st
import os
import pandas as pd
import altair as alt

# Custom Modules
from processor import clean_data
#from metrics import calculate_yoy_metrics
from metrics import populatemetrics
import ui_components4 as ui 
from totalequityvalue import totalequityvalue
import sectoral_indices as si
from epf_ankur import epf_calculation_ankur
from epf_gulu import epf_calculation_gulu
import epfanalysis

# Ensure changes in logic files reflect immediately
importlib.reload(ui)
importlib.reload(si)

# --- 1. Global Setup ---
st.set_page_config(page_title="Pi Finance Dash", layout="wide", page_icon="-")
datafile = 'transactiondata.csv'

@st.cache_data(show_spinner=False)
def load_data():
    if os.path.exists(datafile):
        return clean_data(datafile)
    return None

df_raw = load_data()
if df_raw is None:
    st.error("Error: 'transactiondata.csv' not found.")
    st.stop()

# --- 2. Render Sidebar ---
# Returns filtered data, year, and the layout mode (Side-by-Side or Stacked)
df_filtered, sel_year = ui.render_sidebar(df_raw)

# --- 3. Header & Metrics ---
populatemetrics(df_filtered,sel_year)

st.divider()

# --- 4. Monthly Trend ---
ui.render_monthly_trend(df_filtered, sel_year)

# --- 4.1 Cash Flow
from cashflow import cash_flow
st.divider()
cash_flow(df_raw)



# --- 5 Month Filter for Detailed Table ---
st.subheader("Detailed Expense Ledger:")
# We use the already filtered df_filtered (which has the correct year)
available_months = sorted(df_filtered['MonthName'].unique().tolist(), 
                          key=lambda x: pd.to_datetime(x, format='%b').month)
available_years = sorted(df_filtered['Year'].unique().tolist())
available_cats = sorted(df_filtered['Category'].unique().tolist())

# Add "All" as the default option
month_options = ["All"] + available_months
year_options = ["All"] + available_years
cats_options = ["All"]  + available_cats

# Create two equal columns for the filters
col_year, col_month, col_cat = st.columns([1, 1, 1]) 

with col_year:
    selected_year = st.selectbox("📅 Year", options=year_options, index=0)

with col_month:
    selected_month = st.selectbox("📅 Month", options=month_options, index=0)

with col_cat:
    selected_cats = st.selectbox("📂 Category", options=cats_options, index=0)

# Applying the double filter to your display data
display_df = df_filtered.copy()

if selected_year != "All":
    display_df = display_df[display_df['Year'] == selected_year]
    
if selected_month != "All":
    display_df = display_df[display_df['MonthName'] == selected_month]

if selected_cats != "All":
    display_df = display_df[display_df['Category'] == selected_cats]

# Render the wrapped table
with st.expander(f"Detailed Spending: {selected_month} | {selected_cats}"):
    st.dataframe(
        display_df[["Date", "Spender", "Raw SMS"]], 
        use_container_width=True,
        hide_index=True,
        column_config={
            "Raw SMS": st.column_config.TextColumn("Raw SMS", width="large")
        }
    )


st.divider()

# --- 6. Equity Trend (Ultra-Fast Strategy) ---
st.subheader("Equity Analysis")

# Button to trigger the heavy work
if st.button('Refresh Equity Data'):
    with st.spinner("Calculating Equity Values..."):
        totalequityvalue().to_csv('total-equity-value.csv', index=False)
        st.rerun()

# Instant Load from CSV
EQUITY_FILE = 'total-equity-value.csv'
if os.path.exists(EQUITY_FILE):
    equity_df = pd.read_csv(EQUITY_FILE)
    tab1, tab2= st.tabs(["Equity Trend", "Table"])
    with tab1:
        chart = alt.Chart(equity_df).mark_line(point=True).encode(
            x='Date:T',
            y='TotalValue:Q',
            tooltip=['Date', 'TotalValue']
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)
    with tab2:
        st.dataframe(equity_df, use_container_width=True, hide_index=True)
else:
    st.info("No Equity data found. Click 'Refresh Equity Data' to generate.")

st.divider()

# --- 7. Sectoral Indices (Ultra-Fast Strategy) ---
st.subheader('Sectoral Indices')

# Button to trigger the 40-second PDF scan
if st.button('Refresh Sectoral Indices'):
    with st.spinner("Processing PDFs (takes ~40s)..."):
        # Calling the function from sectoral_indices.py
        result_df = si.sectoral_indices()
        if not result_df.empty:
            result_df.to_csv('sectoral_indices.csv', index=False)
            st.success("Successfully updated indices!")
            st.rerun()
        else:
            st.error("No data extracted from PDFs.")

# Instant Load from CSV
SECTOR_FILE = 'sectoral_indices.csv'
if os.path.exists(SECTOR_FILE):
    sectoral_df = pd.read_csv(SECTOR_FILE)
    st.dataframe(sectoral_df, use_container_width=True, hide_index=True)
else:
    st.info("No Sectoral data found. Click 'Refresh Sectoral Indices' to start PDF scan.")

# --- 8. EPF Analysis 
epfanalysis.render_epf()

# --- 9. Equity Analysis
from equity_analysis_ui import render_ui
render_ui()
