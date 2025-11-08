# Amundson–ζ Pitch Field

The Amundson spiral pitch captures how quickly a complex trajectory grows radially
compared to its angular sweep.  For an analytic function $f$ sampled along a path
$\gamma(t)$ we write
\[
  c_f(t) = \frac{\frac{\mathrm d}{\mathrm dt} \ln \lvert f(\gamma(t))\rvert}{\frac{\mathrm d}{\mathrm dt} \arg f(\gamma(t))},
\]
whenever the denominator is non-zero.  On the Riemann critical line the path is
$s(t) = \tfrac12 + it$ and we can express derivatives through the logarithmic
slope of $\zeta$:
\[
  \frac{\mathrm d}{\mathrm dt} \log \zeta(s(t)) = \frac{\mathrm d}{\mathrm dt}\big(\ln \lvert \zeta(s(t))\rvert + i\,\arg \zeta(s(t))\big)
  = i\,\frac{\zeta'(s(t))}{\zeta(s(t))}.
\]
The real part controls radial growth, the imaginary part controls angular motion,
and their ratio is the pitch $c_\zeta(t)$.

## Sampling workflow

The module `tools.number_theory.zeta_pitch` contains helpers to evaluate the
pitch numerically with only `mpmath` as a dependency.  Typical usage:

```python
from tools.number_theory import zeta_pitch

# Sample a uniform grid on the critical line.
samples = zeta_pitch.sample_interval(14.0, 40.0, num_points=512)

# Persist the raw data for further analysis.
zeta_pitch.write_csv(samples, "riemann_pitch.csv")

# Optionally visualise the pitch next to |ζ| (requires matplotlib).
zeta_pitch.plot_pitch(samples, path="riemann_pitch.png")
```

Each sample records $t$, $\zeta(\tfrac12 + it)$, the logarithmic derivative, and
the resulting pitch.  Near zeros the denominator approaches zero, so the pitch
exhibits spikes whose distribution can be studied across zero gaps.

## Relation to the argument principle

Writing $\log \zeta$ in terms of magnitude and phase shows that the pitch is an
observable derived from the same data appearing in the argument principle.  For
an integration contour crossing successive zeros, both $\ln \lvert \zeta \rvert$
and $\arg \zeta$ exhibit sawtooth behaviour.  The pitch compresses their joint
dynamics into a single scalar field that highlights how sharply the phase winds
relative to radial motion.

Investigations suggested in the Riemann brief include:

* comparing the distribution of $c_\zeta(t)$ between consecutive zeros,
* measuring low-order moments of $c_\zeta$ against zero spacing statistics, and
* rescaling samples to probe whether the pitch stabilises to universal limits
  (GUE heuristics).

The `zeta_pitch` module exists to make these experiments painless: evaluate,
save, and explore.
