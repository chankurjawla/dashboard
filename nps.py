import pandas as pd
from datetime import datetime

START_DATE = '2026-03-01'
END_DATE = '2048-03-31'

def get_nps_data():
    """Generates the NPS dataframe in memory."""
    date_range = pd.date_range(start=START_DATE, end=END_DATE, freq="MS")
    df = pd.DataFrame(index=date_range, columns=['Ankur', 'Gulu'])
    
    # Initialize values
    df.loc[pd.Timestamp(START_DATE), "Ankur"] = 496700
    df.loc[pd.Timestamp(START_DATE), "Gulu"] = 496700
    
    # Fill values forward
    return df.ffill()

def current_nps():
    """Retrieves the sum for the current month without file I/O."""
    df = get_nps_data()
    
    # Normalize current time to the 1st of the month
    now = datetime.now()
    current_month = pd.Timestamp(year=now.year, month=now.month, day=1)
    
    try:
        row = df.loc[current_month]
        return float(row['Ankur'] + row['Gulu'])
    except KeyError:
        # Fallback if current date is outside range
        return 0.0
