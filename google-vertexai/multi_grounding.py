from google import genai
from google.genai.types import (
    GenerateContentConfig,
    GoogleSearch,
    HttpOptions,
    Retrieval,
    Tool,
    VertexAISearch,
)

DEFAULT_MODEL = "gemini-3-pro-preview"
DATASTORE_PATH = "projects/project-b8819359-0bf9-4214-88d/locations/global/collections/default_collection/dataStores/hku-market-analysis_1769864742906"

client = genai.Client(http_options=HttpOptions(api_version="v1"), vertexai=True)


def build_default_tools(path):
    google_search_tool = Tool(google_search=GoogleSearch())
    vertex_tool = Tool(
        retrieval=Retrieval(
            vertex_ai_search=VertexAISearch(datastore=path),
        ),
    )
    return [vertex_tool, google_search_tool]


def build_default_config():
    return GenerateContentConfig(tools=build_default_tools(DATASTORE_PATH))


def generate_content(contents, model=None, config=None):
    response = client.models.generate_content(
        model=model or DEFAULT_MODEL,
        contents=contents,
        config=config or build_default_config(),
    )
    return response.text


if __name__ == "__main__":
    response_text = generate_content(
        contents=(
            "How was the performance of AIA as a company in 2025 H1? "
            "Please list out the sources from which you gather information."
        )
    )
    print(response_text)
