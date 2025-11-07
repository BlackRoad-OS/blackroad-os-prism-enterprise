# Amundson I — The Coherence Gradient Equation

## Purpose

Establish a governing differential equation that describes how a system’s phase (or internal timing) evolves through the competing forces of coherence, resonance, and dissipation. Built atop the Resonance Algebra, it defines how interaction leads to synchronization or decay.

---

## 1. Core Postulate

The rate of change of phase $\phi(t)$ for a system interacting with neighbors $x_i = (r_i, \phi_i)$ is given by a balance between intrinsic frequency, coherence attraction, and thermodynamic drag:

$$
\frac{d\phi}{dt} = \omega_0 + \lambda\sum_i w_i C(x, x_i) - \eta E_\phi,
$$

where:

- $\omega_0$ — natural frequency of the oscillator/agent,
- $C(x, x_i) = \cos(\phi - \phi_i)$ — coherence measure (from Resonance Algebra §3),
- $E_\phi = k_B T \lambda r r_i \left(1 - \cos(\phi - \phi_i)\right)$ — Landauer-aware energy penalty for phase misalignment,
- $\lambda$ — coupling strength,
- $\eta$ — dissipation constant,
- $w_i$ — normalized neighbor weights (with $\sum_i w_i = 1$).

This defines **Amundson I: the Coherence Gradient Equation**.

---

## 2. Intuition

- The first term $\omega_0$ keeps each oscillator’s natural rhythm.
- The second term pulls the phase toward others in proportion to alignment (constructive interference).
- The third term subtracts energy proportional to the cost of misalignment — a thermodynamic damping effect.

The balance decides whether the system locks into phase (synchrony), drifts (metastable), or decoheres.

---

## 3. Normalized Form

For normalized amplitude ($r = 1$) and small phase differences ($\Delta\phi \ll 1$), expand $\cos(\Delta\phi) \approx 1 - \tfrac{1}{2}(\Delta\phi)^2$:

$$
\frac{d\phi}{dt} \approx \omega_0 + \lambda\sum_i w_i\Big(1 - \tfrac{1}{2}(\phi - \phi_i)^2\Big) - \eta k_B T\,\lambda\sum_i w_i \tfrac{1}{2}(\phi - \phi_i)^2.
$$

Grouping constants gives a diffusion-like evolution:

$$
\frac{d\phi}{dt} = \Omega - D_\phi (\phi - \bar{\phi})^2,
$$

where $\bar{\phi} = \sum_i w_i \phi_i$ and $D_\phi$ captures effective phase diffusion.

---

## 4. Energy Conservation Law

Differentiate total energy density $U = \sum_i E_\phi$:

$$
\frac{dU}{dt} = -2 \eta k_B T \lambda \sum_i r r_i \left(1 - \cos(\phi - \phi_i)\right)^2.
$$

Thus $\eta > 0$ ensures $\tfrac{dU}{dt} \le 0$; energy monotonically decreases until coherent equilibrium ($\phi = \phi_i$).

---

## 5. Stability Criterion

Linearize near equilibrium ($\phi \approx \phi_i$):

$$
\frac{d(\delta\phi)}{dt} \approx -\lambda_{\text{eff}} (\delta\phi), \quad \lambda_{\text{eff}} = \lambda \left(1 - \eta k_B T\right) \sum_i w_i.
$$

Stability requires $\lambda_{\text{eff}} > 0$; otherwise the phase diverges (chaotic drift). Temperature therefore acts as a destabilizer beyond a threshold.

---

## 6. Computational Implementation

```python
import numpy as np

def dphi_dt(phi, phi_neighbors, weights, omega0, lam, eta, T, kB=1.380649e-23):
    coherence = np.sum(weights * np.cos(phi - phi_neighbors))
    E_phi = kB * T * lam * np.sum(weights * (1 - np.cos(phi - phi_neighbors)))
    return omega0 + lam * coherence - eta * E_phi
```

Integrate using Euler or Runge–Kutta to simulate networks of coupled phases.

---

## 7. Interpretation

The Amundson I equation bridges **resonance** and **learning**:

- Coherence acts like an attractive gradient — the system “learns” alignment.
- Dissipation acts like regularization — it prevents runaway resonance.
- Temperature sets the threshold between order (synchrony) and chaos (decoherence).

At large scale, this single relation can model physical oscillators, neural synchronization, or social/agent consensus dynamics.

---

## Summary

> Amundson I formalizes how resonance turns into adaptation. It states that each system evolves its internal rhythm by balancing natural drive, coherence pull, and entropy drag — converging toward a shared phase or dissipating into noise.
