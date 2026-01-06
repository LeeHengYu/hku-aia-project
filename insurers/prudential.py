import os
import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from download_file import create_folder_if_not_exist, download_file_from_url

CONFIG = {
    "non_product_keywords": [
        'admin', 'login', 'contact', 'about', 'news', 'blog', 'faq', 'form', 
        'terms', 'privacy', 'policy', 'claim', 'statement', 'download', 'search',
    ],
    "product_url_keywords": [
        '/health-insurance/', '/critical-illness/', '/medical/', 
        '/product', 'plan', 'insurance', 'pru', 'ci'
    ],
    "medical_keywords": [
        'health-insurance', 'critical-illness', 'medical'
    ],
    "pdf_priority_keywords": [
        'product', 'leaflet', 'brochure', 'benefit', 'fact', 'guide', 
        '危疾', 'ci', 'critical', 'illness', 'plan', 'summary', 'features'
    ],
    "product_page_guess_keywords": [
        'health', 'medical', 'insurance', 'pru', 'ci'
    ],
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
}

def discover_product_links(start_url):
    """Discover product links by exploring the site structure"""
    discovered_links = set()
    
    try:
        # Get the main page content
        response = requests.get(start_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for links in navigation, product lists, and content areas
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href', '')
            
            # Look for potential product pages based on URL patterns
            if any(keyword in href.lower() for keyword in CONFIG['product_url_keywords']):
                full_url = urljoin(start_url, href)
                
                # Filter for internal links that look like product pages
                if 'prudential.com.hk' in full_url and ('.html' in full_url or '/index.html' in full_url):
                    # Avoid administrative or non-product pages
                    if not any(skip in full_url.lower() for skip in CONFIG['non_product_keywords']):
                        discovered_links.add(full_url)
        
        # Also look for links in JavaScript attributes or data attributes
        for element in soup.find_all(attrs={"data-href": True}):
            href = element.get('data-href', '')
            if href and any(keyword in href.lower() for keyword in CONFIG['product_url_keywords']):
                full_url = urljoin(start_url, href)
                if 'prudential.com.hk' in full_url and ('.html' in full_url or '/index.html' in full_url):
                    if not any(skip in full_url.lower() for skip in CONFIG['non_product_keywords']):
                        discovered_links.add(full_url)
        
        # Look for links in onclick attributes or other JavaScript handlers
        for element in soup.find_all(attrs={"onclick": True}):
            onclick = element.get('onclick', '')
            if any(w in onclick.lower() for w in CONFIG['medical_keywords']):
                # Extract potential URLs from onclick
                potential_urls = re.findall(r'["\']([^"\']*(?:health-insurance|critical-illness|medical)[^"\']*\.(?:html|htm))["\']', onclick)
                for url_part in potential_urls:
                    full_url = urljoin(start_url, url_part)
                    if 'prudential.com.hk' in full_url:
                        discovered_links.add(full_url)
        
        return sorted(list(discovered_links))
    
    except Exception as e:
        print(f"[!] Error discovering links: {e}")
        return []

def explore_deeper_links(initial_links, max_depth=2):
    """Explore deeper into the site to find more product links"""
    all_links = set(initial_links)
    visited = set()
    
    for depth in range(max_depth):
        new_links = set()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            for link in list(all_links):
                if link in visited:
                    continue
                    
                try:
                    print(f"  [Depth {depth+1}] Exploring: {link}")
                    page.goto(link, wait_until="load", timeout=15000)
                    page.wait_for_timeout(1000)  # Wait for dynamic content
                    
                    soup = BeautifulSoup(page.content(), 'html.parser')
                    
                    # Look for more product links on this page
                    for a_tag in soup.find_all('a', href=True):
                        href = a_tag.get('href', '')
                        
                        if any(keyword in href.lower() for keyword in CONFIG['product_url_keywords']):
                            full_url = urljoin(link, href)
                            
                            if 'prudential.com.hk' in full_url and ('.html' in full_url or '/index.html' in full_url):
                                if not any(skip in full_url.lower() for skip in CONFIG['non_product_keywords']):
                                    new_links.add(full_url)
                    
                    visited.add(link)
                    
                except Exception as e:
                    print(f"    [Error] {e}")
                    continue
            
            browser.close()
        
        # Add new links to the collection
        all_links.update(new_links)
        
        if not new_links:
            print(f"  [Depth {depth+1}] No new links found")
            break
        else:
            print(f"  [Depth {depth+1}] Found {len(new_links)} new links")
    
    return sorted(list(all_links))

def download_all_pdfs_from_page(page_url, page, max_pdfs=5):
    """Download PDFs from a product page"""
    download_folder = "brochures"
    create_folder_if_not_exist(download_folder)
    
    try:
        page.goto(page_url, wait_until="load", timeout=30000)
        page.wait_for_timeout(2000)  # Wait for dynamic content
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        
        pdf_links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            text = a_tag.get_text(strip=True).lower()
            
            # Check if href is a PDF file
            url_path = href.split("?")[0].split("#")[0]
            if url_path.lower().endswith('.pdf'):
                # Filter out irrelevant PDFs
                if any(skip in href.lower() for skip in CONFIG['non_product_keywords']):
                    continue
                
                # Priority: product brochures first
                if any(kw in href.lower() or kw in text for kw in CONFIG['pdf_priority_keywords']):
                    priority = 1
                else:
                    priority = 2
                
                if href.startswith('http'):
                    file_url = href
                elif href.startswith('/'):
                    # Handle relative URLs
                    base_url = f"{page_url.split('/')[0]}//{page_url.split('/')[2]}"
                    file_url = f"{base_url}{href}"
                else:
                    file_url = urljoin(page_url, href)
                
                # Clean filename
                filename = os.path.basename(urlparse(file_url).path)
                if filename and filename != '/':
                    # Ensure filename has .pdf extension
                    if not filename.lower().endswith('.pdf'):
                        filename += '.pdf'
                    pdf_links.append((priority, file_url, filename))
        
        # Also look for PDFs in data attributes or other elements
        for element in soup.find_all(attrs={"data-href": True, "data-type": "pdf"}):
            href = element.get('data-href', '')
            if href.lower().endswith('.pdf'):
                if href.startswith('http'):
                    file_url = href
                elif href.startswith('/'):
                    base_url = f"{page_url.split('/')[0]}//{page_url.split('/')[2]}"
                    file_url = f"{base_url}{href}"
                else:
                    file_url = urljoin(page_url, href)
                
                filename = os.path.basename(urlparse(file_url).path)
                if filename and filename != '/':
                    if not filename.lower().endswith('.pdf'):
                        filename += '.pdf'
                    pdf_links.append((2, file_url, filename))
        
        # Look for PDFs in onclick attributes or other JavaScript handlers
        for element in soup.find_all(attrs={"onclick": True}):
            onclick = element.get('onclick', '')
            if '.pdf' in onclick.lower():
                # Extract PDF URL from onclick attribute
                pdf_urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))*\.pdf', onclick)
                for pdf_url in pdf_urls:
                    filename = os.path.basename(urlparse(pdf_url).path)
                    if filename and filename != '/':
                        if not filename.lower().endswith('.pdf'):
                            filename += '.pdf'
                        pdf_links.append((2, pdf_url, filename))
        
        # Sort by priority and remove duplicates
        pdf_links.sort(key=lambda x: x[0])
        seen_files = set()
        pdfs_to_download = []
        for priority, url, filename in pdf_links:
            clean_filename = filename.replace(' ', '_').replace('%20', '_').replace('?', '_').replace('&', '_')
            if clean_filename not in seen_files:
                seen_files.add(clean_filename)
                pdfs_to_download.append((priority, url, clean_filename))
            if len(pdfs_to_download) == max_pdfs:
                break     
        
        for priority, file_url, filename in pdfs_to_download:
            filepath = os.path.join(download_folder, filename)
            
            if os.path.exists(filepath):
                print(f"  [~] {filename} (exists)")
            else:
                download_file_from_url(file_url, filepath)
         
    except Exception as e:
        print(f"  [!] Error processing page: {e}")

