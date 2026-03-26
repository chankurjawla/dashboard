import pandas as pd
import streamlit as st
from datetime import datatime

current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
current_month_str = current_month.strftime('%Y-%m-%d')

def calculate_yoy_metrics(df, selected_year):
    curr_df = df[df['Year'] == selected_year]
    prev_df = df[df['Year'] == (selected_year - 1)]
    
    curr_total = curr_df['Amount'].sum()
    prev_total = prev_df['Amount'].sum()
    
    curr_month_total = curr_df[curr_df['MonthYear']==current_month_str]['Amount'].sum()

    if not curr_df.empty:
        max_month = curr_df['Month'].max()
        ytd_curr = curr_df[curr_df['Month'] <= max_month]['Amount'].sum()
        ytd_prev = prev_df[prev_df['Month'] <= max_month]['Amount'].sum()
    else:
        ytd_curr, ytd_prev = 0, 0

    def get_pct_diff(curr, prev):
        if prev == 0: return 0.0
        return ((curr - prev) / prev) * 100

    return {
        "curr_total": curr_total,
        "prev_total": prev_total,
        "total_diff_pct": get_pct_diff(curr_total, prev_total),
        "ytd_curr": ytd_curr,
        "ytd_prev": ytd_prev,
        "ytd_diff_pct": get_pct_diff(ytd_curr, ytd_prev)
    }

def populatemetrics(df,sel_year):
    st.title('Financial Analytics')
    m = calculate_yoy_metrics(df, sel_year)

    c1, c2, c3 = st.columns(3)
    c1.metric(f"This Month {current_month_str}", f"₹{m['curr_month_total']:,.2s}")
    c2.metric("YTD Spending", f"₹{m['ytd_curr']:,.2f}", f"{m['ytd_diff_pct']:.1f}% vs Prev YTD", delta_color="inverse")
    ytd_var = m['ytd_curr'] - m['ytd_prev']
    c3.metric("YTD Variance", f"₹{abs(ytd_var):,.2f}", "Down" if ytd_var > 0 else "Up", delta_color="normal")

