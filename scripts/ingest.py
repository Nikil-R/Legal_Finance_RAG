import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ingestion.cli import main

if __name__ == "__main__":
    # Wrapper for document ingestion CLI
    sys.exit(main())