def auto_discover_and_scrape_products(start_url, max_pdfs_per_product=5):
    """Main function to auto-discover and scrape product pages"""
    
    print("\n[Step 1] Discovering product links...")
    initial_links = discover_product_links(start_url)
    
    if not initial_links:
        try:
            response = requests.get(start_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for all potential product-related links
            for a_tag in soup.find_all('a', href=True):
                href = a_tag.get('href', '')
                
                # Look for any links that might be product pages
                if any(w in href.lower() for w in CONFIG['product_page_guess_keywords']) and ('.html' in href):
                    full_url = urljoin(start_url, href)
                    if 'prudential.com.hk' in full_url and not any(skip in full_url.lower() for skip in CONFIG['non_product_keywords']):
                        initial_links.append(full_url)
                        
        except Exception as e:
            print(f"[!] Alternative approach failed: {e}")
    
    if not initial_links:
        print("[!] No product links found after all attempts!")
        return
    
    print(f"[✓] Found {len(initial_links)} initial product links\n")
    
    print("[Step 2] Exploring deeper links...")
    all_product_links = explore_deeper_links(initial_links, max_depth=2)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for i, product_url in enumerate(all_product_links, 1):
            product_name = product_url.split('/')[-1].replace('.html', '').replace('.htm', '')
            if not product_name:
                product_name = product_url.split('/')[-2]
            print(f"[{i}/{len(all_product_links)}] {product_name}")
            
            count = download_all_pdfs_from_page(product_url, page, max_pdfs=max_pdfs_per_product)
            
            if i < len(all_product_links):
                time.sleep(.5)
        
        browser.close()

if __name__ == "__main__":
    start_url = "https://www.prudential.com.hk/tc/health-insurance/critical-illness/"
    auto_discover_and_scrape_products(start_url, max_pdfs_per_product=5)