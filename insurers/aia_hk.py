import os
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests

from download_file import download_file_from_url

def find_aia_major_categories():
    base_url = "https://www.aia.com.hk/en/"
    target_pattern = "https://www.aia.com.hk/en/products/"

    try:
        response = requests.get(base_url)
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        product_links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if not href.startswith('/en/products'):
                continue
            
            full_url = urljoin(base_url, href)
            segments = full_url.replace(target_pattern, "").split("/")
            if len(segments) == 1:
                product_links.add(full_url)
        
        return sorted(product_links)
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []
    
def scrape_dynamic_products(root_url):
    # this is a recursive formula, if the target_url contains the brochure of we want, we download it.
    # else, check if we are currently in a list view of products.
    PRODUCT_LIST_CLASS = 'cmp-hkproductfilterlist__productcard'
    visited = set()

    def dfs(current_url, page):
        if current_url in visited:
            return
        visited.add(current_url)

        try:
            page.goto(current_url, wait_until="load", timeout=30000)
            soup = BeautifulSoup(page.content(), 'html.parser') 
        except Exception as e:
            print(f"[!] Failed to load {current_url}: {e}")
            return
        
        product_divs = soup.find_all('div', class_=PRODUCT_LIST_CLASS)
        if product_divs:
            print(f"Current page: {current_url}, found {len(product_divs)} products")
            next_batch = []
            for div in product_divs:
                a_tag = div.find_parent('a', href=True)
                if a_tag:
                    full_url = urljoin(current_url, a_tag['href'])
                    # Only follow links that extend the current path to stay in scope
                    if full_url.startswith(current_url.replace('.html', '')):
                        next_batch.append(full_url)
            for link in next_batch:
                dfs(link, page)

        else:
            download_brochure(current_url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        dfs(root_url, page)
        browser.close()


def download_brochure(page_url, download_folder="brochures/aia"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(page_url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        download_tag = soup.find('a', {'data-cmp-is': 'document-download-link'})

        if not download_tag or not download_tag.get('href'):
            print(f"[-] No brochure link found on: {page_url}")
            return None

        file_url = urljoin(page_url, download_tag['href'])
        
        parsed_url = urlparse(file_url)
        filename = os.path.basename(parsed_url.path)
        
        if not filename:
            print(f"[-] Could not determine filename from URL: {file_url}")
            return None

        os.makedirs(download_folder, exist_ok=True)
        file_path = os.path.join(download_folder, filename)
        
        print(f"[*] Found: {filename}")
        download_file_from_url(file_url, file_path, headers)
        return file_path

    except Exception as e:
        print(f"[!] Error processing {page_url}: {e}")
        return None


if __name__ == "__main__":
    major_links = find_aia_major_categories()
    # print("Entry pages for each insurance type:")
    # for l in major_links:
    #     print(l)
    
    for l in major_links:
        if l.split("/")[-1] == 'health':
            scrape_dynamic_products(l)
