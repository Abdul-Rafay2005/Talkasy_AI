# backend/main.py
import os
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Dict

# Google Gemini
import google.generativeai as genai

# local helpers
from db import init_db, create_user, get_user_by_username
from auth_utils import hash_password, verify_password, create_jwt_token, decode_jwt_token

load_dotenv()

# Init DB
init_db()

app = FastAPI(title="Gemini Chat (Python)")

# Configure CORS
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:5500")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []  # [{role: "user"|"ai", content: "..."}]


# Helper: get current user from Authorization header
def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth.split(" ", 1)[1]
    payload = decode_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload["sub"]


# Gemini API call
def call_gemini_api(message: str, history: List[Dict]) -> str:
    GEMINI_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    if not GEMINI_KEY:
        # fallback for local testing
        return f"[Mock] Gemini offline. You asked: \"{message}\""

    # Configure SDK
    genai.configure(api_key=GEMINI_KEY)

    # Choose model
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Format history
    formatted_history = []
    for h in history:
        role = "user" if h["role"] == "user" else "model"
        formatted_history.append({"role": role, "parts": [h["content"]]})

    # Add the latest user message
    formatted_history.append({"role": "user", "parts": [message]})

    # Generate response
    try:
        resp = model.generate_content(formatted_history)
        return resp.text or "No response from Gemini"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e}")


@app.post("/api/register")
def register(req: RegisterRequest):
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="username and password required")
    username = req.username.strip().lower()
    if get_user_by_username(username):
        raise HTTPException(status_code=400, detail="username already taken")
    pwd_hash = hash_password(req.password)
    ok = create_user(username, pwd_hash)
    if not ok:
        raise HTTPException(status_code=500, detail="could not create user")
    return {"ok": True, "message": "user created"}


@app.post("/api/login")
def login(req: LoginRequest):
    user = get_user_by_username(req.username.strip().lower())
    if not user:
        raise HTTPException(status_code=400, detail="invalid credentials")
    if not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="invalid credentials")
    token = create_jwt_token(user["username"])
    return {"access_token": token}


@app.post("/api/chat")
def chat(req: ChatRequest, username: str = Depends(get_current_user)):
    if not req.message or not isinstance(req.message, str):
        raise HTTPException(status_code=400, detail="message is required")
    reply = call_gemini_api(req.message, req.history)
    return {"answer": reply}


@app.get("/api/health")
def health():
    return {"ok": True}
