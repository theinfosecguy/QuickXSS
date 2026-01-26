PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python

.PHONY: venv install test isort
.PHONY: itest

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(PIP) install -e '.[dev]'

test: install
	$(VENV)/bin/pytest

itest: install
	QUICKXSS_INTEGRATION=1 $(VENV)/bin/pytest -m integration

isort: install
	$(VENV)/bin/isort quickxss tests
