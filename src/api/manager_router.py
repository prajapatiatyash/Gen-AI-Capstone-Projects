# src/api/manager_router.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.auth.jwt_service import get_current_user
from src.agents.manager_agent import ManagerAgent

router = APIRouter()
SESSION_STORE = {}  # share same store if you prefer; for demo it's separate

class ChatReq(BaseModel):
    message: str

@router.post("/chat")
def chat(req: ChatReq, current_user=Depends(get_current_user)):
    if current_user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Not a manager")
    agent = ManagerAgent(current_user, SESSION_STORE)
    return agent.handle_message(req.message)
