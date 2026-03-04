#!/bin/bash
# Initial setup script for LegalFinance RAG

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create .env from template if it doesn't exist
if [ ! -f .env ]; then
  cp .env.example .env
  echo ".env created from template. Please update with your GROQ_API_KEY."
fi

# Create data directories
mkdir -p data/raw/tax data/raw/finance data/raw/legal data/processed

echo "Setup COMPLETE."
