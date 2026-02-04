import argparse
import json
import os
import pprint
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import List, Optional

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

class Report(BaseModel):
    company_name: str = Field(description="The name of the company which published the report")
    report_year: int = Field(description="The fiscal year of the report is about. If not detectable, use publication year.")
    document_type: str = Field(description="The content nature of the report. E.g. Annual Report, Interim Report, Financial Supplement")
    source_url: str = Field()
    filename: str = Field(description="The suggested filename from the website. Use the original name if menaingful, else suggest one which can be inferred from the website where the report is found")

class ExtractSchema(BaseModel):
    reports: List[Report] = Field(description="List of reports")
    
extract_prompt = """
Extract the direct PDF links for annual financial reports and the URLs for financial supplements for Prudential PLC, AIA, BOCHK, AXA HK, Sun Life, FWD, and Generali from 2015 to the present. For each document found, capture the company_name, fiscal_year, document_type (e.g., Annual Report, Financial Supplement), direct_source_url, and filename.
"""

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-r", "--run", action="store_true", help="Start a new agent job")
    group.add_argument("-c", "--check", type=str, metavar="JOB_ID", help="Check status of a specific Job ID")
    
    args = parser.parse_args()
    
    if args.r: 
        agent_job = app.start_agent(
            prompt=extract_prompt,
            # urls=[],
            schema=ExtractSchema,
            model="spark-1-mini",
        )
    
        print(f"Job ID: {agent_job.id}")
        status = app.get_agent_status(agent_job.id)
        pprint(status)
        
    elif args.c:
        job_id = args.check
        status = app.get_agent_status(job_id)

        try:
            data = status.data
            pprint(data)
            
            filename = f"firecrawl/job-result/{job_id}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except:
            ...

if __name__=="__main__": 
    main()