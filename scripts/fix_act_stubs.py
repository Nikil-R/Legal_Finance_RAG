"""
Fix stub act files by aggregating ALL sections from HuggingFace Indian-Laws dataset.
Each act file will contain all its sections concatenated — rich, real, full legal text.
"""
import re
from pathlib import Path
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

ACTS_DIR = Path("data/raw/tax/acts")
ACTS_DIR.mkdir(parents=True, exist_ok=True)

TAX_KEYWORDS = [
    "tax", "finance", "revenue", "customs", "excise", "tariff",
    "cess", "gst", "goods", "sales", "income", "wealth", "duty"
]

def safe_filename(name: str) -> str:
    name = re.sub(r"[^\w\s\-]", "_", name).strip().replace(" ", "_")
    return re.sub(r"_+", "_", name)[:80]


def main():
    try:
        from datasets import load_dataset
    except ImportError:
        logging.error("Install datasets: pip install datasets")
        return

    logging.info("Loading mratanusarkar/Indian-Laws from HuggingFace...")
    ds = load_dataset("mratanusarkar/Indian-Laws", split="train")

    # Group all sections by act_title for tax-related acts
    act_sections = defaultdict(list)

    logging.info("Aggregating sections per act (tax-related only)...")
    for row in ds:
        title = row.get("act_title", "").strip()
        section = row.get("section", "").strip()
        if not title or not section:
            continue
        if any(kw in title.lower() for kw in TAX_KEYWORDS):
            act_sections[title].append(section)

    logging.info(f"Found {len(act_sections)} tax-related acts with real section text.")

    saved = 0
    for title, sections in act_sections.items():
        fname = safe_filename(title) + ".txt"
        fpath = ACTS_DIR / fname

        # Full combined text of title + all sections
        full_text = f"{title}\n{'=' * len(title)}\n\n"
        full_text += "\n\n---\n\n".join(sections)

        # Always overwrite stubs (< 300 bytes)
        if not fpath.exists() or fpath.stat().st_size < 300:
            fpath.write_text(full_text, encoding="utf-8")
            saved += 1
            logging.info(f"  ✓ Saved: {fname}  ({len(sections)} sections, {len(full_text)} chars)")

    logging.info(f"\nDone! Saved/enriched {saved} act files in {ACTS_DIR}")

    # Final count
    all_files = list(ACTS_DIR.glob("*.txt")) + list(ACTS_DIR.glob("*.pdf"))
    good_files = [f for f in all_files if f.stat().st_size >= 300]
    logging.info(f"Acts directory: {len(all_files)} total files, {len(good_files)} substantive (>=300 bytes)")


if __name__ == "__main__":
    main()
