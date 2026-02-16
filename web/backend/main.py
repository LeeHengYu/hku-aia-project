from __future__ import annotations

import hmac
import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .vertex import generate_content, get_vertex_runtime_config

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    systemInstruction: str | None = None
    datastorePath: str | None = None
    parameters: dict[str, Any] | None = None

class ChatResponse(BaseModel):
    text: str


class TestResponse(BaseModel):
    text: str


EXPECTED_AUTH_KEY = os.getenv("HKU_KEY_DEV", "").strip()
LOGGER = logging.getLogger(__name__)

def _validate_auth_key(authorization: str | None) -> None:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing auth key.")

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

@asynccontextmanager
async def lifespan(_app: FastAPI):
    if not EXPECTED_AUTH_KEY:
        raise RuntimeError("Missing required environment variable: HKU_KEY_DEV")

    vertex_config = get_vertex_runtime_config()
    LOGGER.info(
        "Startup config loaded: cors_origins=%s, vertex_project=%s, "
        "vertex_location=%s, vertex_model=%s",
        allow_origins,
        vertex_config["project_id"],
        vertex_config["location"],
        vertex_config["model"],
    )
    yield


app = FastAPI(title="Gemini Lite", lifespan=lifespan)

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
    datastore_path = str(request.datastorePath or "").strip()

    if not datastore_path:
        raise HTTPException(status_code=400, detail="Missing datastorePath.")
    if not request.messages:
        raise HTTPException(status_code=400, detail="Missing messages.")

    try:
        text = generate_content(
            messages=[
                {"role": "model" if m.role == "assistant" else "user", "content": m.content}
                for m in request.messages if m.content.strip()
            ],
            system_instruction=request.systemInstruction,
            datastore_path=datastore_path,
        )
        
    except Exception as exc:
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
