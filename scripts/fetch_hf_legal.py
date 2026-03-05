import os
import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        from datasets import load_dataset
    except ImportError:
        logging.error("Failed to import HuggingFace datasets library. Run: pip install datasets")
        return

    legal_dir = Path("data/raw/legal")
    legal_dir.mkdir(parents=True, exist_ok=True)
    
    logging.info("Downloading LexGLUE (Ledgar - Legal Contracts) dataset from HuggingFace...")
    # LexGLUE Ledgar contains thousands of contract provisions. It is widely used for Legal AI.
    dataset = load_dataset("lex_glue", "ledgar", split="train")
    
    count = 0
    target_count = 100 # How many contracts to create
    
    logging.info(f"Extracting {target_count} legal contracts into text files...")
    for i, item in enumerate(dataset):
        # We'll use the provision type as the filename with an index
        label = item['label']
        text = item['text']
        
        safe_title = f"contract_clause_{label}_{i}"
        filepath = legal_dir / f"{safe_title}.txt"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
            
        count += 1
        
        if count >= target_count:
            break
                
    logging.info(f"Successfully saved {count} legal documents to {legal_dir}.")

if __name__ == "__main__":
    main()
