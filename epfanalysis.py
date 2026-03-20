import streamlit as st
import pandas as pd

def render_epf()
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
        ], ignore_index=True).groupby('Month').sum().reset_index()
    
    if not epf.empty:
        base = alt.Chart(epf).encode(x='Month:T')
        # Line for the actual Fund Value
        line = base.mark_line(point=True).encode(
            y='TotalFund:Q',
            tooltip=['Month', 'TotalFund'])
    
        # Dashed line or Area for the Cumulative Contribution
        contribution = base.mark_line(strokeDash=[5,5]).encode(
            y='CumulativeMonthlyContribution:Q',
            opacity=alt.value(0.5))
    
        st.altair_chart(line + contribution, use_container_width=True)
    
    else:
        st.info("No EPF data found. Run the analyses to generate results.") 
    
    st.divider()
