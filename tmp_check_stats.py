import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from app.api.dependencies import get_retriever

def check_stats():
    retriever = get_retriever()
    stats = retriever.get_stats()
    print(f"Stats: {stats}")

if __name__ == "__main__":
    check_stats()
