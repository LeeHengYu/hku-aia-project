import argparse
import os
from google.cloud import storage
from typing import List

BUCKET_NAME = "crawled-clean"

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
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_path)
            print(f"Uploaded {local_path} to {remote_path}")

def upload_bytes(client, bucket_name, data, destination_blob_name, blob_prefix=None):
    bucket = client.bucket(bucket_name)
    if blob_prefix is not None:
        destination_blob_name = f"{blob_prefix}/{destination_blob_name}"
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(data)
    print(f"Uploaded bytes to gs://{bucket_name}/{destination_blob_name}")

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Cloud Storage Utility CLI")
    parser.add_argument("--bucket", default=BUCKET_NAME, help=f"GCS Bucket name (default: {BUCKET_NAME})")
    
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
            
    else:
        parser.print_help()