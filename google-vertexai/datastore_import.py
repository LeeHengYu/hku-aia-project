from google.cloud import discoveryengine

project_id = "project-b8819359-0bf9-4214-88d"
location = "global"
data_store_id = "hku-market-analysis_1769864742906"

def import_from_gcs(uri):
    cli = discoveryengine.DocumentServiceClient()
    
    parent = cli.branch_path(
        project=project_id,
        location=location,
        data_store=data_store_id,
        branch="default_branch",
    )
    
    request = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=discoveryengine.GcsSource(
            input_uris=uri,
            data_schema="content",
        ),
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
    )
    
    operation = cli.import_documents(request=request)
    response = operation.result()
    print(response)
    
if __name__=="__main__": 
    uris = None
    with open("firecrawl/target.txt", "r") as f:
        uris = f.readlines()
    if uris is not None:
        uris = sorted(set(uri.strip() for uri in uris)) # cleaning
        import_from_gcs(uris)