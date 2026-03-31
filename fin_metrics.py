import pandas as pd
import streamlit as st
import datetime as dt
import os
from nps import current_nps

# 00. Standardize the date to the 1st of the month
current_month = dt.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
current_month_str = current_month.strftime('%Y-%m-%d')

EQUITY_FILE = 'total-equity-value.csv'
epf_ankur = pd.read_csv('epf_Ankur.csv') if os.path.exists('epf_Ankur.csv') else pd.DataFrame()
epf_gulu = pd.read_csv('epf_Gulu.csv') if os.path.exists('epf_Gulu.csv') else pd.DataFrame()

# 1. EPF
epf = pd.concat([
    epf_ankur[['Month', 'TotalFund','CumulativeMonthlyContribution']],
    epf_gulu[['Month', 'TotalFund','CumulativeMonthlyContribution']]
], ignore_index=True)

epf['Month'] = pd.to_datetime(epf['Month'])
epf = epf.groupby('Month').sum().reset_index()

# 3. Extract scalar values (using .sum() or .iloc[0] safely)
row = epf[epf['Month'] == current_month]

if not row.empty:
    current_epf = row['TotalFund'].iloc[0]
    current_contri = row['CumulativeMonthlyContribution'].iloc[0]
    ratio = current_epf / current_contri
else:
    current_epf, current_contri, ratio = 0, 0, 0

# 2. NPS
nps = current_nps() if os.path.exists('nps.csv') else 0

# 2. Equity


# 3. MF


# 4. Sum Equity anf MF

def populatemetrics():
    st.title('Investment Analytics')
    c1, c2, c3 = st.columns(3)
    
    # Using formatted string and scalar values
    c1.metric(
        label=f"Total EPF ({current_month_str})",
        value=f"₹{current_epf:,.2f}",
        delta=f"{ratio:.1f}x Contribution",
        delta_color="normal"
    )
    c2.metric(
        "NPS",
        value=f"₹{nps:,.2f}",
    )
    c3.metric("Total Net Worth", "Coming Soon")
