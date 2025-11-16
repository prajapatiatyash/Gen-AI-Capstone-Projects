# src/api/hr_router.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.auth.jwt_service import get_current_user
from src.agents.hr_agent import HRAgent

router = APIRouter()
SESSION_STORE = {}

class ChatReq(BaseModel):
    message: str

@router.post("/chat")
def chat(req: ChatReq, current_user=Depends(get_current_user)):
    if current_user["role"] != "hr":
        raise HTTPException(status_code=403, detail="Not HR")
    agent = HRAgent(current_user, SESSION_STORE)
    return agent.handle_message(req.message)
