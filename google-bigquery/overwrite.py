import os
from typing import List
from google.cloud.bigquery import *
from google.cloud.bigquery.table import TableListItem

PROJECT_ID = "project-b8819359-0bf9-4214-88d"
DATASET_ID = "financial_history"
SOURCE_DATA_DIR = "./financial"

def transform_schema(client: Client, full_table_id: str)-> List[SchemaField]:
    new_schema: List[SchemaField] = []
    try:
        table = client.get_table(full_table_id)
        original_schema = table.schema
        for field in original_schema: 
            if field.name == 'id':
                new_schema.append(
                    SchemaField(
                        name=field.name,
                        field_type=field.field_type,
                        mode='REQUIRED',
                        description=field.description,
                    )
                )
            else:
                new_schema.append(field)
        return new_schema
    except Exception as e:
        print(e)
        return []


def main():
    cli = Client(project=PROJECT_ID)
    dataset_ref = cli.dataset(DATASET_ID)
    tables: List[TableListItem] = list(cli.list_tables(dataset_ref))

    for table in tables:
        new_schema = transform_schema(cli, table)
        if not new_schema:
            continue

        # 3. Write or overwrite 
        if not os.path.exists(f"{SOURCE_DATA_DIR}/{table.table_id}.csv"):
            continue

        job_config = LoadJobConfig(
            schema=new_schema,
            skip_leading_rows=1,
            source_format=SourceFormat.CSV,
            write_disposition=WriteDisposition.WRITE_TRUNCATE,
        )

        try:
            with open(f"{SOURCE_DATA_DIR}/{table.table_id}.csv", "rb") as f:
                load_job = cli.load_table_from_file(
                    f,
                    dataset_ref.table(table.table_id),
                    job_config=job_config,
                )
                load_job.result()
        except Exception as e:
            print(e)

if __name__ == '__main__':
    main()