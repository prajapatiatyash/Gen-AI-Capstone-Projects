import streamlit as st
from login import login_ui
from manager_ui import manager_ui
from hr_ui import hr_ui
from employee_ui import employee_ui

st.set_page_config(page_title="Travel Portal", layout="wide")

# Create session var
if "auth" not in st.session_state:
    st.session_state.auth = None

# ----------------------------
# SHOW LOGIN IF NOT LOGGED IN
# ----------------------------
if st.session_state.auth is None:
    auth = login_ui()
    if auth:
        st.session_state.auth = auth
        st.rerun()
    st.stop()

# ----------------------------
# ROUTE TO CORRECT DASHBOARD
# ----------------------------
role = st.session_state.auth["role"]
token = st.session_state.auth["token"]

if role == "manager":
    manager_ui(token)
elif role == "employee":
    employee_ui(token)
elif role == "hr":
    hr_ui(token)
