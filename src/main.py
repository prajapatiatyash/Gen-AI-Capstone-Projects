# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from src.api.auth_router import router as auth_router
from src.api.employee_router import router as employee_router
from src.api.manager_router import router as manager_router
from src.api.hr_router import router as hr_router

app = FastAPI(title="Travel Indent System")

# ---------------------------
# CORS (if using Streamlit UI)
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Routers
# ---------------------------
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(employee_router, prefix="/employee", tags=["employee"])
app.include_router(manager_router, prefix="/manager", tags=["manager"])
app.include_router(hr_router, prefix="/hr", tags=["hr"])


@app.get("/")
def root():
    return {"message": "Travel Indent System API Running"}
