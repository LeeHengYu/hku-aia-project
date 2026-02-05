from google import genai
from google.genai.types import (
    GenerateContentConfig,
    GoogleSearch,
    HttpOptions,
    Retrieval,
    Tool,
    VertexAISearch,
)

client = genai.Client(http_options=HttpOptions(api_version="v1"), vertexai=True)
DATASTORE_PATH = "projects/project-b8819359-0bf9-4214-88d/locations/global/collections/default_collection/dataStores/hku-market-analysis_1769864742906"

googleSearchTool = Tool(
    google_search=GoogleSearch()
)

tool = Tool(
    retrieval=Retrieval(
        vertex_ai_search=VertexAISearch(
            datastore=DATASTORE_PATH
        )
    )
)

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="How was the performance of AIA as a company in 2025 H1? Please list out the sources from which you gather information.",
    config=GenerateContentConfig(
        tools=[
            tool, googleSearchTool
        ],
    ),
)

print(response.text)
