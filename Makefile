.PHONY: setup dev test lint clean docker-build docker-run help

# Variables
PYTHON = python
PIP = pip
PYTEST = pytest
PORT = 8080
DOCKER_IMAGE = chatbot-api
DOCKER_TAG = latest

help:
	@echo "Available commands:"
	@echo "  make setup       - Install dependencies"
	@echo "  make dev         - Run development server"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run linting"
	@echo "  make clean       - Clean up build files"
	@echo "  make docker-build- Build Docker image"
	@echo "  make docker-run  - Run Docker container"

setup:
	$(PIP) install -r requirements.txt

dev:
	uvicorn app:app --reload --host 0.0.0.0 --port $(PORT)

test:
	$(PYTEST) -v --cov=. tests/

lint:
	# Install flake8 if not available
	$(PIP) install flake8 || true
	flake8 .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .coverage -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run:
	docker run -p $(PORT):$(PORT) \
		--env-file .env \
		$(DOCKER_IMAGE):$(DOCKER_TAG)

# Default target
.DEFAULT_GOAL := help 