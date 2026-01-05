from bs4 import BeautifulSoup
import requests
import sys
import os

from urllib.parse import urljoin, unquote

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from insurers.download_file import download_file_from_url

def find_statements():
    url = "https://www.aia.com/en/investor-relations/overview/results-presentations"
    kws = ['supplement', 'announcement']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        buttons = soup.find_all('div', class_='ctabutton')
        
        for div in buttons:
            a_tags = div.find_all('a')
            for a in a_tags:
                if 'href' in a.attrs: 
                    link_text = a.get_text(strip=True)
                    if not link_text:
                        continue
                        
                    link = urljoin(url, a['href'])
                    
                    if any(kw in link_text.lower() for kw in kws):
                        filename = unquote(link.split('/')[-1])
                        cur_wd = os.getcwd() + '/financial_statements/data'
                        os.makedirs(cur_wd, exist_ok=True)
                        download_file_from_url(link, f"{cur_wd}/{filename}")
                        
    except requests.RequestException as e:
        print(f"Network error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    find_statements()

if __name__ == "__main__":
    main()