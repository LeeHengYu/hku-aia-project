from __future__ import annotations

import hmac
import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .datastore import delete_conversation, get_messages, save_messages
from .vertex import generate_content, get_vertex_runtime_config


class ChatRequest(BaseModel):
    chatId: str
    message: str
    systemInstruction: str | None = None
    datastorePath: str | None = None
    parameters: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    text: str


class TestResponse(BaseModel):
    text: str


EXPECTED_AUTH_KEY = os.getenv("HKU_KEY_DEV", "").strip()
LOGGER = logging.getLogger(__name__)

async def require_auth(authorization: str | None = Header(default=None)) -> None:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing auth key.")

    scheme, _, token = authorization.partition(" ")
    candidate = token.strip() if scheme.lower() == "bearer" else ""

    if not candidate:
        raise HTTPException(status_code=401, detail="Missing auth key.")
    if not EXPECTED_AUTH_KEY:
        raise HTTPException(status_code=500, detail="Server auth key is not configured.")
    if not hmac.compare_digest(candidate.encode(), EXPECTED_AUTH_KEY.encode()):
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


@app.get("/api/conversations/{chat_id}/messages")
async def get_conversation_messages(
    chat_id: str,
    _: Annotated[None, Depends(require_auth)],
) -> list[dict[str, Any]]:
    return get_messages(chat_id)


@app.post("/api/conversations/{chat_id}/messages")
async def post_conversation_messages(
    chat_id: str,
    messages: list[dict[str, Any]],
    _: Annotated[None, Depends(require_auth)],
) -> dict[str, str]:
    save_messages(chat_id, messages)
    return {"status": "ok"}


@app.delete("/api/conversations/{chat_id}")
async def delete_conversation_endpoint(
    chat_id: str,
    _: Annotated[None, Depends(require_auth)],
) -> dict[str, str]:
    delete_conversation(chat_id)
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    _: Annotated[None, Depends(require_auth)],
) -> ChatResponse:
    datastore_path = str(request.datastorePath or "").strip()

    if not datastore_path:
        raise HTTPException(status_code=400, detail="Missing datastorePath.")
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Missing message.")

    now = datetime.now(timezone.utc).isoformat()

    messages = get_messages(request.chatId)

    user_msg = {
        "id": str(uuid.uuid4()),
        "role": "user",
        "content": request.message.strip(),
        "createdAt": now,
    }
    messages.append(user_msg)

    try:
        text = generate_content(
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in messages if m.get("content", "").strip()
            ],
            system_instruction=request.systemInstruction,
            datastore_path=datastore_path,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    assistant_msg = {
        "id": str(uuid.uuid4()),
        "role": "model",
        "content": text.strip() if text else "No response generated.",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    messages.append(assistant_msg)

    save_messages(request.chatId, messages)

    return ChatResponse(text=assistant_msg["content"])


@app.post("/api/test", response_model=TestResponse)
async def test_endpoint(
    _: Annotated[None, Depends(require_auth)],
) -> TestResponse:
    return TestResponse(text="ok")
