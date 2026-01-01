import os
import requests
from playwright.sync_api import sync_playwright

MEDICAL_INSURANCE = "https://www.censtatd.gov.hk/en/EIndexbySubject.html?pcode=C0000056&scode=380"
OUTPUT_DIR = "./census/data"

def download_census_data():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    hrefs = []
    cookies = []
    user_agent = ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"Navigating to {MEDICAL_INSURANCE}...")
        try:
            page.goto(MEDICAL_INSURANCE, wait_until='networkidle')
            
            # Extract Cookies and User Agent
            cookies = context.cookies()
            user_agent = page.evaluate("navigator.userAgent")
            
            # Extract absolute URLs for Excel files
            # Using JS execution to get the 'href' property ensures we get absolute URLs
            hrefs = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a'))
                    .map(a => a.href)
                    .filter(href => href.toLowerCase().endsWith('.xls') || href.toLowerCase().endsWith('.xlsx'));
            }""")
            
            print(f"Found {len(hrefs)} Excel links.")
            
        except Exception as e:
            print(f"Error during Playwright execution: {e}")
        finally:
            browser.close()

    # Prepare requests session with captured credentials
    session = requests.Session()
    
    # Set cookies
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
    
    # Set headers
    session.headers.update({
        "User-Agent": user_agent,
        "Referer": MEDICAL_INSURANCE
    })
    
    for url in sorted(set(hrefs)): # unique and sorted
        try:
            filename = url.split('/')[-1]
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            print(f"Downloading {filename}...")
            response = session.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Saved to {filepath}")
            
        except Exception as e:
            print(f"Failed to download {url}: {e}")

if __name__ == '__main__':
    download_census_data()