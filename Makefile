SHELL := /bin/bash
POETRY := poetry

.PHONY: help install shell run test pytest tox docker-build docker-up docker-down logs migrate alembic-revision

help:
	@echo "Available targets:"
	@echo "  install        : Install dependencies with poetry"
	@echo "  shell          : Enter poetry shell"
	@echo "  run            : Run dev server (uvicorn)"
	@echo "  test           : Run pytest"
	@echo "  pytest         : Run pytest with optional TEST variable: make pytest TEST=src/unidades/test_unidades.py"
	@echo "  tox            : Run tox"
	@echo "  docker-build   : Build docker image"
	@echo "  docker-up      : Start services with docker-compose"
	@echo "  docker-down    : Stop services"
	@echo "  logs           : Tail docker-compose logs"
	@echo "  migrate        : Run alembic upgrade head"
	@echo "  lint           : Run linter (pylint)"
	@echo "  format         : Run code formatter (black)"
	@echo "  typecheck      : Run static type checks (mypy)"

install:
	$(POETRY) install

shell:
	$(POETRY) shell

run:
	$(POETRY) run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(POETRY) run pytest

pytest:
	$(POETRY) run pytest $(TEST)

lint:
	$(POETRY) run pylint src


tox:
	tox

docker-build:
	docker build -t paraiba-hotdog-back .

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down

logs:
	docker-compose logs -f

migrate:
	$(POETRY) run alembic upgrade head

alembic-revision:
	$(POETRY) run alembic revision --autogenerate -m "$(MSG)"
