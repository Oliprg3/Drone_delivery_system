SHELL := /bin/bash
PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
HOST ?= 0.0.0.0
PORT ?= 8000
AGENT ?= heuristic
STEPS ?= 1000

.DEFAULT_GOAL := help
.PHONY: help install install-dev install-all test lint format run train serve docker-build docker-up docker-down clean

help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install the package with the core dependencies
	$(PIP) install -e .

install-dev: ## Install with the development extras (pytest, ruff, httpx)
	$(PIP) install -e ".[dev]"

install-all: ## Install with every optional extra (api, viz, rl, dev)
	$(PIP) install -e ".[all]"

test: ## Run the test suite
	$(PYTHON) -m pytest

lint: ## Lint the source tree
	$(PYTHON) -m ruff check src tests

format: ## Auto-fix lint findings
	$(PYTHON) -m ruff check --fix src tests

run: ## Run a headless simulation with the heuristic policy
	$(PYTHON) -m drone_delivery.cli.run_simulation --agent $(AGENT) --headless --max-steps $(STEPS)

train: ## Train the PPO policy
	$(PYTHON) -m drone_delivery.cli.train --timesteps 10000

serve: ## Serve the HTTP API
	$(PYTHON) -m drone_delivery.cli.serve --host $(HOST) --port $(PORT)

docker-build: ## Build the container image
	docker compose build

docker-up: ## Start the API container
	docker compose up -d api

docker-down: ## Stop the containers
	docker compose down

clean: ## Remove build and cache artefacts
	rm -rf build dist artifacts .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
