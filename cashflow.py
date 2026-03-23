import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

def cash_flow(raw_df):
    df = raw_df.copy()
    conditions = [
        df['Category'].str.contains('Loan', case=False),
        df['Category'].str.contains('investment', case=False),
        df['Category'].str.contains('salary|dividend', case=False) # '|' acts as OR
    ]

    choices = ['Loan', 'Investment', 'CashIn']

    df['Cash_flow'] = np.select(conditions, choices, default='CashOut')
    df_grouped = df.groupby(['MonthYear','Cash_flow'], as_index=False)['Amount'].sum()
    df_wide = df_grouped.pivot(index='MonthYear', columns='Cash_flow', value='Amount')
    st.subheader("Cash Flow over last 6 months:")
    st.dataframe(df_wide.tail(6))
    st.divider()

