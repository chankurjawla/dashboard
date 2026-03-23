import pandas as pd
import numpy as np
import streamlit as st

def cash_flow(raw_df):
    df =raw_df.copy()
    conditions = [
        df['category'].str.contains('Loan', case=False),
        df['category'].str.contains('investment', case=False),
        df['category'].str.contains('salary|dividend', case=False) # '|' acts as OR
    ]

    choices = ['Loan', 'investment', 'CashIn']

    df['Cash_flow'] = np.select(conditions, choices, default='CashOut')
    st.dataframe(df)
    
