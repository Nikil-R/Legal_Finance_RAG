import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_tax_dir():
    tax_dir = Path("data/raw/tax")
    if tax_dir.exists():
        for category in ["acts", "circulars", "notifications"]:
            cat_dir = tax_dir / category
            if cat_dir.exists():
                for f in cat_dir.glob("*.txt"):
                    if f.is_file():
                        # Delete the mock files
                        f.unlink()
        logging.info("Cleaned previous mock files.")

def fetch_real_indian_tax_laws():
    try:
        from datasets import load_dataset
    except ImportError:
        logging.error("Failed to import datasets.")
        return

    # mratanusarkar/Indian-Laws has actual Indian Bare Acts
    logging.info("Downloading Indian Laws Dataset from HuggingFace...")
    dataset = load_dataset("mratanusarkar/Indian-Laws", split="train")

    acts_dir = Path("data/raw/tax/acts")
    acts_dir.mkdir(parents=True, exist_ok=True)
    
    count = 0
    # Search for keywords related to tax, revenue, customs, excise, finance
    tax_keywords = ["tax", "finance", "revenue", "customs", "excise", "tariff", "cess"]
    
    for item in dataset:
        title = item.get("act_title", "").lower()
        if any(keyword in title for keyword in tax_keywords):
             raw_title = item.get("act_title", "Unknown_Act").replace(" ", "_").replace("/", "_").replace('"', '')
             content = item.get("act_definition", "No Definition.")
             
             # Save real act
             safe_title = "".join(c for c in raw_title if c.isalnum() or c == '_')[:60]
             filepath = acts_dir / f"{safe_title}.txt"
             
             if not filepath.exists():
                 with open(filepath, "w", encoding="utf-8") as f:
                     f.write(item.get("act_title", "") + "\n\n")
                     f.write(content)
                 count += 1
                 
    logging.info(f"Successfully saved {count} genuine Indian Tax related acts from the dataset.")

if __name__ == "__main__":
    clean_tax_dir()
    fetch_real_indian_tax_laws()
