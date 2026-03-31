import pandas as pd
from datetime import datetime
import os

# Constants
START_DATE = '2026-03-01'
END_DATE = '2048-03-31'
FILE_NAME = 'nps.csv'

def nps():
    # Generate the date range
    date_range = pd.date_range(start=START_DATE, end=END_DATE, freq="MS")
    df = pd.DataFrame(index=date_range, columns=['Ankur', 'Gulu'])
    
    # Initialize values
    df.loc["2026-03-01", "Ankur"] = 496700
    df.loc["2026-03-01", "Gulu"] = 496700
    
    # Fill values forward and save
    df = df.ffill()
    # index_label ensures the date column is named 'date' for easier retrieval
    df.to_csv(FILE_NAME, index_label='date')

def current_nps():
    # 1. Normalize current month to the 1st of the month
    current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_str = current_month.strftime('%Y-%m-%d')
    
    if not os.path.exists(FILE_NAME):
        return 0
    
    # 2. Load CSV and set the 'date' column as index
    nps_df = pd.read_csv(FILE_NAME, index_col='date')
    
    try:
        # 3. Access the row for the current month
        row = nps_df.loc[current_month_str]
        nps_now = row['Ankur'] + row['Gulu']
        return nps_now
    except KeyError:
        return "Current month not found in the projections."

# Example Usage
if __name__ == "__main__":
    nps()  # Generate the file
    print(f"Total NPS Value for today: {current_nps()}")
