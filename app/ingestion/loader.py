"""
Document Loader — reads PDF and TXT files from the domain-organised data/raw/ tree.

Each returned document dict has the shape:
    {
        "content": "<extracted text>",
        "metadata": {
            "source":    "<filename>",
            "domain":    "tax" | "finance" | "legal",
            "file_path": "<relative or absolute path>",
        }
    }
"""

from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Domains that are recognised as direct children of data/raw/
VALID_DOMAINS = {"tax", "finance", "legal"}


class DocumentLoader:
    """Loads PDF and TXT files from the data/raw/ directory tree."""

    # ------------------------------------------------------------------
    # Single-file loaders
    # ------------------------------------------------------------------

    def load_pdf(self, file_path: str) -> str:
        """
        Extract full text from a PDF file using PyPDF2.

        Returns an empty string if the file is corrupted or unreadable.
        """
        try:
            import PyPDF2  # type: ignore

            text_parts: list[str] = []
            with open(file_path, "rb") as fh:
                reader = PyPDF2.PdfReader(fh)
                for page_num, page in enumerate(reader.pages):
                    try:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                    except Exception as exc:  # noqa: BLE001
                        logger.warning(
                            "Failed to extract page %d from '%s': %s",
                            page_num,
                            file_path,
                            exc,
                        )
            return "\n".join(text_parts)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not read PDF '%s': %s", file_path, exc)
            return ""

    def load_txt(self, file_path: str) -> str:
        """Read a plain-text file and return its content."""
        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                return fh.read()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not read TXT '%s': %s", file_path, exc)
            return ""

    # ------------------------------------------------------------------
    # Directory walker
    # ------------------------------------------------------------------

    def load_directory(self, directory_path: str) -> list[dict]:
        """
        Recursively walk *directory_path* and load every .pdf / .txt file.

        The domain is derived from the name of the immediate child-folder
        under *directory_path* (e.g. data/raw/tax/ → domain "tax").
        Files that sit directly inside *directory_path* (not in a domain
        subfolder) are tagged with domain "unknown".

        Returns a list of document dicts.
        """
        root = Path(directory_path)
        if not root.exists():
            logger.error("Directory '%s' does not exist.", directory_path)
            return []

        documents: list[dict] = []
        domain_counts: dict[str, int] = {}

        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue

            suffix = file_path.suffix.lower()
            if suffix not in {".pdf", ".txt"}:
                continue

            # Derive domain from the first subfolder under root
            try:
                relative = file_path.relative_to(root)
                parts = relative.parts
                domain = parts[0] if len(parts) > 1 else "unknown"
            except ValueError:
                domain = "unknown"

            # Load content
            if suffix == ".pdf":
                content = self.load_pdf(str(file_path))
            else:
                content = self.load_txt(str(file_path))

            if not content.strip():
                logger.warning("Empty content for '%s', skipping.", file_path)
                continue

            doc = {
                "content": content,
                "metadata": {
                    "source": file_path.name,
                    "domain": domain,
                    "file_path": str(file_path),
                },
            }
            documents.append(doc)
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

        logger.info(
            "Loaded %d document(s) from '%s'. Per-domain: %s",
            len(documents),
            directory_path,
            domain_counts,
        )
        return documents
