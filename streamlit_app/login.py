import streamlit as st
import requests

def login_ui():
    st.title("🔐 Employee Login")

    emp_id = st.text_input("Employee ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = requests.post(
            "http://localhost:8000/auth/token",
            data={"username": emp_id, "password": password}
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "token": data["access_token"],
                "role": data["role"],
                "employee_id": data["employee_id"]
            }
        else:
            st.error("Invalid credentials")

    return None
