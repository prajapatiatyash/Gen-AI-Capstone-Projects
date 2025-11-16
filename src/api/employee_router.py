# src/api/employee_router.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.auth.jwt_service import get_current_user
from src.agents.employee_agent import EmployeeAgent

router = APIRouter()
# In-memory session store (demo). Replace with Redis in prod.
SESSION_STORE = {}

class ChatReq(BaseModel):
    message: str

@router.post("/chat")
def chat(req: ChatReq, current_user=Depends(get_current_user)):
    if current_user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Not an employee")
    agent = EmployeeAgent(current_user, SESSION_STORE)
    res = agent.handle_message(req.message)
    return res

@router.post("/confirm")
def confirm(current_user=Depends(get_current_user)):
    if current_user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Not an employee")
    # Agent will look into session for pending intent and create indent
    agent = EmployeeAgent(current_user, SESSION_STORE)
    res = agent.handle_message("confirm")
    return res
