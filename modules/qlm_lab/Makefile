.PHONY: setup demo demo_toolcaller test lint notebooks gate
setup:
	python -m venv .venv && . .venv/bin/activate && pip install -e .[qiskit] pytest pytest-cov ruff mypy jupyter nbconvert

demo:
	python -m qlm_lab.demos.demo_bell

demo_toolcaller:
	python -m qlm_lab.demos.demo_toolcaller

test:
	pytest --cov=qlm_lab --cov-report=xml

lint:
	ruff check . && mypy qlm_lab

notebooks:
	jupyter nbconvert --to notebook --execute notebooks/01_bell_chsh.ipynb --output out01.ipynb

gate: test
