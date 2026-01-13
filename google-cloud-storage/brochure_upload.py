from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, List
import argparse
import io
import os
import subprocess

from PyPDF2 import PdfReader, PdfWriter
from google.cloud import storage

from main import upload_bytes

BUCKET_NAME = "crawled-clean"

def run_script(tgt, *args): 
    subprocess.run(['python3', tgt, *args])    

def run_all_brochure_crawlers():
    for file in os.listdir('./insurers'):
        if file.endswith('.py') and not file.startswith('download'):
            run_script(os.path.join('./insurers', file))
            
@dataclass
class File:
    blob_name: str
    payload: Any # pdf, csv, bytes, etc.

class DataPipeline:
    def __init__(self, folder: str, storage_client: storage.Client):
        self.folder = folder
        self.storage_client = storage_client
        self.files: List[File] = []
        self.cleaned_files: List[File] = []
    
    @abstractmethod
    def load(self):
        ...
    
    @abstractmethod
    def clean(self): 
        ...

    def get_file_bytes(self):
        ...
    
class AIAHandler(DataPipeline):
    label = 'aia'
    
    def __init__(self, filepath: str, cli: storage.Client):
        super().__init__(filepath, cli)
        # can also use dependency injection on uploading function
    
    def load(self):
        for filename in os.listdir(self.folder):
            if filename.endswith('.pdf'):
                with open(os.path.join(self.folder, filename), 'rb') as f:
                    bytes_stream = io.BytesIO(f.read())
                    pdf = PdfReader(bytes_stream)
                    self.files.append(File(filename, pdf))
        return self
    
    def clean(self):
        # remove last page
        for file in self.files:
            writer = PdfWriter()
            for page in range(len(file.payload.pages)-1):
                writer.add_page(file.payload.pages[page])
            
            with io.BytesIO() as f:
                writer.write(f)
                self.cleaned_files.append(File(file.blob_name, f.getvalue()))
            
            writer.close()
        return self
    
    def upload(self):
        for file in self.cleaned_files:
            upload_bytes(self.storage_client, BUCKET_NAME, file.payload, file.blob_name, self.label)
        
        return self

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run_all', help="Run all available crawlers")
    args = parser.parse_args()
    
    if args.run_all:
        run_all_brochure_crawlers()
        
    cli = storage.Client()
    aia = AIAHandler('./brochures/aia', cli)
    aia.load().clean().upload()