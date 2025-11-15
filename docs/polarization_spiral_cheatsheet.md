# Polarization Spirals Cheat-Sheet

This note condenses the intuition that links glare-cutting sunglasses, polarization helices, and spiral motifs that recur in our Amundson playbook.

## 1. Surface Glare and Linear Polarizers
- Sunlight reflecting off water near Brewster's angle is predominantly **horizontally polarized**.
- Polarized lenses are fabricated with a **vertical transmission axis**, suppressing the reflected component while passing the subsurface light that reveals fish or reef structure.
- Intensity trends while rotating the lens follow Malus's law: \(I(\theta) = I_0 \cos^2 \theta\). A 90° twist swaps bright and dark states because the analyzer aligns or rejects the horizontal field.

## 2. Polarization Helices on the Poincaré Sphere
- Circular and elliptical polarization correspond to electric field vectors that **corkscrew** as the wave propagates.
- On the Poincaré sphere, the Stokes vector executes a **uniform rotation** with angular rate
  \[
  \Omega_{\text{pol}} = \frac{2\pi\, \Delta n}{\lambda}
  \]
  for birefringent media with refractive-index split \(\Delta n\).
- Quarter-wave plates act like multiplying one field component by \(i\), converting linear states into circular ones and vice versa.

## 3. Quantized Phase Winding in Atomic Orbitals
- Hydrogenic eigenstates carry an azimuthal factor \(e^{i m \phi}\) with integer **winding number** \(m\).
- The winding encodes angular momentum projection \(L_z = m\hbar\) and describes **phase structure**, not a classical orbital path.

## 4. Bloch-Sphere Spirals with Dissipation
- A driven two-level system precesses at the Rabi rate \(\Omega\). Dephasing \(\gamma_2\) damps the transverse components.
- The resulting trajectory is a spiral that collapses toward the equilibrium pole with an effective pitch \(c_{\text{Bloch}} \approx -\gamma_2/\Omega\).

## 5. Lab Demos
- **Polarization helix**: Send a laser through a quarter-wave plate and a rotatable linear polarizer. Pure circular states keep intensity constant. Cascading two plates reveals the precession of the Stokes vector.
- **Glare filter**: Observe a shallow water surface while rotating your head. The swing between bright and dark views tracks the rejection of horizontally polarized reflections, exposing underwater detail.

These recurring spiral parameters \((c, \Omega_{\text{pol}}, m, c_{\text{Bloch}})\) translate Amundson's complex-plane spiral constant into optical, quantum, and control contexts.
