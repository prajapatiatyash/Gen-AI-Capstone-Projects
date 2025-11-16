# src/api/employee_router.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.auth.jwt_service import get_current_user
from src.agents.employee_agent import EmployeeAgent
from datetime import date
from typing import Literal
from src.db.travel_queries import (create_travel_indent_from_form,get_employee_travel_indents,get_employee_details)
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
class TravelIndentCreate(BaseModel):
    purpose_of_booking: str
    travel_type: Literal["domestic", "international"]
    travel_start_date: date
    travel_end_date: date
    from_city: str
    from_country: str
    to_city: str
    to_country: str
@router.post("/create-indent")
def create_indent(
    req: TravelIndentCreate,
    current_user=Depends(get_current_user),
):
    if current_user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Not an employee")

    new_indent_id = create_travel_indent_from_form(
        employee_id=current_user["employee_id"],
        purpose_of_booking=req.purpose_of_booking,
        travel_type=req.travel_type,
        travel_start_date=req.travel_start_date,
        travel_end_date=req.travel_end_date,
        from_city=req.from_city,
        from_country=req.from_country,
        to_city=req.to_city,
        to_country=req.to_country,
    )

    return {
        "message": "Travel ticket created successfully.",
        "indent_id": new_indent_id,
    }
@router.get("/my-indents")
def list_my_indents(current_user=Depends(get_current_user)):
    if current_user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Not an employee")

    tickets = get_employee_travel_indents(current_user["employee_id"])
    return {"items": tickets}
@router.get("/profile")
def profile(current_user=Depends(get_current_user)):
    if current_user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Not an employee")

    emp_id = current_user["employee_id"]
    details = get_employee_details(emp_id)
    if not details:
        raise HTTPException(status_code=404, detail="Employee profile not found")

    return details
