# HKU AIA project

Only about phase 2. AIA mainly cares about medical and health insurance products, so, in the first step we try to gather information relevant to health/medical.

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

# Task 2: Data crawling

### Census data

- [x] HK Census and Stat department
- [ ] US Census (API always broken)

### Financial (stocks and bonds)

- [ ] HK Stock (FUTU API needs auth setup with FUTU HK account)
- [ ] US Stock
- [x] HK Bond Yield
- [x] US Bond Yield

### Financial Statements / Reports

- [x] AIA Group
- [x] FWD
- [x] Prudential
- [ ] Manulife

### Insurance brochures

- [x] AIA Group
- [x] FWD
- [x] Prudential
- [x] Manulife

### Medical

- [x] CHP
- [ ] Hospital Authority

# Task 3: AI & GCP

## Resolve CSV import problem

- In the metadata, an `id` field set as REQUIRED is needed
- BigQuery is used as a bridge to import data into data stores, but auto-detection schema in BigQuery cannot set `id` to REQUIRED, nor can Google SQL => switch to SDK sol to prepare the schema ourselves. Can rely on Gemini to generate the schema (in Python code form)
- The final csv data is imported from BigQuery to data stores for grounding

## Test programmatic grounding with multiple sources (data stores + Google Search)

- Cannot configure in console UI
- Can test with SDK, unlikely to work though the param is `List[Tool]`

## Long term plan

Conversational agent (part of Vertex AI agent builder)

- aka Agentic RAG
- Add each data store and google search as a tool
- Define a playbook, instruct when to look for which vector DB, but ultimately determined by the LLM.
