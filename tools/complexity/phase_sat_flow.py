"""Harnesses for experimenting with Amundson coherence flows on combinatorial instances."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

import math
import random

import numpy as np


@dataclass
class FlowParameters:
    """Parameters governing the Amundson I flow."""

    omega0: float = 0.0
    lam: float = 1.0
    eta: float = 0.1
    temperature: float = 1.0
    kB: float = 1.0


@dataclass
class FlowResult:
    """Summary of a numerical flow experiment."""

    history: np.ndarray
    converged: bool
    steps: int
    final_time: float

    @property
    def final_state(self) -> np.ndarray:
        return self.history[-1]


def _normalize_weights(weight_matrix: np.ndarray) -> np.ndarray:
    """Normalize rows of ``weight_matrix`` to sum to one where possible."""

    row_sums = weight_matrix.sum(axis=1, keepdims=True)
    normalized = weight_matrix.copy()
    mask = row_sums > 0
    normalized[mask] /= row_sums[mask]
    return normalized


def _coherence_gradient(phi: np.ndarray, weights: np.ndarray, params: FlowParameters) -> np.ndarray:
    """Vectorized Amundson I gradient for a network."""

    diff = phi[:, None] - phi[None, :]
    cos_diff = np.cos(diff)
    coherence = np.sum(weights * cos_diff, axis=1)
    energy = params.kB * params.temperature * params.lam * np.sum(weights * (1 - cos_diff), axis=1)
    return params.omega0 + params.lam * coherence - params.eta * energy


def simulate_flow(
    initial_phases: Sequence[float],
    weight_matrix: np.ndarray,
    params: FlowParameters,
    *,
    dt: float = 0.01,
    max_steps: int = 10_000,
    tolerance: float = 1e-6,
    sample_every: int = 10,
) -> FlowResult:
    """Integrate the Amundson flow using explicit Euler updates."""

    phi = np.asarray(initial_phases, dtype=float)
    weights = _normalize_weights(weight_matrix)
    history: List[np.ndarray] = [phi.copy()]
    time = 0.0

    for step in range(1, max_steps + 1):
        grad = _coherence_gradient(phi, weights, params)
        phi = phi + dt * grad
        time += dt
        if step % sample_every == 0:
            history.append(phi.copy())
        if np.linalg.norm(dt * grad, ord=np.inf) < tolerance:
            history.append(phi.copy())
            return FlowResult(history=np.stack(history, axis=0), converged=True, steps=step, final_time=time)

    history.append(phi.copy())
    return FlowResult(history=np.stack(history, axis=0), converged=False, steps=max_steps, final_time=time)


def maxcut_weight_matrix(num_vertices: int, edges: Iterable[Tuple[int, int, float]]) -> np.ndarray:
    """Construct a symmetric weight matrix from weighted edges."""

    matrix = np.zeros((num_vertices, num_vertices), dtype=float)
    for u, v, weight in edges:
        matrix[u, v] += weight
        matrix[v, u] += weight
    np.fill_diagonal(matrix, 0.0)
    return matrix


def random_maxcut_instance(num_vertices: int, edge_probability: float, *, seed: int | None = None) -> np.ndarray:
    """Generate a random Erdos–Renyi graph with unit weights."""

    rng = random.Random(seed)
    edges = []
    for u in range(num_vertices):
        for v in range(u + 1, num_vertices):
            if rng.random() <= edge_probability:
                edges.append((u, v, 1.0))
    return maxcut_weight_matrix(num_vertices, edges)


Literal = Tuple[int, bool]
Clause = Tuple[Literal, ...]


def random_2sat_instance(num_vars: int, num_clauses: int, *, seed: int | None = None) -> List[Clause]:
    """Create a random 2-SAT instance for experimentation."""

    rng = random.Random(seed)
    clauses: List[Clause] = []
    for _ in range(num_clauses):
        a = rng.randrange(num_vars)
        b = rng.randrange(num_vars)
        clauses.append(((a, rng.choice([True, False])), (b, rng.choice([True, False]))))
    return clauses


def build_clause_weight_matrix(num_vars: int, clauses: Sequence[Clause]) -> np.ndarray:
    """Construct a weight matrix using one auxiliary node per clause."""

    total_nodes = num_vars + len(clauses)
    matrix = np.zeros((total_nodes, total_nodes), dtype=float)
    clause_offset = num_vars
    for clause_idx, clause in enumerate(clauses):
        aux = clause_offset + clause_idx
        for var_index, desired in clause:
            phase_target = 0.0 if desired else math.pi
            weight = math.cos(phase_target)
            matrix[var_index, aux] += weight
            matrix[aux, var_index] += weight
    np.fill_diagonal(matrix, 0.0)
    return matrix


def random_phases(num_nodes: int, *, seed: int | None = None) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.uniform(-math.pi, math.pi, size=num_nodes)


__all__ = [
    "FlowParameters",
    "FlowResult",
    "simulate_flow",
    "maxcut_weight_matrix",
    "random_maxcut_instance",
    "random_2sat_instance",
    "build_clause_weight_matrix",
    "random_phases",
]
