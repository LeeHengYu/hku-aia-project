import os
import pathlib
import sys

try:
    from web.backend.vertex_grounding import (
        build_default_config,
        build_default_tools,
        generate_content,
        get_runtime_config,
    )
except ModuleNotFoundError:
    ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(ROOT_DIR))
    from web.backend.vertex_grounding import (
        build_default_config,
        build_default_tools,
        generate_content,
        get_runtime_config,
    )

__all__ = [
    "build_default_config",
    "build_default_tools",
    "generate_content",
    "get_runtime_config",
]


if __name__ == "__main__":
    path = os.getenv("VERTEX_DATASTORE_PATH", "").strip()
    if not path:
        raise RuntimeError("Set VERTEX_DATASTORE_PATH for local script execution.")

    response_text = generate_content(
        datastore_path=path,
        contents=(
            "How was the performance of AIA as a company in 2025 H1? "
            "Please list out the sources from which you gather information."
        )
    )
    print(response_text)
