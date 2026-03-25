import streamlit as st
import altair as alt
import pandas as pd
from epf_gulu import epf_calculation_gulu
from epf_ankur import epf_calculation_ankur
import os
def render_epf():
    st.divider()
    st.subheader("EPF Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Generate EPF projection - Ankur"):
            with st.spinner("Running EPF Ankur calculations..."):
                epf_calculation_ankur()
                st.success("EPF Ankur analysis completed!")
        epf_ankur = pd.read_csv('epf_Ankur.csv') if os.path.exists('epf_Ankur.csv') else pd.DataFrame()    
    with col2:
        if st.button("Generate EPF projection - Gulu"):
            with st.spinner("Running EPF Gulu calculations..."):
                epf_calculation_gulu()
                st.success("EPF Gulu analysis completed!")
        epf_gulu = pd.read_csv('epf_Gulu.csv') if os.path.exists('epf_Gulu.csv') else pd.DataFrame()
    
    #col1, col2 = st.columns(2)
    with col3:
        selected_person = st.selectbox("Select Person for EPF Analysis", options=["Both", "Ankur", "Gulu"])
    
        if selected_person == "Ankur":
            epf = epf_ankur[['Month', 'TotalFund','CumulativeMonthlyContribution']]
        elif selected_person == "Gulu":
            epf = epf_gulu[['Month', 'TotalFund','CumulativeMonthlyContribution']]
        else:
            epf = pd.concat([
                epf_ankur[['Month', 'TotalFund','CumulativeMonthlyContribution']],
                epf_gulu[['Month', 'TotalFund','CumulativeMonthlyContribution']]
            ], ignore_index=True).groupby('Month').sum().reset_index()
    with col4:
        # --- Time slider begins
        # 1. Ensure the column is in datetime format
        epf['Month'] = pd.to_datetime(epf['Month'])
        # 2. Get the min and max dates
        min_date = epf['Month'].min().to_pydatetime()
        max_date = epf['Month'].max().to_pydatetime()

        # 3. Create the slider
        # Passing a tuple to 'value' creates a range slider
        selected_range = st.slider(
            "Select Date Range",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
            format="MMM YYYY"
        )

        # 4. Filter the DataFrame based on selection
        start_date, end_date = selected_range
        filtered_epf = epf[(epf['Month'] >= start_date) & (epf['Month'] <= end_date)]

        st.write(f"Showing data from {start_date.date()} to {end_date.date()}")
        # --- Time slider ends here

    if not filtered_epf.empty:
        base = alt.Chart(filtered_epf).encode(x='Month:T')
        # Line for the actual Fund Value
        line = base.mark_line().encode(
            y='TotalFund:Q',
            tooltip=['Month', 'TotalFund'])
    
        # Dashed line or Area for the Cumulative Contribution
        contribution = base.mark_line(strokeDash=[5,5]).encode(
            y='CumulativeMonthlyContribution:Q',
            opacity=alt.value(0.5))
    
        st.altair_chart(line + contribution, use_container_width=True)
    
    else:
        st.info("No EPF data found. Run the analyses to generate results.") 
    
