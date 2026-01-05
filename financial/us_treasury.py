# Source: US Fiscal Data

import os
import pandas as pd
import requests

def get_endpoint(page_num=1, page_size=100):
    base_url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates"
    
    url = f"{base_url}?sort=-record_date&format=json&page[number]={page_num}&page[size]={page_size}"
    
    return url

def get_data(url):
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json().get('data', [])
    
    df = pd.DataFrame(data)
    numerical_cols = set(df.columns[3:])
    for col in df.columns: 
        if col in numerical_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        if col == 'record_date':
            df[col] = pd.to_datetime(df[col])
    
    return df

def crawl_pages(num_pages=3, page_size=100):
    all_frames = []
    
    for p in range(1, num_pages + 1):
        url = get_endpoint(page_num=p, page_size=page_size)
        df = get_data(url)
        if not df.empty:
            all_frames.append(df)
    
    if all_frames:
        return pd.concat(all_frames, ignore_index=True)
    return pd.DataFrame()

if __name__ == "__main__":
    os.makedirs('./financial', exist_ok=True)
    df = crawl_pages(num_pages=20)
    if not df.empty:
        df.to_csv('./financial/us_treasury_yield.csv', index=False)