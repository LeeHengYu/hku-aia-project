from __future__ import annotations

import hmac
import os
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .vertex import generate_content

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    systemInstruction: str | None = None
    parameters: dict[str, Any] | None = None
    model: str | None = None

class ChatResponse(BaseModel):
    text: str


class TestResponse(BaseModel):
    text: str


app = FastAPI(title="Gemini Lite")
EXPECTED_AUTH_KEY = os.getenv("HKU_KEY_DEV", "").strip()

def _validate_auth_key(authorization: str | None) -> None:
    if not authorization: 
        return ""
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        candidate = ""
    else:
        candidate = token.strip()
    
    if not candidate:
        raise HTTPException(status_code=401, detail="Missing auth key.")
    if not EXPECTED_AUTH_KEY:
        raise HTTPException(status_code=500, detail="Server auth key is not configured.")
    if not hmac.compare_digest(candidate, EXPECTED_AUTH_KEY):
        raise HTTPException(status_code=403, detail="Invalid auth key.")

origins_env = os.getenv("CORS_ORIGINS", "")
if origins_env:
    allow_origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]
else:
    allow_origins = ["http://localhost:5173", "http://127.0.0.1:5173", "https://hku-aia-project.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    authorization: str | None = Header(default=None),
) -> ChatResponse:
    _validate_auth_key(authorization)
    try:
        text = generate_content(
            messages=[message.model_dump() for message in request.messages],
            system_instruction=request.systemInstruction,
        )
    except Exception as exc:  # pragma: no cover - surface external errors
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ChatResponse(text=text)


@app.post("/api/test", response_model=TestResponse)
async def test_endpoint(
    request: ChatRequest,
    authorization: str | None = Header(default=None),
) -> TestResponse:
    _validate_auth_key(authorization)
    content = request.messages[-1].content if request.messages else ""
    if content.strip().lower() == "hello":
        return TestResponse(text="Hi")
    return TestResponse(text="Unsupported test message")
