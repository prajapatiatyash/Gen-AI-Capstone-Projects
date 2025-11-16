import streamlit as st
import requests

FASTAPI_URL = "http://127.0.0.1:8000"

def show_login():
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        resp = requests.post(
            f"{FASTAPI_URL}/auth/token",
            data={"username": email, "password": password}
        )

        if resp.status_code == 200:
            data = resp.json()
            st.session_state["token"] = data["access_token"]
            st.session_state["employee_id"] = data["employee_id"]
            st.session_state["role"] = data["role"]
            st.rerun()
        else:
            st.error("Invalid credentials")
