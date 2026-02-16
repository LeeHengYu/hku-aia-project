from __future__ import annotations

import os
from typing import Any

from google import genai
from google.genai.types import (
    GenerateContentConfig,
    GoogleSearch,
    HttpOptions,
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
DEFAULT_MODEL = "gemini-3-pro-preview"

client = genai.Client(
    http_options=HttpOptions(api_version="v1"),
    vertexai=True,
    project=VERTEX_PROJECT_ID,
    location=VERTEX_LOCATION,
)


def build_default_tools(path: str) -> list[Tool]:
    datastore_path = str(path or "").strip()
    if not datastore_path:
        raise ValueError("datastore_path is required.")

    google_search_tool = Tool(google_search=GoogleSearch())
    vertex_tool = Tool(
        retrieval=Retrieval(
            vertex_ai_search=VertexAISearch(datastore=datastore_path),
        ),
    )
    return [vertex_tool, google_search_tool]


def build_default_config(
    datastore_path: str,
    system_instruction: str | None = None,
) -> GenerateContentConfig:
    config_kwargs: dict[str, Any] = {"tools": build_default_tools(datastore_path)}
    instruction = str(system_instruction or "").strip()
    if instruction:
        config_kwargs["system_instruction"] = instruction
    return GenerateContentConfig(**config_kwargs)


def get_runtime_config() -> dict[str, str]:
    return {
        "project_id": VERTEX_PROJECT_ID,
        "location": VERTEX_LOCATION,
        "model": DEFAULT_MODEL,
    }


def send_to_gemini(
    contents: Any,
    datastore_path: str,
    system_instruction: str | None = None,
) -> str:
    path = str(datastore_path or "").strip()
    if not path:
        raise ValueError("datastore_path is required.")

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=contents,
        config=build_default_config(path, system_instruction),
    )
    return response.text
