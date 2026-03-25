import pandas as pd
import streamlit as st
from datetime import datetime
import os

# Get current date and replace the day with 1
current_month = datetime.now().replace(day=1)

EQUITY_FILE = 'total-equity-value.csv'
epf_ankur = pd.read_csv('epf_Ankur.csv') if os.path.exists('epf_Ankur.csv') else pd.DataFrame()
epf_gulu = pd.read_csv('epf_Gulu.csv') if os.path.exists('epf_Gulu.csv') else pd.DataFrame()
epf = pd.concat([
    epf_ankur[['Month', 'TotalFund','CumulativeMonthlyContribution']],
    epf_gulu[['Month', 'TotalFund','CumulativeMonthlyContribution']]
    ], ignore_index=True).groupby('Month').sum().reset_index()
epf['Month'] = pd.datetime(epf['Month'])
current_epf = epf[epf['Month']==current_month]['TotalFund']
current_contri = epf[epf['Month']==current_month]['CumulativeMonthlyContribution']
def populatemetrics():
    st.title('Investment Analytics')
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Total EPF {current_month}",
    f"₹{current_epf:,.2f}",
    f"{current_epf/current_contri:.1f} Times of Contribution")
    c2.metric()
    c3.metric()
