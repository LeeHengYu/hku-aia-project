import re
from playwright.sync_api import sync_playwright, Locator
import sys
import os
from urllib.parse import urljoin, unquote

# Add parent directory to path to import insurers module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from insurers.download_file import create_folder_if_not_exist, download_file_from_url

URL = "https://www.fwd.com/en/investors/results-and-reports/"

def scan_page():
    kws = [
        'actuarial',
        'announcement',
        'annual report',
        'business highlights',
        'results presentation',
        'financial supplement',
    ]
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            page.goto(URL, wait_until="networkidle", timeout=15000)
            expand_buttons_locator = page.locator('div[role="button"]').filter(has_text=re.compile(r'^\s*\d+\s*$'))
            
            for i in range(expand_buttons_locator.count()):
                expand_buttons_locator.nth(i).click(force=True)
                page.wait_for_timeout(1000)
            
            links = page.locator('a').all() 
            
            save_dir = os.path.join(os.getcwd(), 'financial_statements', 'data')
            create_folder_if_not_exist(save_dir)
            
            for link in links: 
                href = link.get_attribute('href')
                inner = link.inner_text().lower().strip()
                if not href or not href.endswith((".pdf", ".xlsx", ".xls")):
                    continue # check file format
                if not any(kw in inner for kw in kws):
                    continue # check keyword
                    
                filename = href.strip().split('/')[-1].replace('_Group_Holdings_Limited', '')
                dest_path = os.path.join(save_dir, filename)
                download_file_from_url(urljoin(URL, href), dest_path)
                # print("Found:", filename)
            
            browser.close()
            
    except Exception as e:
        print(f"[!] An error occurred: {e}")

def main():
    scan_page()

if __name__ == "__main__":
    main()
