# src/api/auth_router.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.jwt_service import (
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter()

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Username = email
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # JWT payload
    access_token = create_access_token(
        data={"sub": user["employee_id"], "role": user["role"]}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "employee_id": user["employee_id"],
        "role": user["role"],
        "name": user["name"]
    }
