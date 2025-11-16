import streamlit as st
from login import show_login

st.set_page_config(page_title="Travel Indent System", layout="wide")

if "token" not in st.session_state:
    show_login()
else:
    role = st.session_state.get("role")
    print(f"User role: {st.session_state}")

    if role == "employee":
        from employee_ui import employee_ui
        employee_ui()

    elif role == "manager":
        from manager_ui import manager_ui
        manager_ui()

    elif role == "hr":
        from hr_ui import hr_ui
        hr_ui()

    else:
        st.error("Unknown role")
