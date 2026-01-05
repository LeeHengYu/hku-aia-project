# Source: HK Monetary Authority

import re
import warnings
import requests
import pandas as pd
import os

BASE_ENDPOINT = "https://api.hkma.gov.hk/public/market-data-and-statistics/monthly-statistical-bulletin"
warnings.simplefilter(action='ignore', category=FutureWarning)

def get_data_note_bill(page=1, pagesize=200):
    endpoint = f"{BASE_ENDPOINT}/efbn/efbn-yield-daily"
    
    query_params = {
        "offset": (page-1) * pagesize,
        "pagesize": pagesize,
    }
    
    resp = requests.get(endpoint, params=query_params)
    resp.raise_for_status()

    data = resp.json().get('result', {}).get('records', [])
    df = drop_empty_columns(pd.DataFrame(data))
    
    return df

def get_data_bonds(page=1, pagesize=200):
    endpoint = f"{BASE_ENDPOINT}/gov-bond/instit-bond-price-yield-daily"
    
    query_params = {
        "segment": "OutstandYields",
        "offset": (page-1) * pagesize,
        "pagesize": pagesize,
    }
    
    resp = requests.get(endpoint, params=query_params)
    resp.raise_for_status()

    data = resp.json().get('result', {}).get('records', [])
    df = pd.DataFrame(data)    
    df.columns = [format_field(col) for col in df.columns]

    return df

def crawl_resource(fetcher, total_pages=3, pagesize=200):
    all_dfs = []
    for p in range(1, total_pages + 1):
        df = fetcher(page=p, pagesize=pagesize)
        
        df = df.loc[:, ~df.columns.duplicated()]
        all_dfs.append(df)

    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

def format_field(s):
    match = re.search(r'(\d+)gb(\d{4})', s.lower())
    
    if match:
        years = match.group(1)
        code = match.group(2)
        return f"{years}yr_{code}"

    return s

def drop_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(axis=1, how='all')

def main():
    output_dir = "./financial"
    output_file = os.path.join(output_dir, "hk_exchange_fund_fi.csv")
    
    os.makedirs(output_dir, exist_ok=True)

    df_notes = crawl_resource(get_data_note_bill, total_pages=10)
    df_bonds = crawl_resource(get_data_bonds, total_pages=10)
    
    if not df_notes.empty and not df_bonds.empty:
        combined_df = pd.merge(
            df_notes, 
            df_bonds, 
            on="end_of_day", 
            how="inner", 
        )    

    combined_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    main()