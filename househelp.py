import pandas as pd
import streamlit as st

def househelp_ui(df):
    df_houehelp = df.copy()

    # 1. Convert monthyear to datetime (if it isn't already)
    df_houehelp['MonthYear'] = pd.to_datetime(df_houehelp['MonthYear'])

    # 2. Define the date threshold
    date_threshold = pd.Timestamp('2026-01-01')

    # 3. Apply both filters
    # Note: Parentheses () are required around each condition when using &
    filtered_df = df_houehelp[
        (df_houehelp['Category'].str.contains('househelp', case=False, na=False)) & 
        (df_houehelp['MonthYear'] > date_threshold)
    ]
    filtered_df = filtered_df[['MonthYear','Category','Amount']]
    df_grouped = filtered_df.groupby(['MonthYear', 'Category'], as_index=False)['Amount'].sum()
        
    # Fix: changed 'value' to 'values' and added fillna
    df_wide = df_grouped.pivot(index='MonthYear', columns='Category', values='Amount').fillna(0)
    months = df_wide.shape[0]

    # Select only numeric columns to avoid errors with text or dates
    numeric_cols = df_wide.select_dtypes(include=['number']).columns

    # Add a 'Total' row at the bottom
    df_wide.loc['Total', numeric_cols] = df_wide[numeric_cols].sum()

    # Update the first matching column for row index 10
    df_wide.loc['Budget', 'HOUSEHELP - COOK']] = 6000
    df_wide.loc['Budget', 'HOUSEHELP - AAYA']] = 13000
    df_wide.loc['Budget', 'HOUSEHELP - IRON']] = 700

    for i df_wide.shape[1]-1:
        df_wide.loc['Due',df_wide.columns[i+1]] = df_wide.loc['Budget',df_wide.columns[i+1]]*months - df_wide.loc['Total',df_wide.columns[i+1]]

    #  Display
    st.subheader("Househelp Dues since Jan-2026:")
    # Ensure it's sorted by date if MonthYear is a datetime type
    st.dataframe(df_wide)
    st.divider()