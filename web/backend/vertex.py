from __future__ import annotations

from typing import Any, Iterable

from google.genai.types import Content, Part

from .vertex_grounding import (
    get_runtime_config,
    send_to_gemini,
)


def get_vertex_runtime_config() -> dict[str, str]:
    return get_runtime_config()


def _build_contents(
    messages: Iterable[dict[str, Any]],
) -> list[Content]:
    contents: list[Content] = []

    for message in messages:
        role = message.get("role")
        if role == "assistant":
            role = "model"
        if role not in {"user", "model"}:
            continue
        text = str(message.get("content", "")).strip()
        if not text:
            continue
        contents.append(Content(role=role, parts=[Part.from_text(text=text)]))

    return contents


def generate_content(
    messages: Iterable[dict[str, Any]],
    system_instruction: str | None = None,
    datastore_path: str | None = None,
) -> str:
    contents = _build_contents(messages)
    if not contents:
        return ""

    path = str(datastore_path or "").strip()
    if not path:
        raise RuntimeError("Missing datastore path.")

    return send_to_gemini(
        contents=contents,
        datastore_path=path,
        system_instruction=system_instruction,
    )
