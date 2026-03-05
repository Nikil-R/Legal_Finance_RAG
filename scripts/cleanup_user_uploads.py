"""
Cleanup job for old user-uploaded files.
"""

from __future__ import annotations

import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.config import settings


def main() -> None:
    base = Path("data/user_uploads")
    if not base.exists():
        print("No user upload directory found; nothing to clean")
        return

    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.USER_DOC_RETENTION_DAYS)
    removed = 0

    for session_dir in base.iterdir():
        if not session_dir.is_dir():
            continue
        modified = datetime.fromtimestamp(session_dir.stat().st_mtime, tz=timezone.utc)
        if modified < cutoff:
            shutil.rmtree(session_dir, ignore_errors=True)
            removed += 1

    print(
        f"Removed {removed} expired session directories "
        f"(retention={settings.USER_DOC_RETENTION_DAYS} days)"
    )


if __name__ == "__main__":
    main()
