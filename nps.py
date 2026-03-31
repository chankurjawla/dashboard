import pandas as pd
from datetime import datetime
import os

start_date = '2026-03-01'
end_date = '2048-03-31'
FILE_NAME = 'nps.csv'

def nps():
    # freq="MS" creates Month Start dates
    date_range = pd.date_range(start=start_date, end=end_date, freq="MS")
    df = pd.DataFrame(index=date_range, columns=['Ankur', 'Gulu'])
    
    # Use pd.Timestamp to match the DatetimeIndex type exactly
    df.loc[pd.Timestamp("2026-03-01"), "Ankur"] = 496700
    df.loc[pd.Timestamp("2026-03-01"), "Gulu"] = 496700
    
    df = df.ffill()
    # Save with the index named 'date'
    df.to_csv(FILE_NAME, index_label='date')

def current_nps():
    if not os.path.exists(FILE_NAME):
        nps() # Generate it if it doesn't exist
    
    # parse_dates=True converts the 'date' column back into Datetime objects
    df = pd.read_csv(FILE_NAME, index_col='date', parse_dates=True)
    
    # Normalize current time to the first of the month
    current_month = pd.Timestamp(datetime.now()).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    try:
        # Now both the index and the key are Timestamps
        row = df.loc[current_month]
        return row['Ankur'] + row['Gulu']
    except KeyError:
        return 0.0
