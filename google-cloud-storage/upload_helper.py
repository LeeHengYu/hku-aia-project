import argparse
import mimetypes
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List
from urllib.parse import urlparse

from google.cloud import storage

FILE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = FILE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from insurers.download_file import download_file_from_url

ERROR_LOG_PATH = FILE_DIR / "upload_json_errors.log"

def log_error(message: str) -> None:
    timestamp = datetime.now()
    with ERROR_LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

def upload_folder(client, bucket_name, source_folder, blob_prefix=None, file_suffix=None):
    bucket = client.get_bucket(bucket_name)
    if isinstance(file_suffix, str):
        file_suffix = [file_suffix]
    
    for file in os.listdir(source_folder):
        if file_suffix is not None and not any(file.endswith(suffix) for suffix in file_suffix):
            continue
        local_path = os.path.join(source_folder, file)
        remote_path = os.path.join(blob_prefix, file) if blob_prefix is not None else file
        if os.path.isdir(local_path):
            upload_folder(client, bucket_name, local_path, remote_path, file_suffix)
        else:
            blob: storage.Blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_path)
            print(f"Uploaded {local_path} to {remote_path}")

def upload_bytes(client, bucket_name, data, destination_blob_name, blob_prefix=None):
    bucket = client.bucket(bucket_name)
    if blob_prefix is not None:
        destination_blob_name = f"{blob_prefix}/{destination_blob_name}"
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(data)
    print(f"Uploaded bytes to gs://{bucket_name}/{destination_blob_name}")

def upload_url(client, bucket_name, file_url, destination_blob_name, blob_prefix=None, timeout=30):
    bucket = client.bucket(bucket_name)
    if blob_prefix is not None:
        destination_blob_name = f"{blob_prefix}/{destination_blob_name}"
    blob: storage.Blob = bucket.blob(destination_blob_name)

    try:
        suffix = Path(destination_blob_name).suffix or Path(urlparse(file_url).path).suffix
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp_path = tmp_file.name
        tmp_file.close()

        download_file_from_url(
            file_url,
            tmp_path,
            timeout=timeout,
        )

        if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
            log_error(f"Empty downloaded file: url={file_url}")
            return

        content_type = mimetypes.guess_type(destination_blob_name)[0]
        blob.upload_from_filename(tmp_path, content_type=content_type)
    
    except Exception as e:
        log_error(f"Error downloading/uploading: url={file_url} error={e}")
        return
    
    finally:
        if "tmp_path" in locals():
            try:
                os.remove(tmp_path)
            except FileNotFoundError:
                pass

    print(f"Uploaded {file_url} to gs://{bucket_name}/{destination_blob_name}")

def upload_json(client, bucket_name, json_path, blob_prefix=None, key=None, timeout=30):
    import json

    json_path = Path(json_path)
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    items = None
    if key:
        if isinstance(data, dict):
            items = data.get(key)
    elif isinstance(data, dict):
        items = data.get("reports") or data.get("brochures")
    elif isinstance(data, list):
        items = data

    if not items:
        print("No items found in JSON for upload.")
        return

    allowed_exts = {".pdf", ".xlsx", ".xls", ".csv", ".docx"}

    for item in items:
        if not isinstance(item, dict):
            continue

        file_url = item.get("source_url") or item.get("url")
        if not file_url:
            continue
        lower_url = file_url.lower()
        if not any(ext in lower_url for ext in allowed_exts):
            continue

        filename = item.get("filename")
        if not filename:
            product_name = item.get("product_name")
            if product_name:
                filename = f"{product_name}.pdf"
            else:
                parsed = urlparse(file_url)
                filename = os.path.basename(parsed.path)

        if not filename:
            continue
        try:
            upload_url(
                client=client,
                bucket_name=bucket_name,
                file_url=file_url,
                destination_blob_name=filename,
                blob_prefix=blob_prefix,
                timeout=timeout,
            )
        except Exception as e:
            log_error(f"Error uploading: url={file_url} filename={filename} error={e}")

def list_blobs(client, bucket_name, prefix=None) -> List[storage.Blob]:
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)
    return list(blob for blob in blobs if not blob.name.endswith('/'))

def download_blob(client, bucket_name, source_blob_name, destination_file_name=None):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name if destination_file_name is not None else os.path.basename(source_blob_name))

def download_folder(client, bucket_name, source_folder, destination_folder=None):
    if destination_folder is None:
        destination_folder = source_folder

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    blobs = list_blobs(client, bucket_name, prefix=source_folder)
    for blob in blobs:
        download_blob(client, bucket_name, blob.name, os.path.join(destination_folder, os.path.basename(blob.name)))
    
