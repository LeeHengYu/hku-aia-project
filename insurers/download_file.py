import os
import requests

def download_file_from_url(file_url, file_path, headers=None, timeout=15):
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    if headers:
        default_headers.update(headers)
    
    headers = default_headers
    
    with requests.get(file_url, headers=headers, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                f.write(chunk)

def create_folder_if_not_exist(dir):
    os.makedirs(dir, exist_ok=True)