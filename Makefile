.PHONY: setup test lint docs demo

setup:
pip install -e .[viz]

setup-qiskit:
pip install -e .[qiskit]

test:
pytest

lint:
ruff check quantum_lab tests
mypy quantum_lab

docs:
@echo "Docs available in docs/"

demo:
python quantum_lab/examples/bell_pair.py
python quantum_lab/examples/grover_demo.py
