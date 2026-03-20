import importlib
import streamlit as st
import os
import pandas as pd
import altair as alt

# Custom Modules
from processor import clean_data
from metrics import calculate_yoy_metrics
import ui_components4 as ui 
from totalequityvalue import totalequityvalue
import sectoral_indices as si
from epf_ankur import epf_calculation_ankur
from epf_gulu import epf_calculation_gulu

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
df_filtered, sel_year, Layout_mode = ui.render_sidebar(df_raw)

# --- 3. Header & Metrics ---
st.title('Financial Analytics')
m = calculate_yoy_metrics(df_filtered, sel_year)

c1, c2, c3 = st.columns(3)
c1.metric(f"Total {sel_year}", f"₹{m['curr_total']:,.2f}", f"{m['total_diff_pct']:.1f}% vs Prev")
c2.metric("YTD Spending", f"₹{m['ytd_curr']:,.2f}", f"{m['ytd_diff_pct']:.1f}% vs Prev YTD", delta_color="inverse")
ytd_var = m['ytd_curr'] - m['ytd_prev']
c3.metric("YTD Variance", f"₹{abs(ytd_var):,.2f}", "Down" if ytd_var > 0 else "Up", delta_color="normal")

st.divider()

# --- 4. Monthly Trend ---
ui.render_monthly_trend(df_filtered, sel_year)

# --- 5. Detailed Tables (Expandable to save space) ---
st.divider()

# --- 4.5 Month Filter for Detailed Table ---
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

st.divider()

# --- 8. EPF Analysis ---
st.subheader("EPF Analysis")

col1, col2 = st.columns(2)

with col1:
    if st.button("Run EPF Ankur Analysis"):
        with st.spinner("Running EPF Ankur calculations..."):
            epf_calculation_ankur()
            st.success("EPF Ankur analysis completed!")

with col2:
    if st.button("Run EPF Gulu Analysis"):
        with st.spinner("Running EPF Gulu calculations..."):
            epf_calculation_gulu()
            st.success("EPF Gulu analysis completed!")

st.subheader("EPF Projection : Total Fund & Contribution")
epf_ankur = pd.read_csv('epf_Ankur.csv') if os.path.exists('epf_Ankur.csv') else pd.DataFrame()
epf_gulu = pd.read_csv('epf_Gulu.csv') if os.path.exists('epf_Gulu.csv') else pd.DataFrame()

selected_person = st.selectbox("Select Person for EPF Analysis", options=["Both", "Ankur", "Gulu"])

if selected_person == "Ankur":
    epf = epf_ankur[['Month', 'TotalFund','CumulativeMonthlyContribution']]
elif selected_person == "Gulu":
    epf = epf_gulu[['Month', 'TotalFund','CumulativeMonthlyContribution']]
else:
    epf = pd.concat([
        epf_ankur[['Month', 'TotalFund','CumulativeMonthlyContribution']],
        epf_gulu[['Month', 'TotalFund','CumulativeMonthlyContribution']]
    ], ignore_index=True).gourpby('Month').sum().reset_index()

if not epf.empty:
    base = alt.Chart(epf).encode(x='Month:T')
    # Line for the actual Fund Value
    line = base.mark_line(point=True).encode(
        y='TotalFund:Q',
        color='Person:N',
        tooltip=['Person', 'Month', 'TotalFund'])

    # Dashed line or Area for the Cumulative Contribution
    contribution = base.mark_line(strokeDash=[5,5]).encode(
        y='CumulativeMonthlyContribution:Q',
        color='Person:N',
        opacity=alt.value(0.5))

    st.altair_chart(line + contribution, use_container_width=True)

else:
    st.info("No EPF data found. Run the analyses to generate results.") 

st.divider()
if not epf.empty:
    # 1. We "fold" the two columns into one for the Y-axis
    # 2. We map the 'key' (column name) to Color to create the legend
    chart = alt.Chart(epf).transform_fold(
        ['TotalFund', 'CumulativeMonthlyContribution'],
        as_=['Metric', 'Value']
    ).mark_line(point=True).encode(
        x=alt.X('Month:T', title='Month'),
        y=alt.Y('Value:Q', title=None), # Setting title to None removes the Y-axis label
        color=alt.Color('Metric:N', title='Legend'), # This creates the legend for the metrics
        detail='Person:N', # Keeps the lines separate if there are multiple people
        tooltip=['Person', 'Month', 'Metric:N', 'Value:Q']
    ).properties(
        height=400,
        width='container'
    ).interactive()

    st.altair_chart(chart, use_container_width=True)
else:
    st.info("Nothing")
