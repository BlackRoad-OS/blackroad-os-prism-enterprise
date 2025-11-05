.PHONY: help install test lint format clean

help:  ## Show this help
@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

test:  ## Run tests
pytest --cov=orchestrator --cov-report=term-missing

lint:  ## Lint code
ruff check .
mypy orchestrator

format:  ## Format code
black .
ruff check --fix .

clean:  ## Clean artifacts
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name '*.pyc' -delete
rm -rf .pytest_cache .coverage .mypy_cache
rm -rf artifacts/*
# <!-- FILE: Makefile -->
.RECIPEPREFIX = >
.PHONY: install dev start format lint test health migrate clean

install:
>npm install

dev:
>npm run dev

start:
>npm start

format:
>npm run format

lint:
>npm run lint

test:
>npm test

health:
>npm run health

migrate:
>@echo "no migrations"

clean:
>rm -rf node_modules coverage
