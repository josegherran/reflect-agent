# Makefile for reflect-agent

.PHONY: install lint format typecheck test coverage run

install:
	uv pip install -e ".[dev]"

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .

typecheck:
	mypy agent/ config.py main.py

test:
	pytest tests/ -v

coverage:
	pytest tests/ --cov=agent --cov=ui --cov=config --cov-report=term-missing --cov-fail-under=80

run:
	python main.py
