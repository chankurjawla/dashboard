import pandas as pd
import json
import os
import streamlit as st

def clean_data(file_path):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    
    initial_count = len(df)
    
    # 1. Attempt Smart Date Parsing
    # We use dayfirst=True if your bank/source is typically DD/MM/YYYY
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=True)
    
    # 2. Check for Data Loss
    dropped_rows = df[df['Date'].isna()]
    df.dropna(subset=['Date'], inplace=True)
    final_count = len(df)
    
    # 3. Diagnostic Alert (Only shows in Streamlit when data is lost)
    if not dropped_rows.empty:
        st.sidebar.warning(f"⚠️ Dropped {len(dropped_rows)} rows due to invalid dates.")
        if st.sidebar.checkbox("View Dropped Rows"):
            st.sidebar.write(dropped_rows)

    # ... Rest of your sorting logic ...
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['MonthName'] = df['Date'].dt.strftime('%b')
    df['MonthName'] = pd.Categorical(df['MonthName'], categories=month_order, ordered=True)
    df['MonthYear'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    return df
