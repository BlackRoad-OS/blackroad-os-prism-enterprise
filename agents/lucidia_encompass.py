"""Lucidia Encompass aggregator.

The aggregator coordinates multiple personas, scores their responses and
surfaces a consensus recommendation.  The implementation intentionally avoids
external dependencies so it can be executed inside the repository without
network connectivity.
"""

from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .personas import (
    Persona,
    PersonaError,
    PersonaNetworkError,
    PersonaPacket,
    load_default_personas,
)

__all__ = ["ConsensusScore", "LucidiaEncompass", "WeightedConsensusScorer"]


@dataclass
class ConsensusScore:
    """Aggregated scoring information for a persona packet."""

    raw: float
    rationale: str

    @property
    def normalised(self) -> float:
        return max(0.0, min(1.0, self.raw))


class WeightedConsensusScorer:
    """Compute per-packet scores using a transparent heuristic."""

    def __init__(self, *, coverage_weight: float = 0.35, depth_weight: float = 0.2) -> None:
        self.coverage_weight = coverage_weight
        self.depth_weight = depth_weight

    def score_packet(self, packet: PersonaPacket, prompt: str) -> ConsensusScore:
        words = [w.lower().strip(".,!?:;()").strip() for w in prompt.split() if w]
        unique_words = {w for w in words if len(w) > 3}
        emphasis_hits = 0
        for token in packet.tokens:
            candidate = str(token.get("text", "")).lower().strip(".,!?:;()").strip()
            if candidate in unique_words:
                emphasis_hits += 1
        coverage = 0.0
        if unique_words:
            coverage = min(1.0, emphasis_hits / max(len(unique_words), 1))

        response_length = len(packet.response.split())
        depth = min(1.0, response_length / 120)  # treat 120 words as "complete"
        base = packet.confidence * (1 - self.coverage_weight - self.depth_weight)
        raw_score = base + coverage * self.coverage_weight + depth * self.depth_weight
        rationale = (
            f"confidence={packet.confidence:.2f}, coverage={coverage:.2f}, depth={depth:.2f}"
        )
        packet.score = round(max(0.0, min(1.0, raw_score)), 4)
        packet.metadata.setdefault("scoring", rationale)
        return ConsensusScore(raw=packet.score, rationale=rationale)

    def score_packets(self, packets: Sequence[PersonaPacket], prompt: str) -> List[ConsensusScore]:
        return [self.score_packet(packet, prompt) for packet in packets]


class LucidiaEncompass:
    """Orchestrate persona execution and compute a consensus."""

    def __init__(
        self,
        personas: Iterable[Persona] | None = None,
        *,
        scorer: WeightedConsensusScorer | None = None,
    ) -> None:
        self.personas: List[Persona] = list(personas or load_default_personas())
        self.scorer = scorer or WeightedConsensusScorer()

    def run(self, prompt: str) -> dict:
        if not prompt:
            raise ValueError("prompt must not be empty")

        packets = self._collect_packets(prompt)
        self.scorer.score_packets(packets, prompt)
        packets.sort(key=lambda p: p.score, reverse=True)

        consensus = self._compute_consensus(packets)
        winner = packets[0].persona if packets else None

        return {
            "prompt": prompt,
            "winner": winner,
            "consensus": round(consensus, 4) if packets else 0.0,
            "packets": [packet.as_dict() for packet in packets],
            "generated_at": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        }

    def _collect_packets(self, prompt: str) -> List[PersonaPacket]:
        packets: List[PersonaPacket] = []
        for persona in self.personas:
            try:
                packets.append(persona.generate_packet(prompt))
            except PersonaNetworkError as exc:
                packets.append(
                    PersonaPacket(
                        persona=persona.name,
                        summary="Persona unavailable",
                        response="",
                        confidence=0.0,
                        tokens=[],
                        score=0.0,
                        metadata={"voice": persona.voice, "focus": list(persona.focus)},
                        error=str(exc),
                    )
                )
            except PersonaError as exc:
                packets.append(
                    PersonaPacket(
                        persona=persona.name,
                        summary="Persona failed",
                        response="",
                        confidence=0.0,
                        tokens=[],
                        score=0.0,
                        metadata={"voice": persona.voice, "focus": list(persona.focus)},
                        error=str(exc),
                    )
                )
        return packets

    def _compute_consensus(self, packets: Sequence[PersonaPacket]) -> float:
        if not packets:
            return 0.0
        total = sum(packet.score for packet in packets)
        mean = total / len(packets)
        spread = math.sqrt(sum((packet.score - mean) ** 2 for packet in packets) / len(packets))
        variance_penalty = min(0.25, spread)
        return max(0.0, mean - variance_penalty)
