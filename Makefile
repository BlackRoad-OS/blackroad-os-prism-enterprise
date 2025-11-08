.DEFAULT_GOAL := test

VENV ?= .venv
PYTHON ?= python3
SAFE_MODE ?= 1

export SAFE_MODE

.PHONY: install test demo encompass-demo clean

install:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && pip install -U pip wheel
	. $(VENV)/bin/activate && pip install -U pytest numpy scipy hypothesis

# Run all tests with repo root on PYTHONPATH
test: install
	. $(VENV)/bin/activate && SAFE_MODE=$(SAFE_MODE) PYTHONPATH=$(PWD) pytest -q

# Optional: run the headline demo
demo: install
	. $(VENV)/bin/activate && SAFE_MODE=$(SAFE_MODE) PYTHONPATH=$(PWD) python scripts/demo_amundson_math_core.py
        . $(VENV)/bin/activate && PYTHONPATH=$(PWD) python scripts/demo_amundson_math_core.py

encompass-demo: install
        . $(VENV)/bin/activate && PYTHONPATH=$(PWD) python scripts/encompass_demo.py --prompt "Who are we?" --pretty --output ui/lucidia_viewer/packets.json

clean:
        rm -rf $(VENV) .pytest_cache __pycache__ */__pycache__
