import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

def cash_flow(raw_df):
    df = raw_df.copy()
    df = df[~(df['Category']=='Not Applicable')]
    
    # 1. Define conditions (Ensure 'Category' exists in your CSV/Source)
    conditions = [
        df['Category'].str.contains('Loan', case=False, na=False),
        df['Category'].str.contains('investment', case=False, na=False),
        df['Category'].str.contains('salary', case=False, na=False)
    ]

    choices = ['Loan', 'Investment', 'CashIn']

    # 2. Assign values
    df['Cash_flow'] = np.select(conditions, choices, default='CashOut')
    
    st.dataframe(df(df['MonthYear'] == '2026-03-01')['Category','Amount'])

    # 3. Group and Pivot (Note the 's' in values)
    df_grouped = df.groupby(['MonthYear', 'Cash_flow'], as_index=False)['Amount'].sum()
    
    # Fix: changed 'value' to 'values' and added fillna
    df_wide = df_grouped.pivot(index='MonthYear', columns='Cash_flow', values='Amount').fillna(0)
    
    # 4. Display
    st.subheader("Cash Flow over last 6 months:")
    # Ensure it's sorted by date if MonthYear is a datetime type
    st.dataframe(df_wide.tail(6))
    st.divider()

