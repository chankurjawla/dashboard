import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

def cash_flow(raw_df):
    df = raw_df.copy()
    conditions = [
        df['category'].str.contains('Loan', case=False),
        df['category'].str.contains('investment', case=False),
        df['category'].str.contains('salary|dividend', case=False) # '|' acts as OR
    ]

    choices = ['Loan', 'Investment', 'CashIn']

    df['Cash_flow'] = np.select(conditions, choices, default='CashOut')
    df_grouped = df.groupby(['MonthYear','Cash_flow'], as_index=False)['Amount'].sum()
    st.dataframe(df_grouped)

