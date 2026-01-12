from abc import abstractmethod
from dataclasses import dataclass
from typing import List
import argparse
import io
import os
import subprocess

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
    payload: any # pdf, csv, bytes, etc.

class DataPipeline:
    def __init__(self, folder: str):
        self.folder = folder
        self.files: List[File] = []
        self.cleaned_files: List[File] = []
    
    @abstractmethod
    def load(self):
        ...
    
    @abstractmethod
    def clean(self): 
        ...
    
    @abstractmethod
    def get_file_bytes(self):
        ...
    
class AIAHandler(DataPipeline):
    label = 'aia'
    
    def __init__(self, filepath: str):
        super().__init__(filepath)
    
    def load(self):
        from PyPDF2 import PdfFileReader
        for filename in os.listdir(self.folder):
            if filename.endswith('.pdf'):
                with open(os.path.join(self.folder, filename), 'rb') as f:
                    pdf = PdfFileReader(f)
                    self.files.append(File(filename, pdf))
        return self
    
    def clean(self):
        # remove last page
        from PyPDF2 import PdfFileWriter
        for file in self.files:
            writer = PdfFileWriter()
            for page in range(file.payload.getNumPages()-1):
                writer.addPage(file.payload.getPage(page))
            
            with io.BytesIO() as f:
                writer.write(f)
                self.cleaned_files.append(File(file.blob_name, f.getvalue()))
        return self

    def get_file_bytes(self):
        return self.cleaned_files

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run_all', help="Run all available crawlers")
    args = parser.parse_args()
    
    if args.run_all:
        run_all_brochure_crawlers()
        
    from google.cloud import storage
    
    aia = AIAHandler('./brochures/aia')
    aia.load().clean()
    
    for f in aia.get_file_bytes():
        cli = storage.Client()
        upload_bytes(cli, BUCKET_NAME, f.payload, f.blob_name, aia.label)