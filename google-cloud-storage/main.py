import os
from google.cloud import storage
from typing import List, Protocol

BUCKET_NAME = "crawled-raw"

class DataLoader(Protocol): # experiment
    ... 
    def load_data():
        ...

def upload_folder(client, bucket_name, source_folder, blob_prefix=None):
    bucket = client.get_bucket(bucket_name)
    for root, _, files in os.walk(source_folder):
        for file in files:
            local_path = os.path.join(root, file)
            remote_path = os.path.relpath(local_path, source_folder) if blob_prefix is None else f"{blob_prefix}/{remote_path}"

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

if __name__=="__main__":
    cli = storage.Client()
    
    # SAMPLE USE CASES
    upload_folder(cli, BUCKET_NAME, 'google-cloud-storage/test_folder', 'data')
    upload_bytes(cli, BUCKET_NAME, b"hello world", "test_bytes.txt")
    
    aia_files = list_blobs(cli, 'crawled-clean', 'aia')
    download_blob(cli, 'crawled-clean', aia_files[0].name, 'test_download.pdf')
