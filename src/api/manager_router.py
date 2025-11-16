from fastapi import APIRouter, Depends
from src.auth.jwt_service import get_current_user
from src.db.travel_queries import (
    fetch_manager_indents,
    fetch_manager_pending,
    fetch_manager_approved,
    approve_indent_manager,
    reject_manager_ticket
)

router = APIRouter(prefix="/manager", tags=["Manager"])


from fastapi import APIRouter, Depends
from src.auth.jwt_service import get_current_user
from src.db.travel_queries import fetch_manager_indents, fetch_employee_profile
from src.llm.client import chat

router = APIRouter(prefix="/manager", tags=["Manager"])



# -----------------------------
# 2️⃣ Manager chatbot
# -----------------------------
@router.post("/chat")
def manager_chat(prompt: str, user=Depends(get_current_user)):
    reply = chat(prompt)
    return {"reply": reply}


# -----------------------------
# 3️⃣ FULL EMPLOYEE PROFILE API
# -----------------------------
@router.get("/employee-profile/{employee_id}")
def get_employee_profile(employee_id: str, user=Depends(get_current_user)):
    profile = fetch_employee_profile(employee_id)
    return profile



@router.get("/indents")
def get_all_indents(user=Depends(get_current_user)):
    return fetch_manager_indents(user["employee_id"])


@router.get("/pending")
def get_pending(user=Depends(get_current_user)):
    return fetch_manager_pending(user["employee_id"])


@router.get("/approved")
def get_approved(user=Depends(get_current_user)):
    return fetch_manager_approved(user["employee_id"])


@router.post("/approve/{indent_id}")
def approve(indent_id: str, user=Depends(get_current_user)):
    approve_indent_manager(indent_id)
    return {"status": "approved", "indent_id": indent_id}

@router.post("/reject/{indent_id}")
def reject(indent_id: str, user=Depends(get_current_user)):
    reject_manager_ticket(indent_id)
    return {"status": "rejected", "indent_id": indent_id}
