.PHONY: install test lint audit pipeline app clean

VENV = .venv/bin
PYTHON = $(VENV)/python
STREAMLIT = $(VENV)/streamlit
PYTEST = $(VENV)/pytest
RUFF = $(VENV)/ruff

install:
	uv pip install -r requirements.txt

audit:
	$(PYTHON) -m src.profiling.profiler

pipeline:
	$(PYTHON) -m src.pipeline

test:
	$(PYTEST) tests/ -v

lint:
	$(RUFF) check src/ tests/

app:
	$(STREAMLIT) run src/app.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
