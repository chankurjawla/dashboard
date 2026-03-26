import streamlit as st
import altair as alt
import pandas as pd
import os
from fin_metrics import populatemetrics
from totalequityvalue import totalequityvalue
import sectoral_indices as si
from epf_ankur import epf_calculation_ankur
from epf_gulu import epf_calculation_gulu
import epfanalysis

st.sidebar.markdown("Investment Analytics")

# --- 1. Metrics
populatemetrics()

# --- 2. Equity Trend (Ultra-Fast Strategy) ---
st.subheader("Equity Analysis")

# Button to trigger the heavy work
if st.button('Refresh Equity Data'):
    with st.spinner("Calculating Equity Values..."):
        totalequityvalue().to_csv('total-equity-value.csv', index=False)
        st.rerun()

# Instant Load from CSV
equity_df = pd.read_csv('equity_data.csv')
EQUITY_VALUE_FILE = 'total-equity-value.csv'
if os.path.exists(EQUITY_VALUE_FILE):
    equity_value_df = pd.read_csv(EQUITY_VALUE_FILE)
    tab1, tab2= st.tabs(["Equity Trend", "Equity Qty. Table"])
    with tab1:
        chart = alt.Chart(equity_value_df).mark_line(point=True).encode(
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

# --- 3. Sectoral Indices (Ultra-Fast Strategy) ---
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

# --- 4. EPF Analysis 
epfanalysis.render_epf()
