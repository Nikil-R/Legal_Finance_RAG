"""
Backup utility for Chroma persist directory.
"""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Backup Chroma DB directory")
    parser.add_argument("--source", default="./chroma_db")
    parser.add_argument("--target-dir", default="./backups")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    target_dir = Path(args.target_dir).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    if not source.exists():
        raise FileNotFoundError(f"Source directory not found: {source}")

    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    archive_base = target_dir / f"chroma_backup_{stamp}"
    archive_path = shutil.make_archive(str(archive_base), "zip", root_dir=source)
    print(f"Backup created: {archive_path}")


if __name__ == "__main__":
    main()
