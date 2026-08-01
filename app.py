import streamlit as st

# Define the pages
expenses = st.Page("expenses.py", title="Financial Analytics", icon="💰")
expenses_home = st.Page("expenses_home.py", title="Home Purchase", icon="🏠")
fin_planning = st.Page("fin_planning.py", title="Investment Analytics", icon="🦈")
archived_app = st.Page("archived_app.py", title="Financial Analytics - Archived", icon="💾")

# Set up navigation
pg = st.navigation([expenses, expenses_home, fin_planning, archived_app])

# Run the selected page
pg.run()