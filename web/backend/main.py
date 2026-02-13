from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
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
    authKey: str

class ChatResponse(BaseModel):
    text: str


class TestResponse(BaseModel):
    text: str


app = FastAPI(title="Gemini Lite")

origins_env = os.getenv("CORS_ORIGINS", "")
if origins_env:
    allow_origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]
else:
    allow_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

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
async def chat(request: ChatRequest) -> ChatResponse:
    if not request.authKey.strip():
        raise HTTPException(status_code=401, detail="Missing auth key.")
    try:
        text = generate_content(
            messages=[message.model_dump() for message in request.messages],
            system_instruction=request.systemInstruction,
        )
    except Exception as exc:  # pragma: no cover - surface external errors
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ChatResponse(text=text)


@app.post("/api/test", response_model=TestResponse)
async def test_endpoint(request: ChatRequest) -> TestResponse:
    content = request.messages[-1].content if request.messages else ""
    if content.strip().lower() == "hello":
        return TestResponse(text="Hi")
    return TestResponse(text="Unsupported test message")


_FRONTEND_DIST = os.getenv("FRONTEND_DIST")
if _FRONTEND_DIST and os.path.isdir(_FRONTEND_DIST):

    @app.get("/")
    async def serve_root() -> FileResponse:
        return FileResponse(os.path.join(_FRONTEND_DIST, "index.html"))

    @app.get("/{path:path}")
    async def serve_spa(path: str) -> FileResponse:
        if path.startswith("api/"):
            raise HTTPException(status_code=404)
        candidate = os.path.join(_FRONTEND_DIST, path)
        if os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(_FRONTEND_DIST, "index.html"))
