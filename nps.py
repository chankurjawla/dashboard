import pandas as pd
from datetime import datetime
import streamlit as st
import os

start_date = '2026-03-01'
end_date = '2048-03-31'
def nps():
    date_range = pd.date_range(start=start_date, end=end_date, freq="MS")
    df = pd.DataFrame(index= date_range, columns =['Ankur','Gulu'])
    df.loc["2026-03-01","Ankur"]= 496700
    df.loc["2026-03-01","Ankur"]= 496700
    df = df.ffill()
    df.to_csv('nps.csv')

def current_nps():
    current_month = dt.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_str = current_month.strftime('%Y-%m-%d')
    nps = pd.read_csv('nps.csv') if os.path.exists('nps.csv') else pd.DataFrame()
    nps_now =nps.loc[current_month_str]['Ankur'].iloc[0]+nps.loc[current_month_str]['Gulu'].iloc[0]
    return nps_now