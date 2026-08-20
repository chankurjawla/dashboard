import altair as alt
import streamlit as st


def render_chart(
    df,
    x_col: str,
    y_col: str,
    chart_title: str,
    chart_type: str = "bar",
    color_col: str | None = None,
    sort_col: str | None = None,
    height: int = 400,
):
    """Renders a reusable Altair Bar or Line chart with labels and tooltips in Streamlit.

    Parameters
    ----------
    - df: Input pandas DataFrame
    - x_col: Name of the column for the X-axis (nominal/ordinal/temporal)
    - y_col: Name of the column for the Y-axis (quantitative)
    - chart_title: Subheader title displayed above the chart
    - chart_type: 'bar' or 'line' (default: 'bar')
    - color_col: Optional column name for grouping/coloring (e.g., 'Year')
    - sort_col: Optional column name to sort the X-axis (e.g., 'Month' number for MonthName)
    - height: Chart height in pixels (default: 400)
    """
    if chart_title:
        st.subheader(chart_title)

    # 1. Configure X-axis with optional sort order
    x_sort = alt.EncodingSortField(field=sort_col) if sort_col else None
    x_encoding = alt.X(f"{x_col}:N", sort=x_sort, title=x_col)

    # 2. Configure Y-axis with SI prefix formatting (k, M)
    y_encoding = alt.Y(
        f"sum({y_col}):Q",
        title=f"Total {y_col}",
        axis=alt.Axis(format=".2s"),
    )

    # 3. Base tooltips
    tooltips = [
        alt.Tooltip(f"{x_col}:N", title=x_col),
        alt.Tooltip(f"sum({y_col}):Q", title=f"Total {y_col}", format=",.2f"),
    ]

    # 4. Initialize Base Chart
    base = alt.Chart(df)
    if color_col:
        base = base.encode(
            color=alt.Color(f"{color_col}:N", title=color_col),
            **({"xOffset": f"{color_col}:N"} if chart_type.lower() == "bar" else {})
        )
        tooltips.insert(0, alt.Tooltip(f"{color_col}:N", title=color_col))

    # 5. Build geometry based on chart_type
    chart_type_lower = chart_type.lower()

    if chart_type_lower == "line":
        marks = base.mark_line(point=True).encode(
            x=x_encoding, y=y_encoding, tooltip=tooltips
        )
        labels = marks.mark_text(
            dy=-12, baseline="bottom", fontSize=10, fontWeight="bold"
        ).encode(text=alt.Text(f"sum({y_col}):Q", format=".2s"))
    else:  # Default to Bar
        marks = base.mark_bar().encode(
            x=x_encoding, y=y_encoding, tooltip=tooltips
        )
        labels = marks.mark_text(
            dy=-8, baseline="bottom", fontSize=10, fontWeight="bold"
        ).encode(text=alt.Text(f"sum({y_col}):Q", format=".2s"))

    # 6. Layer and render
    final_chart = (marks + labels).properties(height=height, width="container")
    st.altair_chart(final_chart, use_container_width=True)
