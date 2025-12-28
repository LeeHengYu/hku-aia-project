import alibabacloud_oss_v2 as oss

BUCKET_ID = "hku-crawled-data"

# upload local files

def sample_data() -> bytes:
    return 'Hello world'.encode()

def local_data(filepath: str) -> bytes:
    try:
        with open(filepath, 'rb') as f:
            return f.read()
    except:
        raise FileNotFoundError("File not found.")
    
def list_all_files_and_directory(client):
    paginator = client.list_objects_v2_paginator()
    for page in paginator.iter_page(oss.ListObjectsV2Request(
            bucket=BUCKET_ID
        )
    ):
        for o in page.contents:
            print(f'Object: {o.key}, {o.size}, {o.last_modified}')
    

def main():
    # pre-configuration of credentials is needed.
    credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider
    cfg.region = 'cn-hongkong'
    
    client = oss.Client(cfg)
    
    res = client.put_object(oss.PutObjectRequest(
        bucket=BUCKET_ID,
        key="data/first-upload", # path
        body=sample_data(), # bytes, 
    ))
    
    print(f'status code: {res.status_code}\n'
          f'request id: {res.request_id}\n'
    )
    
    # list_all_files_and_directory(client)
    
if __name__=="__main__":
    main()