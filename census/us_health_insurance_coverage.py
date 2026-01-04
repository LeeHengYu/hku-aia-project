import argparse
import pandas as pd
import requests

def fetch_census_data(group_code):
    url = f"https://api.census.gov/data/2024/acs/acs1/subject?get=group({group_code})&ucgid=0100000US"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data[1:], columns=data[0])
    except:
        return None

def main():
    help_text = """
    S2701: Selected characteristics of health insurance coverage
    S2702: Same as above but uninsured
    S2703: Private health insurance by type and selected characteristics
    S2704: Public health insurance by type and selected characteristics
    B27001: Health Insurance Coverage Status by Sex by Age
    """
    
    parser = argparse.ArgumentParser(epilog=help_text, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-g", "--group", required=True)
    args = parser.parse_args()
    
    df = fetch_census_data(args.group)
    if df is not None:
        print(df)

if __name__ == "__main__":
    main()