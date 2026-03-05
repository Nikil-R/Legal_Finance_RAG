import os
import time
import logging
import re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Wait for 5 seconds to install playwright: pip install playwright && playwright install chromium
from playwright.sync_api import sync_playwright

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

SOURCES = {
    "circulars": "https://incometaxindia.gov.in/Pages/communications/circulars.aspx",
    "notifications": "https://incometaxindia.gov.in/Pages/communications/notifications.aspx",
    "acts": "https://incometaxindia.gov.in/Pages/acts/income-tax-act.aspx"
}

TARGET_YEARS = {str(year) for year in range(2020, 2025)}
BASE_DIR = Path("data/raw/tax")
DELAY = 2

def create_directories():
    for category in SOURCES.keys():
        dir_path = BASE_DIR / category
        dir_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Ensured directory exists: {dir_path}")

def is_target_year(text):
    return any(year in text for year in TARGET_YEARS)

def extract_metadata(text, category):
    safe_text = re.sub(r'[^a-zA-Z0-9_\-]', '_', text.replace(' ', '_'))
    safe_text = safe_text[:50].strip('_')
    year_found = next((y for y in TARGET_YEARS if y in text), "unknown_year")
    filename = f"{category}_{safe_text}_{year_found}.pdf"
    return re.sub(r'_+', '_', filename)

def main():
    logging.info("Starting Income Tax India document scraping process with Playwright...")
    create_directories()
    
    with sync_playwright() as p:
        # Connect to a real chromium browser engine to bypass WAF 503 Errors
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        for category, url in SOURCES.items():
            logging.info(f"--- Started scraping {category} ---")
            
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                # Wait for any anti-bot interstitial to pass
                time.sleep(DELAY) 
                
                content = page.content()
                with open(f"debug_{category}.html", "w", encoding="utf-8") as f:
                    f.write(content)
                soup = BeautifulSoup(content, 'html.parser')
                
                pdf_links = []
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if 'pdf' in href.lower() or 'document' in href.lower():
                        row_text = ""
                        parent_row = a.find_parent('tr')
                        if parent_row:
                            row_text = parent_row.get_text()
                        else:
                            row_text = a.get_text() + " " + (a.parent.get_text() if a.parent else "")

                        if is_target_year(row_text):
                            pdf_links.append((href, row_text))

                if not pdf_links:
                    logging.warning(f"No target PDF links found for {category}.")
                    continue

                logging.info(f"Found {len(pdf_links)} relevant documents for {category}.")

                for count, (href, row_text) in enumerate(pdf_links, 1):
                    full_url = urljoin(url, href)
                    filename = extract_metadata(row_text, category)
                    filepath = BASE_DIR / category / filename 
                    
                    if filepath.exists():
                        logging.info(f"Skipping already downloaded file: {filepath.name}")
                        continue
                        
                    logging.info(f"Downloading: {full_url} -> {filepath.name}")
                    try:
                        # Use Playwright's network stack to download the PDF
                        response = page.request.get(full_url, timeout=30000)
                        if response.ok:
                            with open(filepath, 'wb') as f:
                                f.write(response.body())
                            logging.info(f"Successfully saved: {filepath.name}")
                        else:
                            logging.error(f"Failed to download {full_url} - Status: {response.status}")
                    except Exception as e:
                        logging.error(f"Download exception for {full_url}: {e}")
                    finally:
                        time.sleep(DELAY)
                        
            except Exception as e:
                logging.error(f"Failed to access main page {url}: {e}")

        browser.close()
    
    logging.info("Scraping successfully completed!")

if __name__ == "__main__":
    main()
