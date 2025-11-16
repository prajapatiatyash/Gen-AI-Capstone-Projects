import streamlit as st
import requests

FASTAPI_URL = "http://127.0.0.1:8000"

def employee_ui():
    st.title("👨‍💼 Employee Assistant")

    msg = st.text_input("Ask something:")
    if st.button("Send"):
        resp = requests.post(
            f"{FASTAPI_URL}/employee/chat",
            json={"message": msg},
            headers={"Authorization": f"Bearer {st.session_state['token']}"}
        )
        data = resp.json()
        if "ask" in data:
            st.warning(data["ask"])
        elif "message" in data:
            st.success(data["message"])
        elif "intent" in data:
            st.info(f"Intent: {data['intent']}")
            st.write("Flights:", data.get("flights", []))
            st.write("Hotels:", data.get("hotels", []))
        else:
            st.write(data)