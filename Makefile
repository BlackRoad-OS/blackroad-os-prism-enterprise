.PHONY: setup demo test lint notebooks

setup:
	python -m pip install -e .[dev]

DEMO_CMDS=\
	python -m qlm_lab.demos.demo_bell && \
	python -m qlm_lab.demos.demo_grover && \
	python -m qlm_lab.demos.demo_phase_reasoning && \
	python -m qlm_lab.demos.demo_codegen_tests

demo:
	$(DEMO_CMDS)

test:
	pytest

lint:
	ruff check qlm_lab tests/test_quantum_np.py tests/test_proto_and_policies.py tests/test_agents_loop.py
	mypy qlm_lab

notebooks:
	nbconvert --to notebook --execute notebooks/01_bell_chsh.ipynb
	nbconvert --to notebook --execute notebooks/02_grover_vs_bruteforce.ipynb
	nbconvert --to notebook --execute notebooks/03_qft_phase.ipynb
	nbconvert --to notebook --execute notebooks/04_codegen_with_selftests.ipynb
