import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"   # FastAPI backend

def call_api(endpoint: str, token: str, payload: dict = None, method: str = "POST"):
    """
    Utility helper for all API calls from Streamlit frontend.
    """

    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        if method.upper() == "POST":
            resp = requests.post(url, json=payload, headers=headers)
        elif method.upper() == "GET":
            resp = requests.get(url, headers=headers)
        else:
            return {"error": f"Unsupported method {method}"}

        # Try JSON
        try:
            return resp.json()
        except Exception:
            return {"error": "Invalid JSON response", "raw": resp.text}

    except Exception as e:
        return {"error": str(e)}
