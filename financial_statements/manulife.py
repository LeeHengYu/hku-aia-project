# All HK related press release/reports/financial statements

import os

from playwright.sync_api import sync_playwright
from urllib.parse import urljoin

URL = "https://www.manulife.com.hk/en/individual/about/newsroom.html"

def download_file_with_playwright(page, url, save_path):
    try:
        response = page.request.get(url, timeout=60000)
        if response.status == 200:
            content = response.body()
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(content)
            return True
        else:
            return False
    except Exception as e:
        return False

def scrape_manulife_newsroom(page):
    try:
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        elements = page.locator("a.dl-link").all() # no filtering logics 
        
        links = []
        for element in elements:
            links.append(element.get_attribute("href")) 
        
        return links
    except Exception as e:
        return print(e)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        news_links = scrape_manulife_newsroom(page)
        
        for link in news_links:
            download_file_with_playwright(page, urljoin(URL, link), f'financial_statements/reports/{os.path.basename(link)}')
            
        browser.close()

if __name__ == "__main__":
    main()
