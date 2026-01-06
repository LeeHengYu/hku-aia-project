import os
import requests

def download_file_from_url(file_url, file_path, headers=None):
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
    print(f"[*] Downloading from: {file_url}")
    
    with requests.get(file_url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                f.write(chunk)
    
    print(f"[+] Successfully saved to {file_path}")

def create_folder_if_not_exist(dir):
    os.makedirs(dir, exist_ok=True)