# Amundson–BlackRoad Buildout Tree

```
packages/
└── amundson_blackroad/
    ├── __init__.py
    ├── spiral.py        # AM-1/2/3 spiral kernels
    ├── autonomy.py      # BR-1/2 transport + BR-7 trust step
    ├── coupling.py      # BR-6 curvature ↔ a-field helpers
    └── thermo.py        # Landauer helpers and provenance

srv/
└── lucidia-math/
    └── ui.py            # Flask service exposing AMBR endpoints

tests/
└── test_amundson_blackroad.py  # V1–V4 validation suite

.github/
└── workflows/
    └── amundson-blackroad.yml  # Continuous validation (added in this sprint)
```
