# Makefile for reflect-agent

.PHONY: install lint typecheck test run

install:
	uv pip install -r requirements.txt
	uv pip install -e .

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .

mypy:
	mypy .

typecheck: mypy

test:
	pytest

run:
	python main.py
