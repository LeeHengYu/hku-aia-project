from abc import abstractmethod
from dataclasses import dataclass
from typing import List
import argparse
import io
import os
import subprocess

from PyPDF2 import PdfReader, PdfWriter
from google.cloud import storage

from kmp_util import kmpSearch
from upload_helper import upload_bytes

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
    payload: PdfReader | bytes # pdf only

class DataPipeline:
    def __init__(self, folder: str, storage_client: storage.Client):
        self.folder = folder
        self.storage_client = storage_client
        self.files: List[File] = []
        self.cleaned_files: List[File] = []
    
    def load(self):
        for filename in os.listdir(self.folder):
            if filename.endswith('.pdf'):
                try:
                    self.files.append(File(filename, PdfReader(os.path.join(self.folder, filename))))
                except:
                    continue
        return self
    
    @abstractmethod
    def clean(self): 
        ...
        
    def get_file_bytes(self):
        ...

    def upload(self):
        if not self.cleaned_files:
            raise Exception("No cleaned files to upload")
        
        for file in self.cleaned_files:
            upload_bytes(self.storage_client, BUCKET_NAME, file.payload, file.blob_name, self.label)
        
        return self
    
class AIAHandler(DataPipeline):
    label = 'aia'
    
    def __init__(self, filepath: str, cli: storage.Client):
        super().__init__(filepath, cli)
        # can also use dependency injection on uploading function
    
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

class FWDHandler(DataPipeline):
    label = 'fwd'
    banned_words = {
        'disclaimer',
        'important notes',
        'remark'
    }

    def __init__(self, filepath: str, cli: storage.Client):
        super().__init__(filepath, cli)

    def clean(self, copy_to_disk=False):
        for file in self.files:
            writer = PdfWriter()
            n_pages = len(file.payload.pages)
            for i in range(n_pages):
                flag = True
                
                s = file.payload.pages[i].extract_text()
                if (n_pages - 5 <= i <= n_pages - 1 and
                    any(kmpSearch(s.lower(), word) for word in self.banned_words)
                    ): # needs a faster string matching algo with lower time complexity, use kmp
                    flag = False

                if flag:
                    writer.add_page(file.payload.pages[i])
                
            with io.BytesIO() as f:
                writer.write(f)
                self.cleaned_files.append(File(file.blob_name, f.getvalue()))
            
            if copy_to_disk:
                with open(f"./brochures/copy/{FWDHandler.label}/{file.blob_name}", 'wb') as f:
                    writer.write(f)

            writer.close()
        return self

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run_all', help="Run all available crawlers")
    args = parser.parse_args()
    
    if args.run_all:
        run_all_brochure_crawlers()
        
    cli = storage.Client()
    # aia = AIAHandler('./brochures/aia', cli).load().clean().upload()
    # fwd = FWDHandler('./brochures/fwd', cli).load().clean().upload()