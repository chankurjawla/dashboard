import streamlit as st

# Define the pages
Expenses = st.Page("expenses.py", title="Expenses", icon="🎈")
#page_2 = st.Page("page_2.py", title="Page 2", icon="❄️")
#page_3 = st.Page("page_3.py", title="Page 3", icon="🎉")

# Set up navigation
pg = st.navigation([Expenses, page_2, page_3])

# Run the selected page
pg.run()