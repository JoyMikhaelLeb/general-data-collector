.PHONY: help install test lint format run clean docker-build docker-run docker-push

# Default target
.DEFAULT_GOAL := help

# Variables
DOCKER_IMAGE = companies_house-crawler
DOCKER_TAG = latest
PYTHON = python3

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install dependencies (uses uv if available, otherwise pip)
	@echo "Installing dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "Using uv..."; \
		uv pip install --system aiohttp beautifulsoup4 lxml python-dotenv pytest pytest-asyncio pytest-cov black ruff mypy 2>/dev/null || true; \
	else \
		echo "Using pip..."; \
		pip3 install aiohttp beautifulsoup4 lxml python-dotenv pytest pytest-asyncio pytest-cov black ruff mypy 2>/dev/null || true; \
	fi
	@echo "✓ Dependencies installed"

test: ## Run tests with pytest
	@echo "Running tests..."
	pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

test-fast: ## Run tests without coverage
	@echo "Running fast tests..."
	pytest tests/ -v

lint: ## Run linting checks
	@echo "Running ruff..."
	ruff check .
	@echo "Running mypy..."
	mypy crawler.py

format: ## Format code with black
	@echo "Formatting code..."
	black .
	ruff check --fix .

run: ## Run the crawler
	@echo "Running crawler..."
	$(PYTHON) crawler.py

clean: ## Clean up generated files
	@echo "Cleaning up..."
	rm -rf __pycache__ .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run: ## Run crawler in Docker container
	@echo "Running Docker container..."
	docker run --rm \
		-v $$(pwd)/data:/app/data \
		$(DOCKER_IMAGE):$(DOCKER_TAG)

docker-test: ## Run tests in Docker container
	@echo "Running tests in Docker..."
	docker run --rm \
		$(DOCKER_IMAGE):$(DOCKER_TAG) \
		pytest tests/ -v

docker-shell: ## Open shell in Docker container
	@echo "Opening shell in container..."
	docker run --rm -it \
		-v $$(pwd)/data:/app/data \
		$(DOCKER_IMAGE):$(DOCKER_TAG) \
		/bin/bash

docker-push: ## Push Docker image to registry
	@echo "Pushing Docker image..."
	docker push $(DOCKER_IMAGE):$(DOCKER_TAG)

validate: lint test ## Run all validation checks

ci: install lint test ## Run CI pipeline

all: install lint test run ## Install, validate, and run
