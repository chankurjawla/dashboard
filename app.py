import streamlit as st

# Define the pages
expenses = st.Page("expenses.py", title="Expenses", icon="🎈")
fin_planning = st.Page("fin_planning.py", title="Financial Planning", icon="❄️")
#page_3 = st.Page("page_3.py", title="Page 3", icon="🎉")

# Set up navigation
pg = st.navigation([expenses, fin_planning])

# Run the selected page
pg.run()