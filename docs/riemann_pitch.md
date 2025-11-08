# Amundson–ζ Pitch (c_ζ)

Given $f(s) = \zeta(s)$ on $\Re(s) = \tfrac12$, define
\[
  c_\zeta(t) = \frac{\frac{\mathrm d}{\mathrm dt} \ln \lvert \zeta(\tfrac12 + it)\rvert}{\frac{\mathrm d}{\mathrm dt} \arg \zeta(\tfrac12 + it)}
\]
whenever the denominator is non-zero.

**Rationale**

- The argument principle relates the winding of $\arg \zeta$ around zeros to zero counts.
- $c_\zeta$ is the ratio of radial growth to angular sweep of $\zeta(s)$ as $s$ moves vertically.
- Near zeros both numerator and denominator are governed by $\zeta'/\zeta$; $c_\zeta$ captures the local geometry in a scalar.

**What to look for**

- Empirical distribution of $c_\zeta$ between consecutive zeros.
- Scaling of $c_\zeta$ statistics vs. zero height.
- Correlation between spikes in $c_\zeta$ and zero spacing (GUE heuristics).

No claim on the Riemann Hypothesis is made; this is a geometric diagnostic to organise data.

---

## Background

The Amundson spiral pitch captures how quickly a complex trajectory grows radially compared
with its angular sweep.  For an analytic function $f$ sampled along a path $\gamma(t)$ we write
\[
  c_f(t) = \frac{\frac{\mathrm d}{\mathrm dt} \ln \lvert f(\gamma(t))\rvert}{\frac{\mathrm d}{\mathrm dt} \arg f(\gamma(t))},
\]
whenever the denominator is non-zero.  On the Riemann critical line the path is $s(t) = \tfrac12 + it$,
and the logarithmic derivative of $\zeta$ decomposes neatly:
\[
  \frac{\mathrm d}{\mathrm dt} \log \zeta(s(t))
  = \frac{\mathrm d}{\mathrm dt}\big(\ln \lvert \zeta(s(t))\rvert + i\,\arg \zeta(s(t))\big)
  = i\,\frac{\zeta'(s(t))}{\zeta(s(t))}.
\]
The real part controls radial growth, the imaginary part controls angular motion, and their ratio is the pitch $c_\zeta(t)$.

## Using the tooling

The module `tools.number_theory.zeta_pitch` provides both a Python API and a command-line harness
for sampling the pitch with only `mpmath` (and optionally Matplotlib) as dependencies.

Typical Python usage mirrors the previous helper-centric workflow:

```python
from tools.number_theory import zeta_pitch

samples = zeta_pitch.sample_interval(14.0, 40.0, num_points=512)
zeta_pitch.write_csv(samples, "riemann_pitch.csv")
zeta_pitch.plot_pitch(samples, path="riemann_pitch.png")
```

The `write_csv` helper records $t$, $\zeta(\tfrac12 + it)$, the unwrapped phase, derivatives of
$\ln |\zeta|$ and $\arg \zeta$, plus the resulting pitch $c_\zeta$.  Near zeros the denominator
approaches zero, so the pitch exhibits spikes whose distribution can be studied across zero gaps.

For a standalone run (matching the internal "paste-ready" script) install the numerical
dependencies and invoke the CLI:

```bash
pip install mpmath matplotlib
python tools/number_theory/zeta_pitch.py --tmin 10 --tmax 200 --n 4000 \
  --csv data/zeta/pitch_10_200.csv --png data/zeta/pitch_10_200.png
```

This will materialise a CSV containing columns `[t, real, imag, logabs, theta_unwrapped, dlog_dt,
dtheta_dt, c_pitch]` and optionally a PNG visualisation of $c_\zeta$ over the sampled interval.

## Relation to the argument principle

Writing $\log \zeta$ in terms of magnitude and phase shows that the pitch is an observable derived
from the same data appearing in the argument principle.  For an integration contour crossing
successive zeros, both $\ln \lvert \zeta \rvert$ and $\arg \zeta$ exhibit sawtooth behaviour.  The
pitch compresses their joint dynamics into a single scalar field that highlights how sharply the
phase winds relative to radial motion.

Investigations suggested in the Riemann brief include:

* comparing the distribution of $c_\zeta(t)$ between consecutive zeros,
* measuring low-order moments of $c_\zeta$ against zero spacing statistics, and
* rescaling samples to probe whether the pitch stabilises to universal limits (GUE heuristics).

The `zeta_pitch` tooling exists to make these experiments painless: evaluate, save, and explore.
