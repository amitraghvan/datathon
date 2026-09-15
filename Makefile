.PHONY: install test test-ui test-all lint typecheck build backend frontend audit pipeline evaluate clean

VENV = .venv/bin
PYTHON = $(VENV)/python
PYTEST = $(VENV)/pytest
RUFF = $(VENV)/ruff

install:
	uv pip install -r requirements.txt
	cd frontend && npm install

audit:
	$(PYTHON) -m src.profiling.profiler

pipeline:
	$(PYTHON) -m src.pipeline

test:
	$(PYTEST) tests/ backend/tests/ -v

test-ui:
	npm test

test-all: test test-ui

lint:
	$(RUFF) check .
	npm run lint

typecheck:
	npm run typecheck

build:
	npm run build

backend:
	$(PYTHON) -m uvicorn backend.app.main:app --port 8000 --host 127.0.0.1 --reload

frontend:
	npm run dev

evaluate:
	$(PYTHON) evaluation/evaluate_llama.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

