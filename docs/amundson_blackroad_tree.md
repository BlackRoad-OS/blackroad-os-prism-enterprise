# Amundson–BlackRoad Buildout Tree

```
packages/
└── amundson_blackroad/
    ├── __init__.py
    ├── spiral.py        # AM-1/2/3 spiral kernels
    ├── autonomy.py      # BR-1/2 transport + BR-7 trust step
    ├── coupling.py      # BR-6 curvature ↔ a-field helpers
    ├── thermo.py        # Landauer helpers and provenance
    ├── resolution.py    # Auto-resolve coherence payloads (units + why-map)
    ├── projective.py    # AM-VI projective phase integrator
    ├── ladder.py        # AM-VII quadratic ladder invariants
    ├── chebyshev.py     # AM-VIII resonance metrics
    ├── collatz.py       # BR-8 Collatz flow instrument
    └── fib_pascal.py    # Fibonacci–Pascal invariants and golden step

srv/
└── lucidia-math/
    └── ui.py            # Flask service exposing AMBR endpoints + new instruments

tests/
└── …
    ├── test_am6_projective_phase.py
    ├── test_am7_quadratic_ladder.py
    ├── test_am8_chebyshev.py
    ├── test_br8_collatz.py
    ├── test_fib_pascal.py
    └── test_resolution.py

.github/
└── workflows/
    └── amundson-blackroad.yml  # Continuous validation (added in this sprint)
```
