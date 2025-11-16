# streamlit_app/hr_ui.py

import streamlit as st
from utils import call_api

def hr_ui():
    st.title("HR Dashboard")

    token = st.session_state.get("token")
    if not token:
        st.error("Please login first.")
        return

    st.subheader("Pending Tickets for Approval")

    emp = st.text_input("Employee ID to fetch details")
    if st.button("Get Employee Info"):
        resp = call_api("/hr/employee-details", token, {"employee_id": emp})
        st.write(resp)

    ticket = st.text_input("Ticket ID")
    if st.button("Approve Ticket"):
        resp = call_api("/hr/approve-ticket", token, {"ticket_id": ticket})
        st.write(resp)

    if st.button("Book Flight & Hotel"):
        resp = call_api("/hr/book-travel", token, {"ticket_id": ticket})
        st.write(resp)
