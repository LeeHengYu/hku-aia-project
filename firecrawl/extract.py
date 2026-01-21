import argparse
import json
import os
import re
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from insurers.download_file import download_file_from_url
except ImportError:
    print("Error: Could not import 'download_file_from_url'. Check yourdirectory structure.", file=sys.stderr)
    sys.exit(1)
    
OUTPUT_DIR = "brochures"

def sanitize_filename(name):
    if not name:
        return "unknown_filename"
    
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', name)
    cleaned = "".join(c for c in cleaned if c.isprintable()).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'_+', '_', cleaned)
    cleaned = re.sub(r'\s*_\s*', '_', cleaned)

    return cleaned

def main():
    parser = argparse.ArgumentParser(description="Download brochures from JSON data.")
    parser.add_argument(
        "-r", "--result", 
        required=True, 
        help="Path to the JSON results file"
    )
    args = parser.parse_args()

    if not os.path.exists(args.result):
        print(f"Error: File '{args.result}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(args.result, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Failed to decode JSON. {e}", file=sys.stderr)
            sys.exit(1)

    download_folder = os.path.join(current_dir, OUTPUT_DIR)
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    for item in data.get("brochures", []):
        url = item.get("pdf_url")
        product_name = item.get("product_name")

        if not url or not product_name:
            continue

        filename = sanitize_filename(f"{product_name}.pdf")
        file_path = os.path.join(download_folder, filename)

        try:
            download_file_from_url(
                file_url=url,
                file_path=file_path,
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=15
            )
        except Exception as e:
            print(f"Error downloading '{product_name}': {e}", file=sys.stderr)

if __name__ == "__main__":
    main()