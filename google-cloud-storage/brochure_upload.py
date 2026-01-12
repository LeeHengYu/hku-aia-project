import argparse
import os
import subprocess

def run_script(tgt, *args): 
    subprocess.run(['python3', tgt, *args])    

def run_all_brochure_crawlers():
    for file in os.listdir('./insurers'):
        if file.endswith('.py') and not file.startswith('download'):
            run_script(os.path.join('./insurers', file))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run_all', help="Run all available crawlers")
    args = parser.parse_args()
    
    if args.run_all:
        run_all_brochure_crawlers()