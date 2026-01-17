# Source: HK Monetary Authority

import os
import pandas as pd
import re
import requests
import uuid
import warnings

BASE_ENDPOINT = "https://api.hkma.gov.hk/public/market-data-and-statistics/monthly-statistical-bulletin"
warnings.simplefilter(action='ignore', category=FutureWarning)

def get_data_note_bill(page=1, pagesize=200):
    endpoint = f"{BASE_ENDPOINT}/efbn/efbn-yield-daily"
    
    query_params = {
        "offset": (page-1) * pagesize,
        "pagesize": pagesize,
    }
    
    resp = requests.get(endpoint, params=query_params, timeout=15)
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

def convert_col_names(s):
    s = s.replace('efb', 'exchange_fund_bill').replace('efn', 'exchange_fund_note').replace('year', 'y')
    pattern = r"(\d+)yr"
    return re.sub(pattern, r"\1year_bond", s)


def main():
    output_file = os.path.join("./financial", "hk_exchange_fund_fi.csv")
    if os.path.exists(output_file) and False:
        df = pd.read_csv(output_file, index_col=0)
    else:
        df_notes = crawl_resource(get_data_note_bill, total_pages=10)
        df_bonds = crawl_resource(get_data_bonds, total_pages=10)
        
        if not df_notes.empty and not df_bonds.empty:
            combined_df = pd.merge(
                df_notes, 
                df_bonds, 
                on="end_of_day", 
            )
            df = combined_df.copy()
            combined_df.set_index("end_of_day", inplace=True)
            
        df = combined_df.copy()

    df.columns = [convert_col_names(col) for col in df.columns]
    
    df.reset_index(inplace=True)
    df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
    df.set_index('id', inplace=True)
    
    df.to_csv(output_file, index=True)

if __name__ == "__main__":
    main()