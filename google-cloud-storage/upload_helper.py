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
    return list(blobs)

def download_blob(client, bucket_name, source_blob_name, destination_file_name):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    
def clean_folder(client, bucket_name, folder_path):
    bucket = client.bucket(bucket_name)
    if not folder_path.endswith('/'):
        folder_path += '/'
        
    blobs = list(bucket.list_blobs(prefix=folder_path))
    if not blobs:
        return
    bucket.delete_blobs(blobs)

if __name__=="__main__":
    cli = storage.Client()
    
    # SAMPLE USE CASES
    # upload_folder(cli, BUCKET_NAME, 'google-cloud-storage/test_folder', 'data')
    # upload_bytes(cli, BUCKET_NAME, b"hello world", "test_bytes.txt")
    
    # aia_files = list_blobs(cli, 'crawled-clean', 'aia')
    # download_blob(cli, 'crawled-clean', aia_files[0].name, 'test_download.pdf')
    
    clean_folder(cli, BUCKET_NAME, 'aia')
    # upload_folder(cli, BUCKET_NAME, 'financial', 'financial_data', '.csv')