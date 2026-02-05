import sys
from curl_cffi import requests

def download_file_from_url(
    file_url,
    file_path=None,
    timeout=15,
    return_stream=False,
    allowed_content_types=None,
):
    default_headers = {
        "User-Agent": "Chrome/120.0.0.0",
        "Content-Type": "application/pdf",
        "Accept": "application/pdf",
        "Accept-Encoding": "gzip, deflate, br",
    }

    if allowed_content_types is None:
        allowed_content_types = {
            "application/pdf",
            "application/octet-stream",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
            "text/csv",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        }

    try:
        r = requests.get(
            file_url,
            headers=default_headers,
            stream=True,
            timeout=timeout,
            impersonate="chrome110",
        )
        r.raise_for_status()

        content_type = r.headers.get("content-type", "").lower()
        if allowed_content_types:
            if not any(ct in content_type for ct in allowed_content_types):
                print(r.text)
                r.close()
                return

        if return_stream:
            return r

        if not file_path:
            r.close()
            raise ValueError("file_path is required when return_stream is False")

        try:
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 32):
                    f.write(chunk)
        finally:
            r.close()
    except Exception as e:
        print(f"Error downloading file: {e}", file=sys.stderr)
