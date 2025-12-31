import os
import requests

from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

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
            product_links.add(full_url)
        
        return sorted(product_links)
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

def get_extended_product_links(target_url):
    """
    Finds all links in the target_url that are sub-paths (extensions) 
    of that specific URL.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    base_prefix = target_url.replace('.html', '')
    if not base_prefix.endswith('/'):
        base_prefix += '/'

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        extended_links = set()
        
        for a_tag in soup.find_all('a', href=True):
            raw_href = a_tag['href']
            if not raw_href.startswith('/en/products'):
                continue
            
            full_url = urljoin(target_url, raw_href)
            
            if full_url.startswith(base_prefix) and full_url.strip('/') != base_prefix.strip('/'):
                extended_links.add(full_url)
        
        return sorted(list(extended_links))

    except requests.exceptions.RequestException as e:
        print(f"Error accessing {target_url}: {e}")
        return []


def download_brochure(page_url, download_folder="brochures"):
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

        # 5. Execute the download
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        
        file_path = os.path.join(download_folder, filename)
        
        print(f"[*] Found: {filename}")
        print(f"[*] Downloading from: {file_url}")
        
        with requests.get(file_url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024 * 8):
                    f.write(chunk)
        
        print(f"[+] Successfully saved to {file_path}")
        return file_path

    except Exception as e:
        print(f"[!] Error processing {page_url}: {e}")
        return None


if __name__ == "__main__":
    res = get_extended_product_links('https://www.aia.com.hk/en/products/health')
    for p in res:
        print(p)
    # major_links = find_aia_major_categories()
    # for cat in major_links:
    #     product_pages = get_extended_product_links(cat)
        # for page in product_pages:
        #     download_brochure(page)