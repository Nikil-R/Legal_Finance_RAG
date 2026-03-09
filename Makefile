.PHONY: help install install-dev test test-unit test-integration lint format clean run-api run-frontend run-worker run-all ingest evaluate docker-build docker-up docker-down

# Default target
help:
	@echo "LegalFinance RAG - Available Commands"
	@echo "======================================"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install production dependencies"
	@echo "  make install-dev    Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run-api        Start FastAPI server"
	@echo "  make run-frontend   Start Streamlit frontend"
	@echo "  make run-worker     Start Celery ingestion worker"
	@echo "  make run-all        Start both API and frontend"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run all tests"
	@echo "  make test-unit      Run unit tests only"
	@echo "  make test-int       Run integration tests"
	@echo "  make lint           Run linters"
	@echo "  make format         Format code"
	@echo ""
	@echo "Data:"
	@echo "  make ingest         Run document ingestion"
	@echo "  make ingest-clear   Clear and re-ingest documents"
	@echo "  make evaluate       Run evaluation suite"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   Build Docker images"
	@echo "  make docker-up      Start Docker containers"
	@echo "  make docker-down    Stop Docker containers"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          Remove cache and temporary files"

# ============ Setup ============

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

# ============ Development ============

run-api:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	streamlit run frontend/app.py

run-worker:
	celery -A app.tasks.celery_app worker --loglevel=INFO

run-all:
	@echo "Starting API and Frontend..."
	@make run-api &
	@sleep 3
	@make run-frontend

# ============ Testing ============

test:
	pytest tests/ -v --tb=short

test-unit:
	pytest tests/unit -v --tb=short

test-int:
	pytest tests/integration -v --tb=short

test-cov:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

lint:
	ruff check .
	black --check .
	isort --check-only .

format:
	black .
	isort .
	ruff check --fix .

# ============ Data Operations ============

ingest:
	python -m app.ingestion.cli

ingest-clear:
	python -m app.ingestion.cli --clear

evaluate:
	python -m evaluation.runner --ci

evaluate-full:
	python -m evaluation.runner

# ============ Docker ============

docker-build:
	docker-compose -f docker/docker-compose.yml build

docker-up:
	docker-compose -f docker/docker-compose.yml up -d

docker-down:
	docker-compose -f docker/docker-compose.yml down

docker-logs:
	docker-compose -f docker/docker-compose.yml logs -f

# ============ Cleanup ============

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true
	rm -rf test_chroma_db/ 2>/dev/null || true
