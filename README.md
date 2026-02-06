# HKU AIA Project

This repository focuses on Phase 2. The current effort is to gather insurance-related information and insurance company financial reports (primarily PDFs) and prepare them for downstream indexing and analysis.

## Installation & Setup

Prerequisites:

- Python 3.11+
- `pip`

It is strongly recommended to use a virtual environment.

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

## Task 2 & 3 Documentation

1. Crawl data using Firecrawl

- Scope: product brochures, economic indicators, company financial reports, etc.
- Define a schema for Tasks 2 & 3 and output JSON
- Prepare a complete, detailed guide for Firecrawl Agent for crawling. Make use of LLM to refine the prompt.
- Parse the JSON to download files with `requests`, create temporary in-memory files, and upload directly to GCS buckets

2. Google Cloud Storage (GCS)

- Intermediate storage before indexing
- To download files, set up Google Cloud auth and use the script; direct browser downloads are clumsy because GCS paths do not render PDFs well

3. BigQuery (not used at the moment)

- For CSV data, structured ingestion requires a schema
- Auto-detected schemas default fields to NULLABLE
- Tables should be overwritten with `id` marked as REQUIRED

4. Vertex AI Data Stores

- Knowledge base for Tasks 2 & 3, data imported from GCS
- Structured and unstructured data cannot be mixed in one data store

5. Vertex AI Studio

- Testing playground
- The playground can only ground to one source (system limit is 10); use the script to enable grounding with data stores and Google Search simultaneously

## Long-Term Plan (To Be Researched)

Conversational agent (Vertex AI Agent Builder)

- aka Agentic RAG
- Add each data store and google search as a tool
- Define a playbook to instruct when to query each vector DB, with final decisions made by the LLM