def clean_folder(client, bucket_name, folder_path):
    bucket = client.bucket(bucket_name)
    if not folder_path.endswith('/'):
        folder_path += '/'
        
    blobs = list(bucket.list_blobs(prefix=folder_path))
    if not blobs:
        return
    bucket.delete_blobs(blobs)

def custom(client, bucket_name):
    bucket = client.bucket(bucket_name)
    ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Cloud Storage Utility CLI")
    parser.add_argument("--bucket", required=True, help="GCS Bucket name")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # 1. Upload Folder
    upload_parser = subparsers.add_parser("upload-folder", help="Upload a local folder")
    upload_parser.add_argument("source", help="Local source folder path")
    upload_parser.add_argument("--prefix", help="Remote folder prefix (destination folder in GCS)")
    upload_parser.add_argument("--suffix", nargs='+', help="Filter by file suffix (e.g., .csv .json)")

    # 2. Download Folder (The requested feature)
    dl_folder_parser = subparsers.add_parser("download-folder", help="Download a remote folder")
    dl_folder_parser.add_argument("remote_folder", help="Remote folder path in GCS")
    dl_folder_parser.add_argument("--local-path", help="Local destination path (defaults to folder name)")

    # 3. Upload Bytes
    bytes_parser = subparsers.add_parser("upload-bytes", help="Upload a text string as a file")
    bytes_parser.add_argument("data", help="String data to upload")
    bytes_parser.add_argument("filename", help="Destination filename")
    bytes_parser.add_argument("--prefix", help="Remote folder prefix")

    # 3b. Upload URL
    url_parser = subparsers.add_parser("upload-url", help="Stream a URL directly to GCS")
    url_parser.add_argument("url", help="Source URL to download")
    url_parser.add_argument("filename", help="Destination filename")
    url_parser.add_argument("--prefix", help="Remote folder prefix")
    url_parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")

    # 3c. Upload JSON
    json_parser = subparsers.add_parser("upload-json", help="Upload files from a JSON manifest")
    json_parser.add_argument("json_path", help="Path to JSON file")
    json_parser.add_argument("--prefix", help="Remote folder prefix")
    json_parser.add_argument("--key", help="Root key to read items from (e.g., reports, brochures)")
    json_parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")

    # 4. List Blobs
    list_parser = subparsers.add_parser("list", help="List files in bucket")
    list_parser.add_argument("--prefix", help="Filter by folder prefix")

    # 5. Download Single File
    dl_file_parser = subparsers.add_parser("download-file", help="Download a single file")
    dl_file_parser.add_argument("blob_name", help="Full path of file in GCS")
    dl_file_parser.add_argument("local_path", help="Local destination filename")

    # 6. Clean Folder
    clean_parser = subparsers.add_parser("clean", help="Delete all files in a remote folder")
    clean_parser.add_argument("folder", help="Remote folder path to delete")

    custom_parser = subparsers.add_parser("custom", help="Run in-code functions")

    args = parser.parse_args()
    
    # Initialize Client
    try:
        cli = storage.Client()
    except Exception as e:
        print("Error initializing Google Cloud Client. Ensure credentials are set.")
        print(e)
        exit(1)

    # Route commands
    if args.command == "upload-folder":
        upload_folder(cli, args.bucket, args.source, args.prefix, args.suffix)
        
    elif args.command == "download-folder":
        download_folder(cli, args.bucket, args.remote_folder, args.local_path)
        
    elif args.command == "upload-bytes":
        upload_bytes(cli, args.bucket, args.data, args.filename, args.prefix)

    elif args.command == "upload-url":
        upload_url(cli, args.bucket, args.url, args.filename, args.prefix, timeout=args.timeout)

    elif args.command == "upload-json":
        upload_json(cli, args.bucket, args.json_path, args.prefix, key=args.key, timeout=args.timeout)
        
    elif args.command == "list":
        blobs = list_blobs(cli, args.bucket, args.prefix)
        for b in blobs:
            print(b.name)
            
    elif args.command == "download-file":
        download_blob(cli, args.bucket, args.blob_name, args.local_path)
        
    elif args.command == "clean":
        confirm = input(f"Are you sure you want to delete everything in '{args.folder}'? (y/n): ")
        if confirm.lower().strip() == 'y':
            clean_folder(cli, args.bucket, args.folder)
    
    elif args.command == "custom":
        custom(cli, args.bucket)
            
    else:
        parser.print_help()
