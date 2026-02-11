from __future__ import annotations

import importlib.util
import pathlib
from typing import Any, Iterable

_BASE_DIR = pathlib.Path(__file__).resolve().parents[2]
_MULTI_GROUNDING_PATH = _BASE_DIR / "google-vertexai" / "multi_grounding.py"


def _load_multi_grounding_module():
    spec = importlib.util.spec_from_file_location(
        "multi_grounding", str(_MULTI_GROUNDING_PATH)
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load multi_grounding.py module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build_contents(
    messages: Iterable[dict[str, Any]],
    system_instruction: str | None,
) -> list[dict[str, Any]]:
    contents: list[dict[str, Any]] = []

    if system_instruction:
        instruction = system_instruction.strip()
        if instruction:
            contents.append(
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": "[System Instruction]\n"
                            + instruction
                            + "\n[/System Instruction]",
                        }
                    ],
                }
            )

    for message in messages:
        role = message.get("role")
        if role == "assistant":
            role = "model"
        if role not in {"user", "model"}:
            continue
        text = str(message.get("content", "")).strip()
        if not text:
            continue
        contents.append({"role": role, "parts": [{"text": text}]})

    return contents


def generate_content(
    messages: Iterable[dict[str, Any]],
    system_instruction: str | None = None,
) -> str:
    contents = _build_contents(messages, system_instruction)
    if not contents:
        return ""

    multi_grounding = _load_multi_grounding_module()
    return multi_grounding.generate_content(contents=contents)
