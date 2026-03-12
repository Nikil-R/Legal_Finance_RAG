"""
Document Loader — reads PDF and TXT files from the data directory.
"""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Number of parallel workers for file loading (I/O bound → threads are safe)
LOADER_MAX_WORKERS = 8


class DocumentLoader:
    """Loads PDF and TXT files from the directory tree."""

    def load_pdf(self, file_path: str) -> str:
        """Extract full text from a PDF file using pypdf."""
        try:
            import pypdf
            text_parts: list[str] = []
            with open(file_path, "rb") as fh:
                reader = pypdf.PdfReader(fh)
                for page_num, page in enumerate(reader.pages):
                    try:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                    except Exception as exc:
                        logger.warning(
                            "Failed to extract page %d from '%s': %s",
                            page_num, file_path, exc
                        )
            return "\n".join(text_parts)
        except Exception as exc:
            logger.warning("Could not read PDF '%s': %s", file_path, exc)
            return ""

    def load_json(self, file_path: str) -> str:
        """Read a JSON file and convert key fields to a text block."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
                data = json.load(fh)
            
            # Combine common fields into a searchable text block
            text_parts = []
            if "title" in data: text_parts.append(f"Title: {data['title']}")
            if "summary" in data: text_parts.append(f"Summary: {data['summary']}")
            if "key_holdings" in data: 
                holdings = "\n".join(data["key_holdings"]) if isinstance(data["key_holdings"], list) else str(data["key_holdings"])
                text_parts.append(f"Key Holdings:\n{holdings}")
            if "legal_principles" in data:
                principles = ", ".join(data["legal_principles"]) if isinstance(data["legal_principles"], list) else str(data["legal_principles"])
                text_parts.append(f"Legal Principles: {principles}")
            if "relevance_to_legal_finance_system" in data:
                text_parts.append(f"Business Relevance: {data['relevance_to_legal_finance_system']}")
            
            # If none of the above worked, just dump everything
            if not text_parts:
                return json.dumps(data, indent=2)
                
            return "\n\n".join(text_parts)
        except Exception as exc:
            logger.warning("Could not read JSON '%s': %s", file_path, exc)
            return ""

    def load_txt(self, file_path: str) -> str:
        """Read a plain-text file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
                return fh.read()
        except Exception as exc:
            logger.warning("Could not read TXT '%s': %s", file_path, exc)
            return ""

    def _load_single_file(self, file_path: Path, root: Path) -> dict | None:
        """Internal worker for parallel loading."""
        suffix = file_path.suffix.lower()
        if suffix not in {".pdf", ".txt", ".json"}:
            return None

        try:
            relative = file_path.relative_to(root)
            parts = relative.parts
            domain = parts[0] if len(parts) > 1 else "unknown"
        except ValueError:
            domain = "unknown"

        t0 = time.time()
        if suffix == ".pdf":
            content = self.load_pdf(str(file_path))
        elif suffix == ".json":
            content = self.load_json(str(file_path))
        else:
            content = self.load_txt(str(file_path))
        elapsed = time.time() - t0

        if not content.strip():
            logger.warning("Empty/unreadable content for '%s', skipping.", file_path)
            return None

        logger.info("Loaded '%s' (%.1fs, domain=%s)", file_path.name, elapsed, domain)

        return {
            "content": content,
            "metadata": {
                "source": file_path.name,
                "domain": domain,
                "file_path": str(file_path),
            },
        }

    def load_directory(self, directory_path: str) -> list[dict]:
        """Loads all .pdf and .txt files in parallel."""
        root = Path(directory_path)
        if not root.exists():
            logger.error("Directory '%s' does not exist.", directory_path)
            return []

        all_files = [f for f in root.rglob("*") if f.is_file()]
        eligible = [f for f in all_files if f.suffix.lower() in {".pdf", ".txt", ".json"}]

        logger.info(
            "Found %d eligible file(s) in '%s'. Loading (workers=%d) …",
            len(eligible), directory_path, LOADER_MAX_WORKERS
        )

        documents: list[dict] = []
        domain_counts: dict[str, int] = {}
        t_start = time.time()

        with ThreadPoolExecutor(max_workers=LOADER_MAX_WORKERS) as pool:
            futures = {pool.submit(self._load_single_file, fp, root): fp for fp in eligible}
            for future in as_completed(futures):
                res = future.result()
                if res:
                    documents.append(res)
                    d = res["metadata"]["domain"]
                    domain_counts[d] = domain_counts.get(d, 0) + 1

        logger.info(
            "Total: loaded %d document(s) in %.1fs. Domains: %s",
            len(documents), time.time() - t_start, domain_counts
        )
        return documents
