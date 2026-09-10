.PHONY: help install dev-install test test-unit test-integration lint format typecheck docker-up docker-down clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -e .

dev-install: ## Install development dependencies
	pip install -e ".[dev]"

test: ## Run all tests
	pytest

test-unit: ## Run unit tests only
	pytest tests/unit/

test-integration: ## Run integration tests only
	pytest tests/integration/

lint: ## Run linter
	ruff check .

format: ## Format code
	ruff format .

typecheck: ## Run type checker
	mypy .

docker-up: ## Start production services
	docker compose -f docker/docker-compose.yml up -d

docker-down: ## Stop production services
	docker compose -f docker/docker-compose.yml down

clean: ## Clean build artifacts
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
