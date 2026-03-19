import pandas as pd
import numpy as np

def epf_calculation(name,carry_forward_amount):
    # 1. Generate the sequence of dates
    date_sequence = pd.date_range(start='2026-01-01', end='2048-03-01', freq='MS')
    df = pd.DataFrame({'Month': date_sequence})    
    df["Person"] = name
    carry_forward_amount = carry_forward_amount
    """
    # 2. Add additional details if there is any chnage in Basic, contri % or 
    rate of return w/o removing existing ones
    """
    df['Basic'] = np.nan
    df.loc[df['Month'] == '2026-01-01', 'Basic'] = 74000

    df['VPFPercent'] = np.nan
    df.loc[df['Month'] == '2026-01-01', 'VPFPercent'] = 0.10

    df['EESPFPercent'] = np.nan
    df.loc[df['Month'] == '2026-01-01', 'EESPFPercent'] = 0.12

    df['ERSPFPercent'] = np.nan
    df.loc[df['Month'] == '2026-01-01', 'ERSPFPercent'] = 0.08

    df['RatePerAnnum'] = np.nan
    df.loc[df['Month'] == '2026-01-01', 'RatePerAnnum'] = 0.0810

    # 3. Forward-fill the values, then replace remaining NaNs (prior to May 2023) with 0
    df = df.ffill().fillna(0)

    # 4. Calculate MonthlyContribution directly (Basic * (VPFPercent + 12% standard PF))
    df['MonthlyContribution'] = df['Basic'] * (df['VPFPercent'] + df['EESPFPercent'] + df['ERSPFPercent'])

    # 5. Initialize recursive columns
    df['InterestEarned'] = 0.0
    df['TotalFund'] = 0.0

    # 6. Iterate through rows to calculate Interest and Total Fund step-by-step
    for i in range(len(df)):
        if i == 0:
            # First row has no previous month
            df.loc[i, 'InterestEarned'] = 0.0
            df.loc[i, 'TotalFund'] = df.loc[i, 'MonthlyContribution']+carry_forward_amount
        else:
            # Get previous month's total fund
            prev_total = df.loc[i-1, 'TotalFund']
            
            # Calculate Interest (Previous Total * Rate / 12)
            current_interest = prev_total * (df.loc[i, 'RatePerAnnum'] / 12)
            df.loc[i, 'InterestEarned'] = current_interest
            
            # Calculate Total Fund (Interest + Monthly Contribution + Previous Total)
            df.loc[i, 'TotalFund'] = current_interest + df.loc[i, 'MonthlyContribution'] + prev_total

    df["CumulativeMonthlyContribution"] = df["MonthlyContribution"].cumsum()

    # Round the columns to 2 decimal places for cleaner viewing
    df = df.round(2)
    return df.to_csv(f'epf_{name}.csv', index=False)

epf_calculation("Ankur",2615734)
