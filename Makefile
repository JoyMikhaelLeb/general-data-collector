.PHONY: help list install-all test-all clean-all docker-build-all docker-run-all

# Default target
.DEFAULT_GOAL := help

# Get all crawler directories
CRAWLER_DIRS := $(wildcard crawlers/*)
CRAWLER_NAMES := $(notdir $(CRAWLER_DIRS))

help: ## Show this help message
	@echo 'General Data Collector - Master Makefile'
	@echo ''
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}'
	@echo ''
	@echo 'Available crawlers:'
	@for crawler in $(CRAWLER_NAMES); do \
		echo "  - $$crawler"; \
	done

list: ## List all available crawlers
	@echo 'Available crawlers ($(words $(CRAWLER_NAMES)) total):'
	@for crawler in $(CRAWLER_NAMES); do \
		echo "  - $$crawler"; \
	done

install-all: ## Install dependencies for all crawlers
	@echo "Installing dependencies for all crawlers..."
	@for crawler in $(CRAWLER_DIRS); do \
		echo "Installing $$crawler..."; \
		cd $$crawler && make install && cd ../..; \
	done
	@echo "✓ All dependencies installed"

test-all: ## Run tests for all crawlers
	@echo "Running tests for all crawlers..."
	@for crawler in $(CRAWLER_DIRS); do \
		echo "Testing $$crawler..."; \
		cd $$crawler && make test-fast && cd ../..; \
	done
	@echo "✓ All tests completed"

lint-all: ## Run linting for all crawlers
	@echo "Running linting for all crawlers..."
	@for crawler in $(CRAWLER_DIRS); do \
		echo "Linting $$crawler..."; \
		cd $$crawler && make lint && cd ../..; \
	done
	@echo "✓ All linting completed"

format-all: ## Format code for all crawlers
	@echo "Formatting code for all crawlers..."
	@for crawler in $(CRAWLER_DIRS); do \
		echo "Formatting $$crawler..."; \
		cd $$crawler && make format && cd ../..; \
	done
	@echo "✓ All code formatted"

clean-all: ## Clean all crawler directories
	@echo "Cleaning all crawlers..."
	@for crawler in $(CRAWLER_DIRS); do \
		echo "Cleaning $$crawler..."; \
		cd $$crawler && make clean && cd ../..; \
	done
	@echo "✓ All crawlers cleaned"

docker-build-all: ## Build Docker images for all crawlers
	@echo "Building Docker images for all crawlers..."
	@for crawler in $(CRAWLER_NAMES); do \
		echo "Building $$crawler..."; \
		cd crawlers/$$crawler && make docker-build && cd ../..; \
	done
	@echo "✓ All Docker images built"

docker-compose-up: ## Start all crawlers with docker-compose
	@echo "Starting all crawlers..."
	docker-compose up

docker-compose-up-d: ## Start all crawlers in background
	@echo "Starting all crawlers in background..."
	docker-compose up -d

docker-compose-down: ## Stop all crawlers
	@echo "Stopping all crawlers..."
	docker-compose down

docker-compose-logs: ## View logs from all crawlers
	docker-compose logs -f

docker-compose-build: ## Build all crawler images with docker-compose
	@echo "Building all crawler images..."
	docker-compose build

# Individual crawler targets
install-%: ## Install dependencies for specific crawler (e.g., make install-harmonic_ai)
	@echo "Installing $*..."
	@cd crawlers/$* && make install

test-%: ## Run tests for specific crawler (e.g., make test-harmonic_ai)
	@echo "Testing $*..."
	@cd crawlers/$* && make test

run-%: ## Run specific crawler (e.g., make run-harmonic_ai)
	@echo "Running $*..."
	@cd crawlers/$* && make run

docker-build-%: ## Build Docker image for specific crawler
	@echo "Building Docker image for $*..."
	@cd crawlers/$* && make docker-build

docker-run-%: ## Run specific crawler in Docker
	@echo "Running $* in Docker..."
	@cd crawlers/$* && make docker-run

clean-%: ## Clean specific crawler
	@echo "Cleaning $*..."
	@cd crawlers/$* && make clean

# Development workflow
dev-setup: install-all ## Setup development environment
	@echo "Development environment ready!"

validate-all: lint-all test-all ## Validate all crawlers (lint + test)

ci: dev-setup validate-all ## Run full CI pipeline

# Data management
clean-data: ## Remove all collected data
	@echo "Cleaning all data directories..."
	@find crawlers -type d -name "data" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ All data cleaned"

# Statistics
stats: ## Show project statistics
	@echo "Project Statistics:"
	@echo "  Total crawlers: $(words $(CRAWLER_NAMES))"
	@echo "  Total Python files: $$(find crawlers -name '*.py' | wc -l)"
	@echo "  Total test files: $$(find crawlers -name 'test_*.py' | wc -l)"
	@echo "  Lines of code: $$(find crawlers -name '*.py' -exec wc -l {} + | tail -1 | awk '{print $$1}')"

# Documentation
docs: ## Generate documentation index
	@echo "# Crawler Documentation" > CRAWLERS.md
	@echo "" >> CRAWLERS.md
	@echo "Total crawlers: $(words $(CRAWLER_NAMES))" >> CRAWLERS.md
	@echo "" >> CRAWLERS.md
	@for crawler in $(CRAWLER_NAMES); do \
		echo "## $$crawler" >> CRAWLERS.md; \
		echo "" >> CRAWLERS.md; \
		echo "- Location: \`crawlers/$$crawler/\`" >> CRAWLERS.md; \
		echo "- [README](crawlers/$$crawler/README.md)" >> CRAWLERS.md; \
		echo "- [Architecture](crawlers/$$crawler/ARCHITECTURE.md)" >> CRAWLERS.md; \
		echo "" >> CRAWLERS.md; \
	done
	@echo "✓ Documentation index generated: CRAWLERS.md"
