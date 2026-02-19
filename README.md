# HKU AIA Project

This repository focuses on Phase 2. Most of the work has been finished.

## Installation & Setup

Prerequisites:

- Python 3.11+
- `pip`

It is strongly recommended to create a virtual environment.

Clone the repository:

```
git clone https://github.com/LeeHengYu/hku-aia-project.git
```

Create and activate a virtual environment, then install dependencies:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Local Packages

Some directories are packaged as installable Python modules (currently `insurers` and `firecrawl`). If you need to import them as packages or run their entry points, install the repository itself:

```
pip install -e .
```

## Task 2 & 3 Common Architecture

### Data

1. Firecrawl MCP server

    To be used in Agent tools such as Openclaw or Codex/Claude code which can invoke MCP endpoints.

2. File Download => GCS

    Download the file from given URLs and directly upload to GCS using a temporary in-memory object.

3. GCS => Vertex AI data stores

    Manual via console

### Testing Website

Link: https://hku-aia-project.vercel.app/

- Frontend: React Typescript

- Backend: FastAPI (Python)

- CI/CD: Vercel, Docker, Cloud Build, Google Cloud Run

- Database: Firestore (GCP)


## Long-Term Directions

- AI agent Crawling tool integration

- Prompt instructions refinement
    - including writing `AGENT.md`, `SKILL.md`

- Conversational agent (Vertex AI Agent Builder)
    - aka Agentic RAG
    - Add each data store and google search as a tool
    - Define a playbook to instruct when to query each vector DB, with final decisions made by the LLM
