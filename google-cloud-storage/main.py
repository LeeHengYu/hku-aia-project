import os
from google.cloud import storage

BUCKET_NAME = "crawled-raw"


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

if __name__=="__main__":
    cli = storage.Client()
    # upload_folder(cli, BUCKET_NAME, 'google-cloud-storage/test_folder', 'data')

    upload_bytes(cli, BUCKET_NAME, b"hello world", "test_bytes.txt")