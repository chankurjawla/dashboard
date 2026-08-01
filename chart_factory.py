import streamlit as st
import pandas as pd
import altair as alt

def render_dynamic_chart(
    df: pd.DataFrame, 
    x_col: str, 
    y_col: str, 
    chart_type: str = "line", 
    group_col: str = None, 
    title: str = None,
    height: int = 400
):
    """
    Renders a modular Line or Bar chart in Streamlit.
    
    Parameters:
    - df (pd.DataFrame): Input dataframe.
    - x_col (str): Column name for the X-axis (e.g., 'MonthName', 'Date', 'Day').
    - y_col (str): Column name for the Y-axis values (e.g., 'Amount').
    - chart_type (str): 'line' or 'bar'. Defaults to 'line'.
    - group_col (str, optional): Column name to split lines/bars into groups/colors (e.g., 'Category', 'Year').
    - title (str, optional): Title header displayed above the chart.
    - height (int): Chart height in pixels.
    """
    if df.empty:
        st.warning("No data available to plot chart.")
        return

    # Work on a copy to prevent modifying the original dataframe
    chart_df = df.copy()

    # 1. Base Encoding Configuration
    encoding_kwargs = {
        'x': alt.X(f"{x_col}:N", title=x_col),  # Default to Nominal; adjust if needed
        'y': alt.Y(f"sum({y_col}):Q", title=y_col),
        'tooltip': [x_col, alt.Tooltip(f"sum({y_col}):Q", format="₹,.2f")]
    }

    # 2. Apply Grouping / Labels (Colors & Multi-line / Multi-bar logic)
    if group_col and group_col in chart_df.columns:
        # Convert group column to Nominal string so years like 2025/2026 act as categories
        chart_df[group_col] = chart_df[group_col].astype(str)
        encoding_kwargs['color'] = alt.Color(f"{group_col}:N", title=group_col)
        encoding_kwargs['tooltip'].append(group_col)
        
        # Add offset for grouped side-by-side bar charts
        if chart_type.lower() == "bar":
            encoding_kwargs['xOffset'] = f"{group_col}:N"

    # 3. Build Chart Base
    base_chart = alt.Chart(chart_df)

    # 4. Construct Selected Chart Type
    if chart_type.lower() == "line":
        chart = base_chart.mark_line(point=True).encode(**encoding_kwargs)
    elif chart_type.lower() == "bar":
        chart = base_chart.mark_bar().encode(**encoding_kwargs)
    else:
        st.error(f"Unsupported chart_type '{chart_type}'. Choose 'line' or 'bar'.")
        return

    # 5. Apply Common Layout Properties
    chart = chart.properties(
        height=height,
        title=title if title else ""
    ).interactive()

    # 6. Display Title & Chart in Streamlit
    if title:
        st.subheader(title)
        
    st.altair_chart(chart, use_container_width=True)
