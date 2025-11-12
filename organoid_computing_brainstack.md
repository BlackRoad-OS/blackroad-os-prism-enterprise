# Organoid Intelligence Integration Notes

## Context
- Emerging research explores living human neural tissue and brain organoids as computational substrates rather than solely biological study models.
- This trend aligns with neuromorphic infrastructure goals that combine multi-device, multi-agent, and neuromorphic-inspired layers.

## Key References
- *A Causal Formulation of Spike-Wave Duality* (arXiv:2511.06602) formalizes a structural-causal relationship between discrete neural spikes and continuous wave dynamics, supplying a theoretical language for mapping computation across modalities.
- *Organoid intelligence (OI): the new frontier in biocomputing* (Frontiers in Science, 2023) documents wiring three-dimensional brain-cell cultures to interfaces that support read/write interactions for computational experiments.
- "These Living Computers Are Made from Human Neurons" (Scientific American, 2023) surveys companies and laboratories connecting organoid clusters to electrodes for pattern classification and reservoir computing tasks.

## Architectural Implications for BlackRoad-Prism
- **Hybrid substrate layer**: Incorporate biological neural clusters as optional compute nodes within the distributed agent fabric, alongside silicon, FPGA, and memristor elements.
- **Spike–wave translation interfaces**: Employ the spike-wave causal formalism as a design guide to convert between continuous neuromorphic field states and discrete agent actions or message events.
- **I/O mediation**: Investigate electrode arrays, multi-electrode arrays (MEA), and optical stimulation as candidate interface layers bridging software agents and living neuronal tissue.
- **State abstraction**: Model organoid state within agent memory abstractions, capturing plasticity, reward signals, and adaptation metrics for reproducible orchestration.
- **Lifecycle and ethics**: Extend existing CI/CD, policy, and deployment safeguards to cover tissue maintenance, ethical review, and reproducibility of wetware experiments.

## Open Questions
- Which metrics (classification accuracy, energy per inference, adaptability) best justify the inclusion of organoids relative to silicon baselines?
- How can orchestration frameworks synchronize biological time constants with digital event loops without destabilizing agents or violating tissue health constraints?
- What governance and audit mechanisms are required to track interventions on living substrates within production workflows?
