import os
import time
import requests
import zipfile
import shutil
import logging
from pathlib import Path
import subprocess
import sys

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dataset_downloader.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

BASE_DIR = Path("data/raw")

def download_legal_cuad():
    """Downloads the CUAD (Contract Understanding Atticus Dataset) containing 500+ commercial legal contracts."""
    legal_dir = BASE_DIR / "legal"
    legal_dir.mkdir(parents=True, exist_ok=True)
    
    zip_path = legal_dir / "cuad.zip"
    url = "https://zenodo.org/record/4595826/files/CUAD_v1.zip"
    
    extracted_txt_dir = legal_dir / "CUAD_v1" / "full_contract_txt"
    
    if list(legal_dir.glob("*.txt")) and len(list(legal_dir.glob("*.txt"))) > 50:
         logging.info("Legal (CUAD) documents already seem to be downloaded. Skipping.")
         return

    logging.info(f"Downloading CUAD Legal Contracts Dataset from {url} ... This may take a moment (~15MB compressed).")
    try:
        # User-Agent to prevent 403s
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    
        logging.info("Extracting CUAD dataset...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # We only extract the 'full_contract_txt' and 'full_contract_pdf' folders to save space
            for member in zip_ref.namelist():
                if "full_contract_txt/" in member or "full_contract_pdf/" in member:
                    zip_ref.extract(member, legal_dir)
                    
        zip_path.unlink() # clean up
        
        # Move a sample of 100 contracts to the root legal dir for easier ingestion
        txt_files = list((legal_dir / "CUAD_v1" / "full_contract_txt").glob("*.txt"))
        pdf_files = list((legal_dir / "CUAD_v1" / "full_contract_pdf").glob("*.pdf"))
        
        logging.info(f"Moving 50 TXT and 50 PDF contracts to {legal_dir}")
        for f in txt_files[:50]:
            shutil.copy(f, legal_dir / f.name)
        for f in pdf_files[:50]:
            shutil.copy(f, legal_dir / f.name)
            
        logging.info("CUAD Legal documents downloaded successfully.")
    except Exception as e:
        logging.error(f"Failed to download CUAD dataset: {e}")


def download_finance_filings():
    """Downloads Top 10 S&P 500 company SEC 10-K Filings for Finance RAG."""
    finance_dir = BASE_DIR / "finance"
    finance_dir.mkdir(parents=True, exist_ok=True)
    
    logging.info("Installing sec-edgar-downloader for Finance reports...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sec-edgar-downloader"])
    
    from sec_edgar_downloader import Downloader
    
    # Initialize the downloader with your company and email as required by SEC rules
    dl = Downloader("MyRAGProject", "student@example.com", finance_dir)
    
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B", "JPM", "V"]
    
    logging.info(f"Downloading SEC 10-K (Annual Reports) for Top 10 Tech/Finance companies...")
    for ticker in tickers:
        try:
            # Download the latest 10-K filing for each ticker
            logging.info(f"Fetching 10-K for {ticker}...")
            dl.get("10-K", ticker, limit=1, download_details=True)
            time.sleep(0.5) # respectful delay
        except Exception as e:
            logging.error(f"Failed to download 10-K for {ticker}: {e}")
    logging.info("Finance documents downloaded successfully.")


def download_irs_tax_pubs():
    """Downloads several extensive IRS Tax publications spanning hundreds of pages."""
    tax_dir = BASE_DIR / "tax" / "irs_pubs"
    tax_dir.mkdir(parents=True, exist_ok=True)
    
    pubs = {
        "Publication_17_Your_Federal_Income_Tax.pdf": "https://www.irs.gov/pub/irs-pdf/p17.pdf",
        "Publication_334_Tax_Guide_for_Small_Business.pdf": "https://www.irs.gov/pub/irs-pdf/p334.pdf",
        "Publication_505_Tax_Withholding.pdf": "https://www.irs.gov/pub/irs-pdf/p505.pdf",
        "Publication_525_Taxable_and_Nontaxable_Income.pdf": "https://www.irs.gov/pub/irs-pdf/p525.pdf",
        "Publication_590_A_IRAs.pdf": "https://www.irs.gov/pub/irs-pdf/p590a.pdf"
    }

    headers = {"User-Agent": "Mozilla/5.0"}
    
    for filename, url in pubs.items():
        filepath = tax_dir / filename
        if filepath.exists():
            continue
            
        logging.info(f"Downloading Tax Document: {filename}")
        try:
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            time.sleep(1) # respectful delay
        except Exception as e:
            logging.error(f"Failed to download {url}: {e}")
            
    logging.info("IRS Tax documents downloaded successfully.")


def main():
    logging.info("Starting Open-Source RAG Dataset Downloader...")
    
    # 1. Legal Domain (Contracts)
    download_legal_cuad()
    
    # 2. Finance Domain (SEC Filings)
    download_finance_filings()
    
    # 3. Tax Domain (IRS Pubs - Bypasses IndiaGov 503 issues by using US Gov Open Data instead)
    download_irs_tax_pubs()
    
    logging.info("All domain datasets downloaded properly. Your data/raw/ directory is now ready for RAG ingestion!")

if __name__ == "__main__":
    main()
