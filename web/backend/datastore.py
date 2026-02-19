from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from google.cloud import datastore

_client: datastore.Client | None = None

CONVERSATION_KIND = "Conversation"

def get_client() -> datastore.Client:
    global _client
    if _client is None:
        project = os.getenv("VERTEX_PROJECT_ID", "").strip() or None
        _client = datastore.Client(project=project)
    return _client


def get_messages(chat_id: str) -> list[dict[str, Any]]:
    client = get_client()
    key = client.key(CONVERSATION_KIND, chat_id)
    entity = client.get(key)
    if entity is None:
        return []
    raw = entity.get("messages", "[]") # json string
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []


def save_messages(chat_id: str, messages: list[dict[str, Any]]) -> None:
    client = get_client()
    key = client.key(CONVERSATION_KIND, chat_id)
    entity = datastore.Entity(key=key, exclude_from_indexes=("messages",))
    entity["messages"] = json.dumps(messages)
    entity["updated_at"] = datetime.now(timezone.utc)
    client.put(entity)


def delete_conversation(chat_id: str) -> None:
    client = get_client()
    key = client.key(CONVERSATION_KIND, chat_id)
    client.delete(key)
