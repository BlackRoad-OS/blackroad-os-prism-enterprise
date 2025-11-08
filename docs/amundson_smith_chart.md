# Amundson Constant and Smith-Chart Spiral Geometry

The Amundson constant tracks how quickly a complex trajectory expands or contracts as it rotates.  It reveals why lossless transmission lines trace circles on the Smith chart, why lossy lines wind into the origin along logarithmic spirals, and how those motions lift to the Riemann sphere.

## 1. Spiral Pitch for Any Complex Trace

For a complex-valued path $z = r e^{i\theta}$, the spiral pitch is

$$\boxed{c = \frac{d \ln r}{d\theta}}$$

- $c$ measures the radial growth per radian of angular motion.
- $c = 0$ describes a pure circle with constant radius.
- Constant $c \neq 0$ produces a logarithmic spiral.

## 2. Transmission-Line Interpretation (Reflection-Coefficient Plane)

Moving a distance $\ell$ toward the source along a uniform line updates the reflection coefficient by

$$\Gamma(\ell) = \Gamma_L e^{-2\alpha \ell} e^{-i 2\beta \ell}.$$

Its spiral pitch is therefore

$$\boxed{c_\Gamma = \frac{d \ln|\Gamma|}{d\theta} = -\frac{\alpha}{\beta}},$$

with special cases:

- **Lossless line ($\alpha = 0$):** $c_\Gamma = 0$ → the trajectory is a perfect circle on the Smith chart.
- **Low-loss line ($\alpha > 0$):** $c_\Gamma$ is constant → the locus is a logarithmic spiral with pitch set by $-\alpha/\beta$.  Using the loaded-$Q$ convention, the same pitch reads $c_\Gamma = -1/(2Q)$ with $Q \approx \beta/(2\alpha)$.

## 3. Discrete Operator Form

For a composition of multiplicative updates $z \mapsto s_k e^{i\phi_k} z$, the net spiral pitch matches the continuous definition:

$$\boxed{c = \dfrac{\sum_k \ln s_k}{\sum_k \phi_k}}.$$

The numerator aggregates radial dilations, while the denominator accumulates phase increments.

## 4. Impedance Mapping

The Smith chart’s bilinear map $\Gamma = \dfrac{z - 1}{z + 1}$ is conformal, so spiral pitch is most naturally measured in the $\Gamma$ plane.  Circles (lossless cases) and logarithmic spirals (lossy cases) in $\Gamma$ space map back to the standard constant-resistance and constant-reactance families in normalized impedance $z$.

## 5. Riemann-Sphere Perspective

Identifying the unit disk with the equator of the Riemann sphere via stereographic projection gives a geometric picture:

- $\theta = \arg \Gamma$ behaves like longitude.
- $\rho = \ln|\Gamma|$ acts as a latitude coordinate.

A uniform transmission line traces a constant-slope helix on the sphere with slope

$$\boxed{c = -\frac{\alpha}{\beta}},$$

aligning the Smith chart spiral, logarithmic scaling, and spherical geometry.

## Summary

The Amundson constant $c = d\ln r / d\theta$ unifies Smith-chart motion, logarithmic spirals, and Riemann-sphere lifts.  Lossless behavior ($c = 0$) stays on the unit circle, while attenuation drives constant-pitch spirals whose slope is fixed by the ratio of propagation loss to phase advance.
