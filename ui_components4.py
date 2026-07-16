import streamlit as st
import pandas as pd
import altair as alt

def render_sidebar(df):
    """Encapsulates all sidebar filter logic and layout controls."""
    st.sidebar.header('Dashboard Filters')
    
    # 1. Category Filter
    all_cats = df['Category'].unique().tolist()

    # 1.1 Define keywords to filter out
    excluded_cats = ["investment", "not applicable", "income", "loan"]

    # 1.2 Build exclusions
    default_cat_exclusions = [
        cat for cat in all_cats 
        if any(word in cat.lower() for word in excluded_cats)]

    # 1.3 Inclusions are just the categories NOT in exclusions
    default_cat_inclusions = [cat for cat in all_cats if cat not in default_cat_exclusions]   
    
    included_cats = st.sidebar.multiselect('Include Categories', options=all_cats, default=default_cat_inclusions)
    
    df_filtered = df[df['Category'].isin(included_cats)].copy()
    
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
        
    return df_filtered, current_year

def render_monthly_trend(df, sel_year):
    """Renders the discrete monthly line chart comparing current vs last year."""

    # 1. Prepare data
    currnlastyear_df = df[df['Year'].isin([sel_year, sel_year-1])].copy()
    curryear_df = df[df['Year'].isin([sel_year])].copy()
    
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
    
    #yearly_agg_data = yearly_agg_data.set_index('Year')
    
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
    
    st.table(styled_yearly_agg_df)
    
    st.divider()

    # 2. Monthly Histogram - Curr Vs last year
    st.subheader(f'Monthly Spending Trend: {sel_year} vs {sel_year-1}')
    # A. Define the base chart logic shared by both bars and labels
    base = alt.Chart(currnlastyear_df).encode(
        alt.Color('Year:N'),
        xOffset = 'Year:N'
    )

    # B. Create the bars
    bars = base.mark_bar().encode(
        x=alt.X('MonthName:N', sort=alt.EncodingSortField(field='Month'), title='Month'),
        y=alt.Y('sum(Amount):Q', title='Total Spending', axis=alt.Axis(format='.2s')),
        tooltip=[
            alt.Tooltip('Year:N'),
            alt.Tooltip('MonthName:N'),
            alt.Tooltip('sum(Amount):Q', format='.2f')
        ]
    )

    # C. Create concise labels (using SI prefix 's' for 'k', 'M', etc.)
    labels = bars.mark_text(
        dy=-10,       # Shift text above the bar
        baseline='bottom',
        fontSize=10,
        fontWeight='bold'
    ).encode(
        text=alt.Text('sum(Amount):Q', format='.2s') # '$.2s' makes it concise (e.g., $1.5k)
    )

    # D. Layer them together
    monthly_trend_histo = (bars + labels).properties(
        height=400,
        width='container'
    )
    st.altair_chart(monthly_trend_histo, width='stretch')
    st.divider()

    # 2. Category split histogram for Curr year
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
    
    # Category Heatmap for Curr year
    CatHeatMap_pivot = curryear_df.pivot_table(
        index='Category', columns='MonthName', values='Amount', 
        aggfunc='sum', observed=True
    )
    #drop columns with all values as zero
    CatHeatMap_pivot = CatHeatMap_pivot.loc[:, (CatHeatMap_pivot != 0).any(axis=0)]

    styled_CatHeatMap = CatHeatMap_pivot.style.format("₹{:,.0f}").background_gradient(cmap="Reds", axis=None) 


    # 3. Fixed Vs Variable
    filtered_cats = curryear_df['Category'].unique().tolist()
    fixed_cat_words = ["rent","education","househelp"]
    fixed_cats = [
        cat for cat in filtered_cats
        if any(word in cat.lower() for word in fixed_cat_words)
    ]
    
    variable_cats = [
        cat for cat in filtered_cats
        if cat not in fixed_cats
        ]
    FixedAndVariable_df = curryear_df.copy()
    FixedAndVariable_df.loc[FixedAndVariable_df['Category'].isin(variable_cats),'expensetype'] = "Variable"
    FixedAndVariable_df.loc[~FixedAndVariable_df['Category'].isin(variable_cats),'expensetype'] = "Fixed"
    FixedAndVariable_pivot = FixedAndVariable_df.pivot_table(
        index = "MonthName",
        columns = "expensetype",
        values="Amount",
        aggfunc="sum",
        observed=True
        )
    # Drops columns where every single value is 0
    FixedAndVariable_pivot = FixedAndVariable_pivot.loc[:, (FixedAndVariable_pivot != 0).any(axis=0)]

    styled_FixedAndVariable_pivot = FixedAndVariable_pivot.style.format("₹{:,.0f}").background_gradient(cmap="Reds", axis=None)
    
    
    # 4. Daily Expense Trend for current month (Variable expenses only)
    VariableTrend_df = FixedAndVariable_df[FixedAndVariable_df['expensetype']=='Variable'].copy()
    
    # 4.1 Force standard datetime conversion
    VariableTrend_df['Date'] = pd.to_datetime(VariableTrend_df['Date'])
    
    # 4.2 Explicitly force Day as a clean, standard integer column
    VariableTrend_df['Day'] = VariableTrend_df['Date'].dt.day.astype(int)
    
    available_months = sorted(
        VariableTrend_df['MonthName'].unique().tolist(), 
        key=lambda x: pd.to_datetime(x, format='%b').month
    )
    currentmonth = available_months[-1] if available_months else None

    if currentmonth:
        # 3. Filter down to just the current month
        daily_df = VariableTrend_df[VariableTrend_df['MonthName'] == currentmonth].copy()
        
        # 4. Group, sort, and reset index cleanly
        daily_agg = daily_df.groupby('Day')['Amount'].sum().reset_index()
        daily_agg = daily_agg.sort_values('Day')
        
        # 5. Calculate cumulative sum and force float type for safety
        daily_agg['Cumulative Amount'] = daily_agg['Amount'].cumsum().astype(float)
        daily_agg['Amount'] = daily_agg['Amount'].astype(float)

        # 6. Build a dead-simple chart structure using Quantitative scale WITHOUT hardcoded domains
        daily_trend_chart = alt.Chart(daily_agg).mark_bar().encode(
            x=alt.X('Day:O', title='Day of Month'),
            y=alt.Y('Cumulative Amount:Q', title='Daily Spend'),
            tooltip=[
                alt.Tooltip('Day:O', title='Day'),
                alt.Tooltip('Amount:Q', title='Daily Spend', format='₹,.2f')
                #alt.Tooltip('Cumulative Amount:Q', title='Total So Far', format='₹,.2f')
            ]
        ).properties(
            height=350,
            title=f"Variable Spending Accumulation — {currentmonth} {sel_year}"
        )
    else:
        daily_trend_chart = None
    
    
    
    
    # Create the tab objects
    tab1, tab2, tab3, tab4, tab5= st.tabs(["Graph", "Detailed","Fixed&Variable","House Help","Daily Trend"])
    with tab1:
        #st.header("Results")
        st.altair_chart(category_histo, width='stretch', theme='streamlit')
    with tab2:
        #st.header("Raw Data")
        st.dataframe(styled_CatHeatMap, width="stretch",height=650)
    with tab3:
        #st.header("Raw Data")
        st.dataframe(styled_FixedAndVariable_pivot, width="stretch",height=650) 
    with tab4:           
        # Househelp table
        from househelp import househelp_ui
        househelp_ui(df)
    with tab5:
        # Daily Expense trend
        if daily_trend_chart is not None:
            st.subheader(f"Daily Trajectory for {currentmonth}")
            st.altair_chart(daily_trend_chart)
            #st.dataframe(daily_agg)
            # Show a small metric summary below it
            total_var_spend = daily_agg['Amount'].sum()
            st.metric(label=f"Total Variable Spend in {currentmonth}", value=f"₹{total_var_spend:,.2f}")
        else:
            st.info("No variable expense data available for the current month loop.")
