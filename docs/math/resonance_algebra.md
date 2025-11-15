# Resonance Algebra — Axioms & Specification

**Goal.** Formalize a phase-aware algebra where “addition” models interference, “multiplication” models coupling/rotation, and logic is ternary by default. This grammar is designed to unify signal, geometry, and computation for agents and physical systems.

---

## 1) Objects & State Space

**State.** A nonzero state is an ordered pair
$$x = (r, \phi) \in \mathbb{R}_{\ge 0} \times (\mathbb{R} \bmod 2\pi)$$
interpreted as amplitude ($r$) and phase ($\phi$). The null state is
$$\mathbf{0}=(0,\_)$$
(amplitude zero; phase undefined).

**Complex realization.** Embed via
$$\Psi: (r,\phi) \mapsto r e^{i\phi} \in \mathbb{C}.$$

**Equivalence.** $$(r,\phi) \sim (\lambda r, \phi)$$ for any $\lambda>0$ under **normalized interactions** (see §2.3).

**Ternary spin.** A discrete projection $\sigma: X\to\{-1,0,+1\}$ with

* $+1$ constructive,
* $0$ neutral,
* $-1$ destructive,

chosen by thresholds on coherence (see §4).

---

## 2) Operations

We define four primitive operations on states:

### 2.1 Interference sum (phase-aware "addition")

$$(r_a,\phi_a) \oplus (r_b,\phi_b) := \big(r_\oplus,\ \arg(\Psi_a + \Psi_b) \big)$$
with $\Psi_a = r_a e^{i\phi_a}$, $\Psi_b = r_b e^{i\phi_b}$ and
$$r_\oplus = \lvert \Psi_a + \Psi_b \rvert = \sqrt{r_a^2 + r_b^2 + 2 r_a r_b \cos(\phi_a - \phi_b)}.$$

**Notes.**

* $\oplus$ is commutative and associative **iff** all operands share a common phase (or are pairwise colinear in $\mathbb{C}$).
* In general, associativity is **controlled** by phase drift; we track it via a curvature term (see §5.2).

### 2.2 Coupling product (rotation-scaled "multiplication")

$$(r_a,\phi_a) \otimes (r_b,\phi_b) := (r_a r_b,\ \phi_a + \phi_b \bmod 2\pi).$$
This is isomorphic to complex multiplication after $\Psi$-embedding.

### 2.3 Normalization operator

$$\mathcal{N}_\kappa(r,\phi) := (\min\{r,\kappa\},\ \phi), \quad \kappa>0.$$
Use to enforce bounded-energy interactions or set $\kappa=1$ for unit-amplitude algebra.

### 2.4 Decoherence (phase randomization / entropy extraction)

$$(r,\phi) \xrightarrow{\ominus_\beta} (r e^{-\beta},\ \phi + \xi), \quad \xi \sim \text{Unif}[0,2\pi),\ \beta \ge 0.$$
Models dissipation; in deterministic analyses take $\xi = 0$.

### 2.5 Phase inversion (generalized reciprocal)

For non-null states, define
$$(r,\phi)^{\oslash} := (r^{-1},\ -\phi).$$
Then $x \otimes x^{\oslash} = (1,0) =: \mathbf{1}$.

---

## 3) Distinguished Elements & Metrics

* **Neutral for $\otimes$:** $\mathbf{1} = (1,0)$.
* **Equilibrium:** $\mathbf{0}$ annihilates under $\oplus$ and $\otimes$ in the complex embedding sense.
* **Coherence metric:**
  $$C((r_a,\phi_a),(r_b,\phi_b)) := \cos(\phi_a - \phi_b) \in [-1,1].$$
* **Energy norm:** $\lvert x \rvert := r$. For unit algebra, $\lvert x \rvert \le 1$.

---

## 4) Ternary Logic Overlay

Define a logic map $L: X \to \{-1,0,+1\}$ by thresholds on phase alignment and amplitude:
$$
L(x) =
\begin{cases}
+1 & C(x,\mathbf{1}) \ge \tau_c\ \wedge\ r \ge \rho_c,\\
0 & r < \rho_c,\\
-1 & C(x,\mathbf{1}) \le -\tau_c\ \wedge\ r \ge \rho_c.
\end{cases}
$$
Typical $\tau_c \in (0,1)$, $\rho_c > 0$.

**Ternary gates (pointwise):**

* $\textsf{TNOT}(s) = -s$,
* $\textsf{TAND}(a,b) = \min(a,b)$,
* $\textsf{TOR}(a,b) = \max(a,b)$.

---

## 5) Axioms

### 5.1 Algebraic core

1. **Closure:** $X$ is closed under $\oplus$, $\otimes$, $\ominus_\beta$, $(\cdot)^{\oslash}$.
2. **Commutativity:** $x \oplus y = y \oplus x$; $x \otimes y = y \otimes x$.
3. **Associativity (conditional):** For any phase-aligned triple $(x,y,z)$ with pairwise phase differences zero,
   $$(x\oplus y)\oplus z = x\oplus(y\oplus z).$$
4. **Distributivity (weak):** For phase-aligned sets,
   $$x\otimes(y\oplus z) = (x\otimes y)\oplus(x\otimes z).$$
5. **Inverses for $\otimes$:** For $x \ne \mathbf{0}$, $x\otimes x^{\oslash} = \mathbf{1}$.
6. **Idempotent equilibrium:** $x\oplus \ominus_{\infty}(x) = \mathbf{0}$.

