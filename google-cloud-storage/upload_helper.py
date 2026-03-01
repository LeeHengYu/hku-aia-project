import argparse
import json
import mimetypes
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union
from urllib.parse import urlparse

from google.cloud import storage

FILE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = FILE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from insurers.download_file import download_file_from_url
from upload_helper_utils import build_blob_path, emit_result

Summary = Dict[str, int]
UploadResult = Dict[str, Union[int, str]]
UploadJsonSummary = Dict[str, Union[int, List[str]]]
CommandResult = Dict[str, Any]


def upload_folder(
    client: storage.Client,
    bucket_name: str,
    source_folder: str,
    blob_prefix: Optional[str] = None,
    file_suffix: Optional[Union[str, Sequence[str]]] = None,
) -> Summary:
    summary = {"uploaded": 0, "skipped": 0}
    bucket = client.get_bucket(bucket_name)

    if isinstance(file_suffix, str):
        suffixes: Optional[List[str]] = [file_suffix]
    elif file_suffix is None:
        suffixes = None
    else:
        suffixes = list(file_suffix)

    for file in os.listdir(source_folder):
        local_path = os.path.join(source_folder, file)
        if os.path.isdir(local_path):
            remote_path = build_blob_path(file, blob_prefix)
            child_summary = upload_folder(
                client,
                bucket_name,
                local_path,
                remote_path,
                suffixes,
            )
            summary["uploaded"] += child_summary["uploaded"]
            summary["skipped"] += child_summary["skipped"]
            continue
        if suffixes is not None and not any(file.endswith(suffix) for suffix in suffixes):
            summary["skipped"] += 1
            continue
        remote_path = build_blob_path(file, blob_prefix)
        try:
            blob: storage.Blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_path)
            summary["uploaded"] += 1
            print(f"Uploaded {local_path} to {remote_path}")
        except Exception as e:
            raise RuntimeError(f"Failed upload: local_path={local_path} remote_path={remote_path} error={e}") from e
    return summary


def upload_bytes(
    client: storage.Client,
    bucket_name: str,
    data: Union[str, bytes],
    destination_blob_name: str,
    blob_prefix: Optional[str] = None,
) -> UploadResult:
    bucket = client.bucket(bucket_name)
    destination_blob_name = build_blob_path(destination_blob_name, blob_prefix)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(data)
    print(f"Uploaded bytes to gs://{bucket_name}/{destination_blob_name}")
    return {"uploaded": 1, "destination": destination_blob_name}


def upload_url(
    client: storage.Client,
    bucket_name: str,
    file_url: str,
    destination_blob_name: str,
    blob_prefix: Optional[str] = None,
    timeout: int = 30,
) -> UploadResult:
    bucket = client.bucket(bucket_name)
    destination_blob_name = build_blob_path(destination_blob_name, blob_prefix)
    blob: storage.Blob = bucket.blob(destination_blob_name)

    tmp_path = None
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
            raise RuntimeError(f"Empty downloaded file: url={file_url}")

        content_type = mimetypes.guess_type(destination_blob_name)[0]
        blob.upload_from_filename(tmp_path, content_type=content_type)

    except Exception as e:
        error = f"Error downloading/uploading: url={file_url} destination={destination_blob_name} error={e}"
        raise RuntimeError(error) from e

    finally:
        if tmp_path is not None:
            try:
                os.remove(tmp_path)
            except FileNotFoundError:
                pass

    print(f"Uploaded {file_url} to gs://{bucket_name}/{destination_blob_name}")
    return {"uploaded": 1, "destination": destination_blob_name}


def upload_json(
    client: storage.Client,
    bucket_name: str,
    json_path: str,
    blob_prefix: Optional[str] = None,
    key: Optional[str] = None,
    timeout: int = 30,
    fail_fast: bool = False,
) -> UploadJsonSummary:
    summary = {"uploaded": 0, "skipped": 0, "failed": 0, "errors": []}
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
        summary["skipped"] += 1
        return summary

    allowed_exts = {".pdf", ".xlsx", ".xls", ".csv", ".docx"}

    for item in items:
        if not isinstance(item, dict):
            summary["skipped"] += 1
            continue

        file_url = item.get("source_url") or item.get("url")
        if not file_url:
            summary["skipped"] += 1
            continue

        parsed = urlparse(file_url)
        lower_url_path = parsed.path.lower()
        if not any(lower_url_path.endswith(ext) for ext in allowed_exts):
            summary["skipped"] += 1
            continue

        filename = item.get("filename")
        if not filename:
            product_name = item.get("product_name")
            if product_name:
                filename = f"{product_name}.pdf"
            else:
                filename = os.path.basename(parsed.path)

        if not filename:
            summary["skipped"] += 1
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
            summary["uploaded"] += 1
        except Exception as e:
            error_message = f"Error uploading: url={file_url} filename={filename} error={e}"
            summary["failed"] += 1
            summary["errors"].append(error_message)
            if fail_fast:
                break

    return summary


