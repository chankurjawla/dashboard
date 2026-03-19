import pandas as pd
import yfinance as yf

def totalequityvalue():
    equity_csv_file = "equity_data.csv"
    equity_df = pd.read_csv(equity_csv_file)
    equity_df['Security Symbol'] =equity_df['Security Symbol'].apply(lambda x: f"{x}.NS")
    begin_date = equity_df['Date'].min()

    equity_df['Date'] = pd.to_datetime(equity_df['Date'], format='%m-%d-%Y')
    equity_df['Net Quantity'] = equity_df['Buy Quantity'] - equity_df['Sell Quantity']
    daily_net_quantity_df = equity_df.groupby(['Date', 'Security Symbol'])['Net Quantity'].sum().reset_index()

    begin_date = pd.to_datetime(begin_date)
    current_date = pd.to_datetime('today')

    weekly_date_range = pd.date_range(start=begin_date, end=current_date, freq='W-FRI') # 'F-MON' sets the week to end on Monday

    pivot_df = daily_net_quantity_df.pivot_table(index='Date', columns='Security Symbol', values='Net Quantity', fill_value=0)
    weekly_net_quantity_df = pivot_df.resample('W-FRI').sum()
    weekly_cumulative_net_quantity_df = weekly_net_quantity_df.cumsum()
    weekly_cumulative_net_quantity_df = weekly_cumulative_net_quantity_df.reindex(weekly_date_range, fill_value=0).ffill()
    #print(weekly_cumulative_net_quantity_df.head())

    price_data = yf.download(equity_df['Security Symbol'].unique().tolist(),
                            start=weekly_cumulative_net_quantity_df.index.min(),
                            end=weekly_cumulative_net_quantity_df.index.max())['Close']

    weekly_price_data = price_data.resample('W-FRI').last()
    weekly_price_data.to_csv("price_data.csv")

    weekly_price_data = weekly_price_data.reindex(weekly_cumulative_net_quantity_df.index).ffill()

    TotalValue = (weekly_cumulative_net_quantity_df * weekly_price_data.fillna(0))
    TotalValue['TotalValue'] = TotalValue.sum(axis=1)
    TotalValue['Date'] = TotalValue.index
    return TotalValue