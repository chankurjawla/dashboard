from mf_allotment_pull import push_to_csv
import pandas as pd
import streamlit as st

def render_ui():
    st.divider()
    st.subheader("Equity:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Allotment - Ankur'):
            with st.spinner("Processing..."):
                push_to_csv("ch.ankurjawla@gmail.com","lupx encd vahn kqym")
                st.success("MF Allotment report is processed successfully.")
    with col2:
        if st.button('Allotment - Gulu'):
            with st.spinner("Processing..."):
                push_to_csv("pooja0626@gmail.com","lupx encd vahn kqym")
                st.success("MF Allotment report is processed successfully.")
    equity_file = 'equity_allotment.csv'
    equity_df = pd.read_csv(equity_file)


    def highlight_duplicates(df):
        is_duplicate = df.duplicated(keep=False)
        return ['background-color: yellow' if v else '' for v in is_duplicate]
    styled_equity_df = equity_df.style.apply(highlight_duplicates, axis=0)
    st.dataframe(styled_equity_df, use_container_width=True, hide_index=True)
    st.info("Duplicate enteries are highlighted in yellow")