def list_blobs(client: storage.Client, bucket_name: str, prefix: Optional[str] = None) -> List[storage.Blob]:
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)
    return list(blob for blob in blobs if not blob.name.endswith('/'))


def download_blob(
    client: storage.Client,
    bucket_name: str,
    source_blob_name: str,
    destination_file_name: Optional[str] = None,
) -> str:
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    destination = destination_file_name if destination_file_name is not None else os.path.basename(source_blob_name)
    blob.download_to_filename(destination)
    print(f"Downloaded gs://{bucket_name}/{source_blob_name} to {destination}")
    return destination


def download_folder(
    client: storage.Client,
    bucket_name: str,
    source_folder: str,
    destination_folder: Optional[str] = None,
) -> Summary:
    summary = {"downloaded": 0, "skipped": 0}
    if destination_folder is None:
        destination_folder = source_folder

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    blobs = list_blobs(client, bucket_name, prefix=source_folder)
    normalized_source = source_folder
    if normalized_source and not normalized_source.endswith('/'):
        normalized_source = f"{normalized_source}/"

    for blob in blobs:
        relative_path = blob.name
        if normalized_source and relative_path.startswith(normalized_source):
            relative_path = relative_path[len(normalized_source):]
        if not relative_path:
            summary["skipped"] += 1
            continue

        local_path = os.path.join(destination_folder, relative_path)
        local_dir = os.path.dirname(local_path)
        if local_dir and not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)

        download_blob(client, bucket_name, blob.name, local_path)
        summary["downloaded"] += 1
    return summary


def clean_folder(client: storage.Client, bucket_name: str, folder_path: str) -> int:
    bucket = client.bucket(bucket_name)
    if not folder_path.endswith('/'):
        folder_path += '/'

    blobs = list(bucket.list_blobs(prefix=folder_path))
    if not blobs:
        return 0
    bucket.delete_blobs(blobs)
    return len(blobs)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Cloud Storage Utility CLI")
    parser.add_argument("--bucket", required=True, help="GCS Bucket name")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True
    
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
    json_mode_group = json_parser.add_mutually_exclusive_group()
    json_mode_group.add_argument("--fail-fast", action="store_true", help="Stop at first failed upload")
    json_mode_group.add_argument("--best-effort", action="store_true", help="Continue after failures (default)")

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
    clean_parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")

    subparsers.add_parser("custom", help="Run in-code functions")

    args = parser.parse_args()

    # Initialize Client
    try:
        cli = storage.Client()
    except Exception as e:
        print("Error initializing Google Cloud Client. Ensure credentials are set.")
        print(e)
        sys.exit(1)

    # Route commands
    result: CommandResult = {"command": args.command, "bucket": args.bucket, "status": "ok"}
    exit_code = 0

    try:
        if args.command == "upload-folder":
            summary = upload_folder(cli, args.bucket, args.source, args.prefix, args.suffix)
            result.update(summary)

        elif args.command == "download-folder":
            summary = download_folder(cli, args.bucket, args.remote_folder, args.local_path)
            result.update(summary)

        elif args.command == "upload-bytes":
            result.update(upload_bytes(cli, args.bucket, args.data, args.filename, args.prefix))

        elif args.command == "upload-url":
            result.update(upload_url(cli, args.bucket, args.url, args.filename, args.prefix, timeout=args.timeout))

        elif args.command == "upload-json":
            summary = upload_json(
                cli,
                args.bucket,
                args.json_path,
                args.prefix,
                key=args.key,
                timeout=args.timeout,
                fail_fast=args.fail_fast,
            )
            result.update(summary)
            if summary.get("failed", 0) > 0:
                result["status"] = "error"
                exit_code = 1

        elif args.command == "list":
            blobs = list_blobs(cli, args.bucket, args.prefix)
            names = [blob.name for blob in blobs]
            for name in names:
                print(name)
            result["count"] = len(names)

        elif args.command == "download-file":
            destination = download_blob(cli, args.bucket, args.blob_name, args.local_path)
            result["downloaded"] = 1
            result["destination"] = destination

        elif args.command == "clean":
            should_clean = args.yes
            if not args.yes:
                if not sys.stdin.isatty():
                    raise RuntimeError("Refusing non-interactive clean without --yes.")
                confirm = input(f"Are you sure you want to delete everything in '{args.folder}'? (y/n): ")
                should_clean = confirm.lower().strip() == "y"

            if should_clean:
                deleted = clean_folder(cli, args.bucket, args.folder)
                result["deleted"] = deleted
                print(f"Deleted {deleted} objects from '{args.folder}'.")
            else:
                result["aborted"] = True
                print("Clean aborted.")

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        exit_code = 1

    emit_result(result)
    sys.exit(exit_code)
