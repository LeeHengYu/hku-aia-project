import json
from typing import Any, Mapping, Optional


def build_blob_path(name: str, prefix: Optional[str] = None) -> str:
    clean_name = str(name).lstrip("/").replace("\\", "/")
    if prefix is None or prefix == "":
        return clean_name
    clean_prefix = str(prefix).strip("/").replace("\\", "/")
    if clean_prefix == "":
        return clean_name
    return f"{clean_prefix}/{clean_name}"


def emit_result(result: Mapping[str, Any]) -> None:
    print(json.dumps(dict(result), ensure_ascii=False))
