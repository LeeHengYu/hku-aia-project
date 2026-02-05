import argparse
import json
import os
from pprint import pprint
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import List

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

class Report(BaseModel):
    company_name: str = Field(description="The name of the company which published the report")
    report_year: int = Field(description="The fiscal year of the report is about. If not detectable, use publication year.")
    document_type: str = Field(description="The content nature of the report. E.g. Annual Report, Interim Report, Financial Supplement")
    source_url: str = Field(description="The file url which users, upon clicking a link in a browser, can download the report.")
    filename: str = Field(description="The suggested filename from the website. Use the original name if meaningful, else suggest one which can be inferred from the website where the report is found")

class ExtractSchema(BaseModel):
    reports: List[Report] = Field(description="List of reports")
    
extract_prompt = """
Task: For Prudential PLC, AIA, BOCHK (Bank of China Hong Kong), AXA HK, Sun Life, FWD, Generali and other insurance companies in Hong Kong, find annual financial reports (PDF) and financial supplements from 2015 to present.

Rules:
- Annual reports: return the direct PDF URL (not a landing page).
- Financial supplements: return the direct PDF URL if available; otherwise the URL to the resource file, do not give landing page URL.
- Use these field names exactly: company_name, report_year, document_type, source_url, filename.
- document_type must be "Annual Report", "Financial Supplement" or of similar patterns.
- report_year is the fiscal year covered by the document. If unclear, use the publication year.
- filename should be the original file name if visible; otherwise synthesize: {company_name}_{report_year}_{document_type}.pdf or .html.
- Please find the links which user can access to download the file, and store it as {source_url}.
- Prefer English versions if multiple languages are available.
- Avoid duplicates (one entry per unique document).

Return only the extracted data that matches the schema.
"""

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-r", "--run", action="store_true", help="Start a new agent job")
    group.add_argument("-c", "--check", type=str, metavar="JOB_ID", help="Check status of a specific Job ID")
    
    args = parser.parse_args()
    
    if args.run: 
        agent_job = app.start_agent(
            prompt=extract_prompt,
            schema=ExtractSchema,
            model="spark-1-mini",
        )
    
        print(f"Job ID: {agent_job.id}")
        status = app.get_agent_status(agent_job.id)
        pprint(status)
        
    elif args.check:
        job_id = args.check
        status = app.get_agent_status(job_id)

        try:
            data = status.data
            if data is not None:
                pprint(data)
                
                filename = f"firecrawl/{job_id[:12]}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
            else:
                pprint(status)
        
        except Exception as exc:
            print(f"Failed to read or write job data: {exc}")

if __name__=="__main__": 
    main()
