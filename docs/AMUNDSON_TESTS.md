# Amundson Test Pack (Set I)

**What this validates**
- Unified harmonic operator: finite, non-zero contour integral.
- Fourier analyzer: finds 5 Hz and 10 Hz in a synthetic signal.
- Ramanujan square: row/col/diag magic constraint holds.
- Lindbladian (GKSL): dissipator returns Hermitian derivative.
- Number theory utils: φ(30)=8, μ(60)=0, μ(30)=-1, factors(60)=[2,2,3,5].

**Install & run**
```bash
python -m venv .venv && . .venv/bin/activate
pip install -U pip pytest numpy scipy
pytest -q
# optional demo
python scripts/demo_amundson_math_core.py
```

**File map**

* `tests/test_*.py` → fast, deterministic tests (<1s each)
* `scripts/demo_amundson_math_core.py` → prints a headline from each module

**Notes**

* Tests import from `agents.blackroad_agent_framework_package5`.
* If class names shift, tweak the imports at the top of each test.

