"""
Indian Kanoon Scraper for Tax Acts & Circulars
=================================================
Indian Kanoon (indiankanoon.org) is publicly accessible and contains
the full text of all Indian Acts, CBDT Circulars, and Notifications.
This script:
  1. Searches for each stub act on Indian Kanoon and downloads its full text
  2. Searches for CBDT circulars (2020-2024) and saves them
  3. Searches for CBDT notifications (2020-2024) and saves them
"""

import re
import time
import logging
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("kanoon_scraper.log", mode="w", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
}
BASE_URL = "https://indiankanoon.org"
SEARCH_URL = "https://indiankanoon.org/search/?formInput={query}&pagenum=0"
DELAY = 1.5  # seconds between requests — be respectful


def safe_filename(name: str, ext=".txt") -> str:
    name = re.sub(r"[^\w\s\-]", "_", name).strip().replace(" ", "_")
    name = re.sub(r"_+", "_", name)[:100]
    return name + ext


def search_kanoon(query: str) -> list[dict]:
    """Search Indian Kanoon and return list of {title, url, snippet}."""
    url = SEARCH_URL.format(query=quote_plus(query))
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for item in soup.select("div.result"):
            a = item.select_one("a.result_title")
            snippet_el = item.select_one("div.snippet")
            if a:
                results.append({
                    "title": a.get_text(strip=True),
                    "url": BASE_URL + a["href"] if a["href"].startswith("/") else a["href"],
                    "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                })
        return results
    except Exception as e:
        logging.warning(f"  Search failed for '{query}': {e}")
        return []


def fetch_document_text(url: str) -> str:
    """Fetch the full text of a document from Indian Kanoon."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # The main content is in #judgments div (or similar)
        content_div = (
            soup.select_one("#judgments")
            or soup.select_one(".judgment")
            or soup.select_one("#doc_content")
            or soup.select_one("div#docContent")
        )
        if content_div:
            text = content_div.get_text(separator="\n", strip=True)
        else:
            # Fallback: grab all paragraphs
            paras = soup.select("p")
            text = "\n\n".join(p.get_text(strip=True) for p in paras if len(p.get_text(strip=True)) > 30)

        return text.strip()
    except Exception as e:
        logging.warning(f"  Failed to fetch {url}: {e}")
        return ""


##############################################################################
# 1. ENRICH STUB ACT FILES
##############################################################################

def enrich_stub_acts():
    acts_dir = Path("data/raw/tax/acts")

    stubs = [f for f in acts_dir.glob("*.txt") if f.stat().st_size < 300]
    logging.info(f"Found {len(stubs)} stub act files to enrich from Indian Kanoon.")

    enriched = 0
    for stub in stubs:
        # Convert filename back to act name
        act_name = stub.stem.replace("_", " ").strip()
        logging.info(f"  Searching Indian Kanoon for: {act_name}")

        results = search_kanoon(f'"{act_name}" site:indiankanoon.org')
        if not results:
            results = search_kanoon(act_name)

        if not results:
            logging.warning(f"    No results found for: {act_name}")
            time.sleep(DELAY)
            continue

        # Take best match (top result that seems most relevant)
        best = next(
            (r for r in results if any(w in r["title"].lower() for w in act_name.lower().split()[:3])),
            results[0],
        )

        logging.info(f"    Fetching: {best['title']} from {best['url']}")
        text = fetch_document_text(best["url"])

        if len(text) > 300:
            full_content = f"{best['title']}\n{'=' * len(best['title'])}\n\nSource: {best['url']}\n\n{text}"
            stub.write_text(full_content, encoding="utf-8")
            logging.info(f"    ✓ Enriched {stub.name} ({len(text)} chars)")
            enriched += 1
        else:
            logging.warning(f"    ✗ Insufficient text returned ({len(text)} chars)")

        time.sleep(DELAY)

    logging.info(f"  Enriched {enriched}/{len(stubs)} stub acts.")


##############################################################################
# 2. DOWNLOAD CBDT CIRCULARS
##############################################################################

def download_cbdt_circulars():
    circ_dir = Path("data/raw/tax/circulars")
    circ_dir.mkdir(parents=True, exist_ok=True)

    circular_queries = [
        ("CBDT Circular 1 2024 income tax", "Circular_1_2024"),
        ("CBDT Circular 2 2024 income tax", "Circular_2_2024"),
        ("CBDT Circular 3 2024 income tax", "Circular_3_2024"),
        ("CBDT Circular 4 2024 income tax TDS", "Circular_4_2024_TDS"),
        ("CBDT Circular 5 2024 income tax", "Circular_5_2024"),
        ("CBDT Circular 1 2023 income tax", "Circular_1_2023"),
        ("CBDT Circular 3 2023 income tax", "Circular_3_2023"),
        ("CBDT Circular 5 2023 income tax", "Circular_5_2023"),
        ("CBDT Circular 7 2023 condonation delay refund", "Circular_7_2023_Condonation"),
        ("CBDT Circular 10 2023 charitable trust registration", "Circular_10_2023_Trusts"),
        ("CBDT Circular 12 2023 income tax", "Circular_12_2023"),
        ("CBDT Circular 1 2022 income tax", "Circular_1_2022"),
        ("CBDT Circular 6 2022 safe harbour rules", "Circular_6_2022_SafeHarbour"),
        ("CBDT Circular 18 2022 TDS", "Circular_18_2022_TDS"),
        ("CBDT Circular 5 2021 TDS 194Q", "Circular_5_2021_TDS194Q"),
        ("CBDT Circular 10 2021 TDS clarification", "Circular_10_2021_TDS"),
        ("CBDT Circular 13 2021 income tax", "Circular_13_2021"),
        ("CBDT Circular 9 2020 COVID relief income tax", "Circular_9_2020_COVID"),
        ("CBDT Circular 10 2020 COVID extension", "Circular_10_2020_COVID"),
        ("CBDT Circular 11 2020 income tax", "Circular_11_2020"),
    ]

    logging.info(f"=== Downloading/enriching CBDT Circulars from Indian Kanoon ===")
    for query, fname_base in circular_queries:
        dest = circ_dir / f"{fname_base}.txt"
        if dest.exists() and dest.stat().st_size > 500:
            logging.info(f"  Already exists: {dest.name}")
            continue

        logging.info(f"  Searching: {query}")
        results = search_kanoon(query)
        if not results:
            logging.warning(f"    No results for: {query}")
            time.sleep(DELAY)
            continue

        # Pick the most relevant result
        cbdt_results = [r for r in results if "cbdt" in r["title"].lower() or "circular" in r["title"].lower()]
        best = cbdt_results[0] if cbdt_results else results[0]

        text = fetch_document_text(best["url"])
        if len(text) > 300:
            full_content = f"{best['title']}\n{'=' * len(best['title'])}\n\nSource: {best['url']}\n\n{text}"
            dest.write_text(full_content, encoding="utf-8")
            logging.info(f"    ✓ Saved {dest.name} ({len(text)} chars)")
        else:
            logging.warning(f"    ✗ Insufficient text for {fname_base}")

        time.sleep(DELAY)

    existing = list(circ_dir.glob("*.txt")) + list(circ_dir.glob("*.pdf"))
    logging.info(f"  Circulars directory now has {len(existing)} files")


##############################################################################
# 3. DOWNLOAD CBDT NOTIFICATIONS
##############################################################################

def download_cbdt_notifications():
    notif_dir = Path("data/raw/tax/notifications")
    notif_dir.mkdir(parents=True, exist_ok=True)

    notification_queries = [
        ("CBDT Notification Cost Inflation Index 2024", "Notification_CPI_2024"),
        ("CBDT Notification PAN Aadhaar linking 2024", "Notification_PAN_Aadhaar_2024"),
        ("CBDT Notification income tax returns ITR forms 2024", "Notification_ITR_Forms_2024"),
        ("CBDT Notification Cost Inflation Index 2023", "Notification_CPI_2023"),
        ("CBDT Notification 44 2023 ITR income tax forms", "Notification_44_2023_ITR"),
        ("CBDT Notification income tax 2023 faceless assessment", "Notification_Faceless_2023"),
        ("CBDT Notification DTAA double tax avoidance 2022", "Notification_DTAA_2022"),
        ("CBDT Notification 111 2022 mandatory return filing", "Notification_111_2022_Return"),
        ("CBDT Notification income tax 2022 e-filing", "Notification_Efiling_2022"),
        ("CBDT Notification Faceless Assessment Scheme 2021", "Notification_Faceless_2021"),
        ("CBDT Notification 19 2021 faceless assessment income tax", "Notification_19_2021_Faceless"),
        ("CBDT Notification 22 2021 income tax rules", "Notification_22_2021"),
        ("CBDT Notification COVID relief income tax 2020", "Notification_COVID_2020"),
        ("CBDT Notification 37 2020 income tax extension deadline", "Notification_37_2020_Extension"),
        ("CBDT Notification 38 2020 income tax", "Notification_38_2020"),
    ]

    logging.info(f"=== Downloading/enriching CBDT Notifications from Indian Kanoon ===")
    for query, fname_base in notification_queries:
        dest = notif_dir / f"{fname_base}.txt"
        if dest.exists() and dest.stat().st_size > 500:
            logging.info(f"  Already exists: {dest.name}")
            continue

        logging.info(f"  Searching: {query}")
        results = search_kanoon(query)
        if not results:
            logging.warning(f"    No results for: {query}")
            time.sleep(DELAY)
            continue

        best = results[0]
        text = fetch_document_text(best["url"])
        if len(text) > 300:
            full_content = f"{best['title']}\n{'=' * len(best['title'])}\n\nSource: {best['url']}\n\n{text}"
            dest.write_text(full_content, encoding="utf-8")
            logging.info(f"    ✓ Saved {dest.name} ({len(text)} chars)")
        else:
            logging.warning(f"    ✗ Insufficient text for {fname_base}")

        time.sleep(DELAY)

    existing = list(notif_dir.glob("*.txt")) + list(notif_dir.glob("*.pdf"))
    logging.info(f"  Notifications directory now has {len(existing)} files")


##############################################################################
# FINAL AUDIT
##############################################################################

def audit():
    base = Path("data/raw")
    logging.info("\n" + "=" * 60)
    logging.info("FINAL AUDIT")
    logging.info("=" * 60)
    total = 0
    for cat in sorted(base.rglob("*")):
        if cat.is_dir():
            files = [f for f in cat.iterdir() if f.is_file() and not f.name.startswith(".")]
            big   = [f for f in files if f.stat().st_size >= 300]
            if files:
                logging.info(f"  {cat.relative_to(base)}: {len(files)} files ({len(big)} substantive ≥300B)")
                total += len(files)
    logging.info(f"\nTOTAL: {total} documents in data/raw/")


if __name__ == "__main__":
    logging.info("Starting comprehensive Indian Kanoon download...")
    enrich_stub_acts()
    download_cbdt_circulars()
    download_cbdt_notifications()
    audit()
    logging.info("✅ All done!")
