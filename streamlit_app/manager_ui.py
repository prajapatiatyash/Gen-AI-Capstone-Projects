import streamlit as st
import requests
API_BASE = st.sidebar.text_input("API Base", "http://localhost:8000")
st.title("Manager Approvals (Demo)")

manager_id = st.text_input("Manager ID (e.g., EMP002)")

if st.button("List pending"):
    resp = requests.get(f"{API_BASE}/manager/pending/{manager_id}")
    st.write(resp.json())

indent = st.text_input("Indent ID to approve")
comments = st.text_input("Comments")

if st.button("Approve"):
    payload = {"manager_id": manager_id, "indent_id": indent, "comments": comments}
    resp = requests.post(f"{API_BASE}/manager/approve", json=payload)
    st.write(resp.json())

# streamlit_app/manager_ui.py

import streamlit as st
from utils import call_api

def manager_ui():
    st.title("Manager Dashboard")

    token = st.session_state.get("token")
    if not token:
        st.error("You must log in first.")
        return

    st.subheader("Approve Pending Tickets")

    # Example input
    emp = st.text_input("Employee ID")
    if st.button("Get Employee Details"):
        resp = call_api("/manager/details", token, {"employee_id": emp})
        st.write(resp)

    ticket = st.text_input("Ticket ID")
    if st.button("Approve Ticket"):
        resp = call_api("/manager/approve", token, {"ticket_id": ticket})
        st.write(resp)

