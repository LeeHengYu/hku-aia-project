import argparse
import os
import re
from io import StringIO
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

# --------------------------------------
# Configuration
# --------------------------------------
OUTPUT_DIR = "./separate_tables"
ATTACH_DIR = os.path.join(OUTPUT_DIR, "attachments")
FORMATS = [".pdf", ".xls", ".xlsx", ".csv", ".doc", ".docx"]
used_names = set()

# --------------------------------------
# Helper Functions
# --------------------------------------

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def extract_page_title(soup):
    """Get readable page title (using <h1> first, <title> second)."""
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)
    title_tag = soup.find("title")
    if title_tag and title_tag.get_text(strip=True):
        return title_tag.get_text(strip=True)
    return "Untitled"


def clean_file_name(raw_text):
    """Remove invalid file name characters and normalize whitespace."""
    raw_text = re.sub(r'[<>:"/\\|?*]', "", raw_text)
    raw_text = re.sub(r"\s+", "_", raw_text.strip())
    return raw_text or "file"


def get_unique_filename(base_name, extension):
    """Prevent duplicate names in the same folder."""
    base = clean_file_name(base_name)
    name = base
    counter = 2
    while f"{name}{extension}" in used_names: # weird way to write but okay
        name = f"{base}_{counter}"
        counter += 1
    used_names.add(f"{name}{extension}")
    return f"{name}{extension}"


def clean_table(df):
    """Trim headers and drop empty rows."""
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how="all")
    return df


def normalize_url(url):
    """Remove fragments and trailing slashes."""
    return url.split("#")[0].rstrip("/").strip()


def resolve_final_url(url):
    """Follow redirects if needed."""
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        if response.status_code in (301, 302, 303, 307, 308):
            return response.headers.get("Location", url)
        return response.url
    except Exception:
        return url


def download_attachment(file_url, page_title):
    """Download attached PDF/Excel/CSV file."""
    try:
        file_name = os.path.basename(urlparse(file_url).path)
        if not file_name:
            return None

        base_name, ext = os.path.splitext(file_name)
        combined_name = f"{page_title}_{base_name}"
        clean_name = get_unique_filename(combined_name, ext)
        save_path = os.path.join(ATTACH_DIR, clean_name)

        response = requests.get(file_url, stream=True, timeout=15)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)

        return save_path

    except Exception as e:
        return


# --------------------------------------
# Main crawler
# --------------------------------------

def crawl_page(url, depth, max_depth, visited):
    """Recursively crawl pages to extract tables and attachments."""
    if depth > max_depth:
        return

    url = normalize_url(url)
    if url in visited:
        return
    visited.add(url)

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        page_title = extract_page_title(soup)

        # --- Extract and save HTML tables ---
        tables = soup.find_all("table")
        for table in tables:
            if table.find("table"):  # skip nested tables
                continue
            try:
                df_list = pd.read_html(StringIO(str(table)), header=0)
                df = clean_table(df_list[0])

                caption_tag = table.find("caption")
                caption_text = caption_tag.get_text(strip=True) if caption_tag else "Table"

                filename_base = f"{page_title}_{caption_text}"
                filename = get_unique_filename(filename_base, ".csv")
                filepath = os.path.join(OUTPUT_DIR, filename)

                df.to_csv(filepath, index=False, encoding="utf-8-sig")
            except Exception as e:
                print(f"[!] Failed to parse table at {url}: {e}")

        # --- Download linked PDF/Excel/CSV attachments ---
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if any(href.lower().endswith(ext) for ext in FORMATS):
                file_url = urljoin(url, href)
                download_attachment(file_url, page_title)

        # --- Recurse into linked pages if within depth ---
        if depth + 1 <= max_depth: # early termination (save parsing time)
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                full_url = urljoin(url, href)
                if not any(full_url.lower().endswith(ext) for ext in FORMATS):
                    final_url = resolve_final_url(full_url)
                    crawl_page(final_url, depth + 1, max_depth, visited)

    except Exception as e:
        pass


def run_table_scrape(base_url, max_depth=1):
    """Main driver function."""
    ensure_dir(OUTPUT_DIR)
    ensure_dir(ATTACH_DIR)
    visited = set()
    crawl_page(base_url, 0, max_depth, visited)

# --------------------------------------
# CLI entry point
# --------------------------------------

if __name__ == "__main__":
    default_entry = "https://www.chp.gov.hk/en/statistics/submenu/44/index.html"

    parser = argparse.ArgumentParser(description="Scrape tables and attachments (PDF/Excel/CSV) into CSV files.")
    parser.add_argument("url", help="Starting URL to scrape", nargs='?', default=default_entry)
    parser.add_argument("depth", type=int, help="Max recursion depth (e.g. 1, 2, 3)", nargs='?', default=3)
    args = parser.parse_args()

    url = args.url.strip() if args.url else input("Enter the starting URL: ").strip()
    depth = args.depth if args.depth else int(input("Enter max depth (e.g. 1, 2, 3): ").strip())

    run_table_scrape(url, max_depth=depth)