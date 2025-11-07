"""Bell/CHSH explorer demo."""
from __future__ import annotations

import json

from ..agents.orchestrator import Orchestrator
from ..tools import quantum_np as Q, viz


def main() -> None:
    orchestrator = Orchestrator()
    orchestrator.run("bell-state-proof", message_budget=64)
    psi = Q.bell_phi_plus()
    counts = Q.measure_counts(psi, shots=4096)
    hist_path = viz.hist(counts, fname="bell_hist.png")
    metrics = {"chsh": Q.chsh_value_phi_plus(), "hist_path": hist_path}
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
