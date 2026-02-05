from curl_cffi import requests

def download_file_from_url(file_url, file_path, headers=None, timeout=15):
    default_headers = {
        "User-Agent": "Chrome/120.0.0.0",
        "Content-Type": "application/pdf",
        "Accept": "application/pdf",
        "Accept-Encoding": "gzip, deflate, br",
    }

    if headers:
        default_headers.update(headers)

    headers = default_headers

    try:
        r = requests.get(
            file_url,
            headers=headers,
            stream=True,
            timeout=timeout,
            impersonate="chrome110",
        )
        r.raise_for_status()

        content_type = r.headers.get("content-type", "").lower()
        if "application/pdf" not in content_type:
            print(r.text)
            return

        if r.status_code != 200:
            return

        with open(file_path, "wb") as f:
            f.write(r.content)

    except Exception:
        ...
