import pandas as pd

def calculate_yoy_metrics(df, selected_year):
    curr_df = df[df['Year'] == selected_year]
    prev_df = df[df['Year'] == (selected_year - 1)]
    
    curr_total = curr_df['Amount'].sum()
    prev_total = prev_df['Amount'].sum()
    
    if not curr_df.empty:
        max_month = curr_df['Month'].max()
        ytd_curr = curr_df[curr_df['Month'] <= max_month]['Amount'].sum()
        ytd_prev = prev_df[prev_df['Month'] <= max_month]['Amount'].sum()
    else:
        ytd_curr, ytd_prev = 0, 0

    def get_pct_diff(curr, prev):
        if prev == 0: return 0.0
        return ((curr - prev) / prev) * 100

    return {
        "curr_total": curr_total,
        "prev_total": prev_total,
        "total_diff_pct": get_pct_diff(curr_total, prev_total),
        "ytd_curr": ytd_curr,
        "ytd_prev": ytd_prev,
        "ytd_diff_pct": get_pct_diff(ytd_curr, ytd_prev)
    }
