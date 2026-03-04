import os
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from evaluation.runner import main  # noqa: E402

if __name__ == "__main__":
    # Wrapper for evaluation runner CLI
    sys.exit(main())
