import os
import time
import requests
from pathlib import Path
import logging
from googlesearch import search
import urllib.parse
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_pdfs(query, output_dir, limit=20):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"Searching google for: {query}")
    try:
        # We need authentic links
        links = list(search(query, num_results=30))
    except Exception as e:
        logging.error(f"Search failed: {e}")
        return

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    count = 0
    for link in links:
        if link.lower().endswith(".pdf") and count < limit:
            try:
                logging.info(f"Downloading from: {link}")
                res = requests.get(link, headers=headers, timeout=10)
                if res.status_code == 200:
                    raw_name = urllib.parse.unquote(link.split("/")[-1])
                    safe_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', raw_name)
                    if not safe_name.endswith('.pdf'):
                        safe_name += '.pdf'
                    
                    filepath = output_dir / safe_name
                    if not filepath.exists():
                        with open(filepath, 'wb') as f:
                            f.write(res.content)
                        count += 1
                        logging.info(f"Success. Saved {safe_name}")
                time.sleep(1)
            except Exception as e:
                logging.error(f"Failed to fetch {link}: {e}")

    logging.info(f"Successfully downloaded {count} authentic actual PDF documents for this category.")

if __name__ == "__main__":
    logging.info("Starting Download of Authentic Indian Tax Circulars & Notifications via Google Search...")
    download_pdfs('filetype:pdf "Central Board of Direct Taxes" "Circular"', 'data/raw/tax/circulars', limit=20)
    download_pdfs('filetype:pdf "Central Board of Direct Taxes" "Notification"', 'data/raw/tax/notifications', limit=20)
