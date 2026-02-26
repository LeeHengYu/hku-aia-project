from __future__ import annotations

import os
from typing import Any, Iterable

from google import genai
from google.genai.types import (
    Content,
    GenerateContentConfig,
    GoogleSearch,
    HttpOptions,
    Part,
    Retrieval,
    Tool,
    VertexAISearch,
)


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


VERTEX_PROJECT_ID = _required_env("VERTEX_PROJECT_ID")
VERTEX_LOCATION = _required_env("VERTEX_LOCATION")
DEFAULT_MODEL = "gemini-3.1-pro-preview"

client = genai.Client(
    http_options=HttpOptions(api_version="v1"),
    vertexai=True,
    project=VERTEX_PROJECT_ID,
    location=VERTEX_LOCATION,
)


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


def _build_tools(paths: list[str]) -> list[Tool]:
    vertex_tools = [
        Tool(retrieval=Retrieval(vertex_ai_search=VertexAISearch(datastore=path)))
        for path in paths
    ]
    return [*vertex_tools, Tool(google_search=GoogleSearch())]


def _build_config(
    datastore_paths: list[str],
    system_instruction: str | None = None,
) -> GenerateContentConfig:
    config_kwargs: dict[str, Any] = {"tools": _build_tools(datastore_paths)}
    instruction = str(system_instruction or "").strip()
    if instruction:
        config_kwargs["system_instruction"] = instruction
    return GenerateContentConfig(**config_kwargs)


def generate_content(
    messages: Iterable[dict[str, Any]],
    system_instruction: str | None = None,
    datastore_paths: list[str] | None = None,
) -> str:
    contents = _build_contents(messages)
    if not contents:
        return ""

    paths = [p.strip() for p in (datastore_paths or []) if p.strip()]
    if not paths:
        raise RuntimeError("Missing datastore paths.")

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=contents,
        config=_build_config(paths, system_instruction),
    )
    return response.text


def get_vertex_runtime_config() -> dict[str, str]:
    return {
        "project_id": VERTEX_PROJECT_ID,
        "location": VERTEX_LOCATION,
        "model": DEFAULT_MODEL,
    }
