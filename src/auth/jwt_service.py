# src/auth/jwt_service.py
import os
import yaml
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
import bcrypt

from src.db.connection import get_db_conn

_auth_cfg_path = os.getenv("AUTH_CONFIG_PATH", "config/auth.yaml")
try:
    with open(_auth_cfg_path) as f:
        _cfg = yaml.safe_load(f)
except FileNotFoundError:
    _cfg = {}

SECRET_KEY = os.getenv("SECRET_KEY", _cfg.get("secret_key", "CHANGE_THIS_SECRET"))
ALGORITHM = _cfg.get("algorithm", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",
                                            _cfg.get("access_token_expire_minutes", 60)))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# -----------------------------------------------------
# FIXED → can search user by email OR employee_id
# -----------------------------------------------------
def get_user_by_identifier(identifier: str):
    print("Fetching user by identifier:", identifier)

    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT employee_id, name, email, password_hash, grade, role, is_active
            FROM users
            WHERE email = %s OR employee_id = %s
        """, (identifier, identifier))
        row = cur.fetchone()
        cur.close()

    if not row:
        return None

    return {
        "employee_id": row[0],
        "name": row[1],
        "email": row[2],
        "password_hash": row[3],
        "grade": row[4],
        "role": row[5],
        "is_active": row[6],
    }


# -----------------------------------------------------
# AUTH HELPERS
# -----------------------------------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    expire = (datetime.now(timezone.utc) +
              (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)))

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(identifier: str, password: str):
    rec = get_user_by_identifier(identifier)
    if not rec:
        return None

    if not rec["password_hash"]:
        return None

    if not verify_password(password, rec["password_hash"]):
        return None

    return {
        "employee_id": rec["employee_id"],
        "name": rec["name"],
        "email": rec["email"],
        "grade": rec["grade"],
        "role": rec["role"],
        "is_active": rec["is_active"]
    }


def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials")


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)

    identifier = payload.get("sub")
    if not identifier:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = get_user_by_identifier(identifier)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user["is_active"]:
        raise HTTPException(status_code=400, detail="Inactive user")

    return {
        "employee_id": user["employee_id"],
        "name": user["name"],
        "email": user["email"],
        "grade": user["grade"],
        "role": user["role"],
    }
