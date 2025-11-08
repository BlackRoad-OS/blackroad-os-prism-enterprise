# Spiral metrics quickstart

This directory collects minimal CLIs around the pitch invariant ``c = d\ln r / d\theta`` so experiments can stay reproducible and scriptable.

## Claims
- `spiral_pitch.py` estimates the logarithmic pitch and spiralness of complex traces.

## Run
```bash
python -m tools.metrics.spiral_pitch samples.csv --real real --imag imag
```

## Good looks like
- Stable pitch estimates across repeated runs (|Δc| < 5e-3).
- Spiralness ≥ 0.85 when the data hugs a clean log spiral.
