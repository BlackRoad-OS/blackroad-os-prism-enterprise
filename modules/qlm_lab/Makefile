.PHONY: setup demo test lint notebooks
setup:
python -m venv .venv && . .venv/bin/activate && pip install -e .[viz] -r requirements-dev.txt || true

demo:
python -m qlm_lab.demos.demo_bell

test:
pytest -q

lint:
ruff check . && mypy qlm_lab

notebooks:
jupyter nbconvert --to notebook --execute notebooks/01_bell_chsh.ipynb --output out01.ipynb
