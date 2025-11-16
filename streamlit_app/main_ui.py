# streamlit_app/main_ui.py
import streamlit as st
import requests

API_BASE = st.sidebar.text_input("API Base", "http://localhost:8000")

def login():
    st.header("Login")
    employee_id = st.text_input("Employee ID")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # OAuth2PasswordRequestForm expects form fields: username, password
        resp = requests.post(f"{API_BASE}/auth/token", data={"username": employee_id, "password": password})
        if resp.status_code == 200:
            data = resp.json()
            st.session_state["token"] = data["access_token"]
            st.session_state["employee_id"] = data["employee_id"]
            st.session_state["role"] = data["role"]
            st.session_state["name"] = data["name"]
            st.success(f"Logged in as {data['name']} ({data['role']})")
            st.experimental_rerun()
        else:
            st.error(f"Login failed: {resp.text}")

def call_api(path, json=None):
    headers = {}
    if "token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state['token']}"
    try:
        r = requests.post(f"{API_BASE}{path}", json=json, headers=headers)
        return r
    except Exception as e:
        st.error(f"API request failed: {e}")
        return None

def employee_page():
    st.header("Employee Chat")
    st.write(f"Welcome {st.session_state.get('name')}")
    msg = st.text_input("Message", "I want to travel from Indore to Hyderabad on 2025-11-20 for client meeting")
    if st.button("Send"):
        r = call_api("/employee/chat", json={"message": msg})
        if r:
            st.write("Status:", r.status_code)
            try:
                st.json(r.json())
            except Exception:
                st.text(r.text)
    if st.button("Confirm ticket"):
        r = call_api("/employee/confirm")
        if r:
            try:
                st.json(r.json())
            except:
                st.text(r.text)

def manager_page():
    st.header("Manager Chat")
    st.write(f"Hi {st.session_state.get('name')}")
    msg = st.text_input("Message", "list pending")
    if st.button("Send (Manager)"):
        r = call_api("/manager/chat", json={"message": msg})
        if r:
            try:
                st.json(r.json())
            except:
                st.text(r.text)

def hr_page():
    st.header("HR Chat")
    st.write(f"Hi {st.session_state.get('name')}")
    msg = st.text_input("Message", "list pending")
    if st.button("Send (HR)"):
        r = call_api("/hr/chat", json={"message": msg})
        if r:
            try:
                st.json(r.json())
            except:
                st.text(r.text)

def main():
    st.sidebar.title("Travel Agent Demo")
    if "token" not in st.session_state:
        login()
    else:
        role = st.session_state.get("role")
        st.sidebar.write(f"Logged in: {st.session_state.get('name')} ({role})")
        if st.sidebar.button("Logout"):
            for k in ["token","employee_id","role","name"]:
                st.session_state.pop(k, None)
            st.experimental_rerun()
        if role == "employee":
            employee_page()
        elif role == "manager":
            manager_page()
        elif role == "hr":
            hr_page()
        else:
            st.write("Unknown role. Contact admin.")

if __name__ == "__main__":
    main()