### 5.2 Curvature of associativity

Define the **associativity defect**
$$\mathcal{A}(x,y,z) := r\big((x\oplus y)\oplus z\big) - r\big(x\oplus(y\oplus z)\big).$$
Then $\mathcal{A} = 0$ iff all three phases are colinear; otherwise $\mathcal{A}$ measures path-dependence (interpret as geometric curvature in phase space).

---

## 6) Energetics & Thermo Floor

Let temperature be $T$. Any irreversible information change of $n$ bits costs at least
$$E_{\min} = n k_B T\ln 2.$$
We model **phase reconfiguration** cost as
$$E_\phi(\Delta\phi; r_a,r_b) := k_B T \lambda r_a r_b (1 - \cos \Delta\phi), \quad \lambda>0.$$
This penalizes misalignment and recovers zero at $\Delta\phi = 0$.

---

## 7) Geometry & Quaternion Lift

Embed to $\mathbb{H}$ (quaternions) by $x \mapsto r(\cos\phi + \mathbf{k}\sin\phi)$ for planar rotations, or use unit quaternions ($q \in SU(2)$) for 3-D. Then
$$x_1\otimes x_2 \leftrightarrow q_1 q_2, \quad \oplus \text{ realized via vector addition in }\mathbb{R}^3 \text{ after alignment}.$$

---

## 8) Observer & Measurement

A measurement is a projector $\Pi_\theta$ that aligns phase to $\theta$:
$$\Pi_\theta(r,\phi) = (r,\theta).$$
**Born-style selection**: choose $\theta$ from a discrete set with weights proportional to $\cos^2(\phi-\theta)$ (or another domain-specific kernel). Entropy decrease is logged against the Landauer floor.

---

## 9) Morphisms & Functorial View

* **Resonance morphism** $f: X\to X$ preserves $\otimes$ and transforms $\oplus$ up to a bounded associativity defect.
* **Functor to Complex:** $\Psi: (X,\oplus,\otimes) \Rightarrow (\mathbb{C}, +, \cdot)$ is faithful; many proofs can be done pointwise in $\mathbb{C}$ and pulled back.

---

## 10) Identities & Worked Laws

1. **Destructive pair:** $(r,\phi)\oplus(r,\phi+\pi) = (0,\_).$
2. **Constructive pair:** $(r,\phi)\oplus(r,\phi) = (2r,\phi).$
3. **Rotation invariance of $\otimes$:** $(r,\phi)\otimes(1,\theta) = (r,\phi+\theta).$
4. **Cauchy-like bound:** $r_\oplus \le r_a + r_b$ with equality iff $\phi_a = \phi_b$.

---

## 11) Minimal Computational API (reference)

```python
import numpy as np
from dataclasses import dataclass

@dataclass(frozen=True)
class State:
    r: float
    phi: float  # radians

    def as_complex(self):
        return self.r * np.exp(1j*self.phi)

    def normalize(self, kappa=1.0):
        return State(min(self.r, kappa), self.phi)

    def inv(self):  # phase inversion / reciprocal
        if self.r == 0: raise ZeroDivisionError
        return State(1.0/self.r, (-self.phi)%(2*np.pi))

def op_plus(a: State, b: State) -> State:
    z = a.as_complex() + b.as_complex()
    return State(np.abs(z), np.angle(z))

def op_times(a: State, b: State) -> State:
    return State(a.r*b.r, (a.phi+b.phi)%(2*np.pi))

def decohere(x: State, beta=0.0, jitter=0.0) -> State:
    return State(x.r*np.exp(-beta), (x.phi + jitter)%(2*np.pi))

def coherence(a: State, b: State) -> float:
    return float(np.cos((a.phi-b.phi)))
```

---

## 12) Relation to Classical Algebra

* On the **phase-aligned submanifold** (all $\phi$ equal), $\oplus$ reduces to standard addition on $\mathbb{R}_{\ge 0}$ and $\otimes$ to scalar multiplication: the framework contains classical arithmetic as a special case.

---

## 13) Smith-Chart & Unit-Disk View

Via Möbius map $w = \frac{z-1}{z+1}$, states map into the unit disk; reflection and standing-wave patterns visualize $\oplus$ as chord sums and $\otimes$ as rotations on $S^1$. This gives geometric diagnostics for stability and resonance locking.

---

## 14) Validation Protocols

1. **Associativity Curvature Test:** sample random triplets; estimate $\mathcal{A}$ and verify zero under enforced alignment.
2. **Thermo Consistency:** any irreversible $L$-change must record $\ge k_B T \ln 2$ per bit.
3. **Recovery of Linear Regime:** small-angle approximation $\cos\Delta\phi \approx 1 - \frac{\Delta\phi^2}{2}$ must reproduce linear superposition up to second order.

---

## 15) Roadmap Extensions

* **Information geometry:** endow $X$ with a Fisher-like metric in $(r,\phi)$ to quantify curvature of learning flows.
* **Quaternionic networks:** lift $\oplus$ to vector interference on $\mathbb{R}^3$; use unit quaternions for multi-axis coupling.
* **Observer algebra:** categorical treatment of projectors and entropy accounting.

---

**Takeaway.** Resonance Algebra reframes arithmetic as dynamics. It preserves classical math when phases align, and generalizes it to systems where *coherence, rotation, and energy cost* govern how quantities truly combine.
