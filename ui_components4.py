import streamlit as st
import pandas as pd
import altair as alt

def render_sidebar(df):
    """Encapsulates all sidebar filter logic and layout controls."""
    st.sidebar.header('Dashboard Filters')
    
    # 1. Category Filter
    unique_cats = df['Category'].unique().tolist()
    all_cats = sorted([str(cat) for cat in unique_cats])
    default_exclusions = [
        cat for cat in all_cats 
        if "investment" in cat.lower() or 
        "not applicable" in cat.lower() or
        "income" in cat.lower() or
        "loan" in cat.lower()
        ]
    excluded = st.sidebar.multiselect('Exclude Categories', options=all_cats, default=default_exclusions)
    df_filtered1 = df[~df['Category'].isin(excluded)].copy()
    
    # 1.1 Category filter
    default_inclusions = [
        cat for cat in all_cats
        if "investment" not in cat.lower() or
        "not applicable" not in cat.lower() or
        "loan" not in cat.lower()
        ]
    included = st.sidebar.multiselect('Include Categories', options=all_cats, default=default_inclusions)
    df_filtered = df_filtered1[df_filtered1['Category'].isin(included)].copy()
    
    # 2. Year Filter
    all_years = sorted(df_filtered['Year'].unique().tolist(), reverse=True)
    current_year = max(all_years)
    sel_year = st.sidebar.selectbox('Current Year', options=all_years)

    st.sidebar.divider()
    
    # 3. System Controls
    st.sidebar.subheader("System Controls")
    if st.sidebar.button('Sync Data & Refresh', use_container_width=True):
        st.cache_data.clear()
        st.rerun()
        
    return df_filtered, sel_year

def render_monthly_trend(df, sel_year):
    """Renders the discrete monthly line chart comparing current vs last year."""

    # 1. Prepare data
    currnlastyear_df = df[df['Year'].isin([sel_year, sel_year-1])].copy()
    curryear_df = df[df['Year'].isin([sel_year])].copy()
    monthly_data = currnlastyear_df.groupby(['Year', 'MonthName', 'Month'])['Amount'].sum().reset_index()
    monthly_data = monthly_data.sort_values(['Year', 'Month'])
    
    # Spending over the years
    yearly_agg_data =df.groupby('Year')['Amount'].sum().reset_index().sort_values(['Year'], ascending=False)
    yearly_agg_data['LY Amount'] = yearly_agg_data['Amount'].shift(-1)
    yearly_agg_data['YoY Change'] = (yearly_agg_data['Amount'] - yearly_agg_data['LY Amount'])*100/yearly_agg_data['LY Amount']
    
    Amount = 'Current Year Spending'
    LY_Amount = 'Last Year Spending'
    YoY_Change = 'YoY Change'
    
    yearly_agg_data = yearly_agg_data.rename(columns={
        'Amount': Amount,
        'LY Amount': LY_Amount,
        'YoY Change': YoY_Change
    })
    
    yearly_agg_data = yearly_agg_data.set_index('Year')
    
    def style_yoy(val):
        color = '#d4edda' if val < 0 else '#f8d7da' # Light Green / Light Red
        text_color = '#155724' if val < 0 else '#721c24' # Dark Green / Dark Red
        return f'background-color: {color}; color: {text_color}; font-weight: bold;'
 
    styled_yearly_agg_df = yearly_agg_data.style.format({
        Amount: "₹{:,.0f}",
        LY_Amount: "₹{:,.0f}",
        YoY_Change: "{:,.0f}%"
    }).map(style_yoy, subset=[YoY_Change])
    
    st.subheader(f"Spendings over the years:")
    
    #st.dataframe(styled_yearly_agg_df, width='stretch', hide_index=True)
    st.table(styled_yearly_agg_df)

    st.divider()
    
    st.subheader(f"Monthly Spending Trend: {sel_year} vs {sel_year-1}")
    # 2. Monthly Histogram - Curr Vs last year
    monthly_trend_histo = alt.Chart(monthly_data).mark_bar().encode(
        # Sort X by the 'Month' number so it's chronological
        x=alt.X('MonthName', sort=alt.EncodingSortField(field='Month', order='ascending'), title='Month'),
        y=alt.Y('Amount', title='Total Spending'),
        xOffset = 'Year:N',
        # This creates the two separate lines
        color='Year:N', 
        tooltip=['Year', 'MonthName', 'Amount']
    ).properties(
        height=400
    )
    st.altair_chart(monthly_trend_histo, width='stretch', theme='streamlit')

    #####----------
    # 1. Define the base chart logic shared by both bars and labels
    base = alt.Chart(monthly_data).encode(
        x=alt.X('MonthName:N', sort=alt.EncodingSortField(field='Month'), title='Month'),
        y=alt.Y('Amount:Q', title='Total Spending', axis=alt.Axis(format='.2s')),
        xOffset='Year:N',
        color='Year:N'
    )

    # 2. Create the bars
    bars = base.mark_bar().encode(
        tooltip=[
            alt.Tooltip('Year:N'),
            alt.Tooltip('MonthName:N'),
            alt.Tooltip('Amount:Q', format='.2f')
        ]
    )

    # 3. Create concise labels (using SI prefix 's' for 'k', 'M', etc.)
    labels = base.mark_text(
        dy=-10,       # Shift text above the bar
        baseline='bottom',
        fontSize=10,
        fontWeight='bold'
    ).encode(
        text=alt.Text('Amount:Q', format='.2s') # '$.2s' makes it concise (e.g., $1.5k)
    )

    # 4. Layer them together
    monthly_trend_histo = (bars + labels).properties(
        height=400,
        width='container'
    ).interactive()
    st.altair_chart(monthly_trend_histo, use_container_width=True)

    #####----------

    # 2. Category split histogram for Curr year
    st.divider()
    category_df = curryear_df.groupby(['Category'])['Amount'].sum().reset_index().sort_values(by='Amount', ascending=False)
    category_histo = alt.Chart(category_df).mark_bar().encode(
        # Sort X by the 'Month' number so it's chronological
        x=alt.X('Category', sort=alt.EncodingSortField(order='ascending')),
        y=alt.Y('Amount'),
        # This creates the two separate lines
        # color='Category:N', 
        tooltip=['Category', 'Amount']
    ).properties(
        height=400
    )
    st.subheader("Spending by Category : YTD")
    #st.altair_chart(category_histo, width='stretch', theme='streamlit')
    
    # Category Heatmap for Curr year
    pivot_1 = curryear_df.pivot_table(
        index='Category', columns='MonthName', values='Amount', 
        aggfunc='sum', observed=False
    )
    
    styled_df = pivot_1.style.format("₹{:,.0f}").background_gradient(cmap="Reds", axis=None)

    # Create the tab objects
    tab1, tab2, tab3, tab4= st.tabs(["Graph", "Detailed","Fixed&Variable","House Help"])
    with tab1:
        #st.header("Results")
        st.altair_chart(category_histo, width='stretch', theme='streamlit')
    with tab2:
        #st.header("Raw Data")
        st.dataframe(styled_df, width="stretch",height=650)
    with tab3:
        #st.header("Raw Data")
        st.dataframe(styled_df, width="stretch",height=650) 
    with tab4:           
        # --- 9. Equity Analysis
        from househelp import househelp_ui
        househelp_ui(df)