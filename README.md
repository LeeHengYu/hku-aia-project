# HKU AIA project

Only about phase 2. In the first step we try to gather information relevant to insurance and insurance companies' financial reports, these files are in PDF formats.

# Installation & Setup

It is recommended to install Python3.11 or above and `pip` for downloading required packages. It is STRONGLY RECOMMENDED to create a virtual environment for this project.

To download all required files from this repo, run

```
git clone https://github.com/LeeHengYu/hku-aia-project.git
```

If you have `python3` installed on your machine, run the following:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Task 2 & 3: Automation Roadmap

- AI Agent crawler by Firecrawl: Schema provision, more structured output such as JSON or CSV.
  - The prompt or scope of search (webistes) can be prepared by other LLM, or through Firecrawl UI.

- File download script deployment
- GCS to Data Stores
- Multi-source grounding cannot be done through AI Studio, richtext display

## Long term plan (to be researched)

Conversational agent (part of Vertex AI agent builder)

- aka Agentic RAG
- Add each data store and google search as a tool
- Define a playbook, instruct when to look for which vector DB, but ultimately determined by the LLM.
