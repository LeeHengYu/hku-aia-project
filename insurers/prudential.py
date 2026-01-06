import os
import re
import time
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from download_file import create_folder_if_not_exist, download_file_from_url

CONFIG = {
    "non_product_keywords": {
        'admin', 'login', 'contact', 'about', 'news', 'blog', 'faq', 'form', 
        'terms', 'privacy', 'policy', 'claim', 'statement', 'download', 'search',
    },
    "product_url_keywords": {
        '/health-insurance/', '/critical-illness/', '/medical/', 
        '/product', 'plan', 'insurance', 'pru', 'ci'
    },
    "medical_keywords": {
        'health-insurance', 'critical-illness', 'medical'
    },
    "pdf_priority_keywords": {
        'product', 'leaflet', 'brochure', 'benefit', 'fact', 'guide', 
        '危疾', 'ci', 'critical', 'illness', 'plan', 'summary', 'features'
    },
    "product_page_guess_keywords": {
        'health', 'medical', 'insurance', 'pru', 'ci'
    },
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
}

BASE_URL = "https://www.prudential.com.hk/en/health-insurance"

def scrape_prudential_products(root_url):
    """
    Scrape Prudential products using DFS traversal.
    Navigates through pages and downloads brochures when found.
    """
    visited = set()

    def dfs(current_url, page):
        if current_url in visited or not current_url.startswith(BASE_URL):
            return
        
        # Ensure we stay on the English page and within Prudential domain
        visited.add(current_url)
        print(f"[*] Searching in {current_url}")

        try:
            page.goto(current_url, wait_until="load", timeout=30000)
            page.wait_for_timeout(2000)
            
            soup = BeautifulSoup(page.content(), 'html.parser')
            
            download_brochures(current_url, soup)

            next_links = _extract_links_from_soup(soup, current_url)
            for link in next_links:
                dfs(link, page)
                
        except Exception as e:
            print(f"[!] Error processing {current_url}: {e}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        dfs(root_url, page)
        browser.close()

def _extract_links_from_soup(soup, base_url):
    """Helper to extract product links from a parsed page"""
    discovered_links = set()
    
    # Look for links in navigation, product lists, and content areas
    for a_tag in soup.find_all('a', href=True):
        href = a_tag.get('href', '')
        
        # Look for potential product pages based on URL patterns
        if any(keyword in href.lower() for keyword in CONFIG['product_url_keywords']):
            full_url = urljoin(base_url, href)
            
            # Filter for internal links that stay on English page and avoid non-product pages
            if 'prudential.com.hk' in full_url and full_url.startswith(BASE_URL):
                if not any(skip in full_url.lower() for skip in CONFIG['non_product_keywords']):
                    discovered_links.add(full_url)
                    
    return discovered_links

def download_brochures(page_url, soup, max_pdfs=5):
    """Download PDFs from a product page"""
    download_folder = "brochures"
    create_folder_if_not_exist(download_folder)
    
    try:
        pdf_links = []
        
        # Helper to process and add URL
        def add_pdf_url(url):
            full_url = urljoin(page_url, url)
            
            # Clean filename
            filename = os.path.basename(urlparse(full_url).path)
            if filename and filename != '/':
                if not filename.lower().endswith('.pdf'):
                    filename += '.pdf'
                pdf_links.append((full_url, filename))

        # 1. <a> tags
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            url_path = href.split("?")[0].split("#")[0]
            if url_path.lower().endswith('.pdf'):
                add_pdf_url(href)
        
        # 2. data-href attributes
        for element in soup.find_all(attrs={"data-href": True}):
            href = element.get('data-href', '')
            if href.lower().endswith('.pdf'):
                add_pdf_url(href)
        
        # 3. onclick attributes
        for element in soup.find_all(attrs={"onclick": True}):
            onclick = element.get('onclick', '')
            if '.pdf' in onclick.lower():
                pdf_urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))*\.pdf', onclick)
                for pdf_url in pdf_urls:
                    add_pdf_url(pdf_url)
        
        # Remove duplicates
        seen_files = set()
        pdfs_to_download = []
        for url, filename in pdf_links:
            clean_filename = unquote(filename).replace(' ', '_').replace('?', '_').replace('&', '_')
            if clean_filename not in seen_files:
                seen_files.add(clean_filename)
                pdfs_to_download.append((url, clean_filename))
            if len(pdfs_to_download) == max_pdfs:
                break     
        
        for file_url, filename in pdfs_to_download:
            filepath = os.path.join(download_folder, filename)
            
            if os.path.exists(filepath):
                print(f"  [~] {filename} (exists)")
            else:
                download_file_from_url(file_url, filepath)
         
    except Exception as e:
        print(f"  [!] Error processing page: {e}")

if __name__ == "__main__":
    start_url = f"{BASE_URL}/health-insurance/index.html"
    scrape_prudential_products(start_url)