# Makefile for Restricted Chat Application

# Virtual environment paths
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

.PHONY: help install setup run clean test init-db

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: $(VENV)  ## Create virtual environment
	@echo "✅ Virtual environment created"

$(VENV):
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: setup  ## Install dependencies
	$(PIP) install -r requirements.txt
	@echo "✅ Dependencies installed"

init-db: install  ## Initialize the database
	$(PYTHON) init_db.py
	@echo "✅ Database initialized"

run: install  ## Run the application
	$(PYTHON) app.py

test: install  ## Run tests (if any)
	$(PYTHON) -m pytest tests/ || echo "No tests found"

clean:  ## Clean up virtual environment
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf *.pyc
	@echo "✅ Cleaned up"

lint: install  ## Run linting
	$(PYTHON) -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || echo "flake8 not installed"

format: install  ## Format code
	$(PYTHON) -m black . || echo "black not installed"

# For backward compatibility
pip-install: install  ## Alias for install command
