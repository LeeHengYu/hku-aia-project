import os
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.manulife.com.hk"

def get_product_links(list_page_url):
    """Extract all product links from list page"""
    try:
        response = requests.get(list_page_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        product_links = set()
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            if '/products/health/vhis/' in href and '.html' in href:
                full_url = urljoin(list_page_url, href)
                
                if full_url != list_page_url and '#' not in full_url:
                    product_links.add(full_url)
        
        return sorted(product_links)
    
    except Exception as e:
        print(f"[!] Error getting product links: {e}")
        return []

def download_pdf_with_retry(file_url, filepath, max_retries=3):
    """Download PDF with retry mechanism"""
    for attempt in range(max_retries):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(file_url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"  [✓] {os.path.basename(filepath)}")
            return True
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print(f"  [✗] Failed: {os.path.basename(filepath)}")
                return False

def download_all_pdfs_from_page(page_url, page, max_pdfs=5) -> int:
    """Download PDFs from product detail page (max: max_pdfs)"""
    download_folder = "brochures/manulife"
    os.makedirs(download_folder, exist_ok=True)
    
    try:
        page.goto(page_url, wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        
        pdf_links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            text = a_tag.get_text(strip=True).lower()
            
            url_path = href.split("?")[0].split("#")[0]
            if url_path.lower().endswith('.pdf'):
                
                # Filter out irrelevant PDFs
                if any(skip in href.lower() for skip in ['faq', 'redomiciliation', 'promotion']):
                    continue
                
                # Priority: product brochures first
                if any(kw in href.lower() or kw in text for kw in [
                    'product', 'leaflet', 'brochure', 'benefit', 'fact', 'guide'
                ]):
                # these two if statements are not quite readable.
                    priority = 1
                else:
                    priority = 2
                
                if href.startswith('http'):
                    file_url = href
                elif href.startswith('/'):
                    file_url = f"{BASE_URL}{href}"
                else:
                    file_url = urljoin(page_url, href)
                
                filename = os.path.basename(urlparse(file_url).path)
                if filename:
                    pdf_links.append((priority, file_url, filename))
        
        # Sort by priority and remove duplicates
        pdf_links.sort(key=lambda x: x[0])
        seen_files = set()
        pdfs_to_download = []
        for priority, url, filename in pdf_links:
            if filename not in seen_files:
                seen_files.add(filename)
                pdfs_to_download.append((priority, url, filename))
            if len(pdfs_to_download) == max_pdfs:
                break
        
        if not pdfs_to_download:
            print(f"  [-] No PDF found")
            return 0
        
        downloaded = 0
        for priority, file_url, filename in pdfs_to_download:
            filepath = os.path.join(download_folder, filename)
            
            if os.path.exists(filepath):
                print(f"  [~] {filename} (exists)")
                downloaded += 1
            else:
                if download_pdf_with_retry(file_url, filepath):
                    downloaded += 1
        
        return downloaded # weird returned value
        
    except Exception as e:
        print(f"  [!] Error: {e}")
        return 0

def scrape_health_products(list_page_url: str, max_pdfs_per_product: int=5) -> None:
    """Main scraper function"""
    
    product_links = get_product_links(list_page_url)
    
    if not product_links:
        print("[!] No product links found!")
        return
    
    print(f"[✓] Found {len(product_links)} products\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        total_pdfs = 0
        for i, product_url in enumerate(product_links, 1):
            product_name = product_url.split('/')[-1].replace('.html', '')
            
            count = download_all_pdfs_from_page(product_url, page, max_pdfs=max_pdfs_per_product)
            total_pdfs += count
            
            if i < len(product_links):
                time.sleep(1)
            
            print()
        
        browser.close()

if __name__ == "__main__":
    health_vhis_url = f"{BASE_URL}/en/individual/products/health/vhis.html"
    scrape_health_products(health_vhis_url, max_pdfs_per_product=5)
