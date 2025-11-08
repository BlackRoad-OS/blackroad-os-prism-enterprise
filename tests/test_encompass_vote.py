"""Tests for the Lucidia Encompass voting heuristic."""

from __future__ import annotations

import json
import pathlib
import sys
from pathlib import Path

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from agents.lucidia_encompass import LucidiaEncompass, WeightedConsensusScorer
from agents.personas import Persona, PersonaError, PersonaNetworkError


class StaticPersona(Persona):
    """Persona returning a preconfigured payload for deterministic tests."""

    def __init__(self, name: str, *, response: str, confidence: float) -> None:
        super().__init__(
            name=name,
            voice=f"{name} voice",
            focus=("focus",),
            base_confidence=confidence,
            response_builder=lambda prompt: {
                "response": response,
                "summary": f"{name} summary",
                "confidence": confidence,
            },
        )


class FailingPersona(Persona):
    """Persona raising errors to simulate network/API failures."""

    def __init__(self, name: str, exc: Exception) -> None:
        super().__init__(
            name=name,
            voice=f"{name} voice",
            focus=(),
            response_builder=lambda prompt: _raise(exc),
        )


def _raise(exc: Exception):  # pragma: no cover - helper used indirectly
    raise exc


def test_encompass_orders_packets_by_score():
    personas = [
        StaticPersona("Low", response="Short reply", confidence=0.2),
        StaticPersona(
            "High",
            response="Detailed response with several components including clarity and alignment",
            confidence=0.9,
        ),
    ]
    scorer = WeightedConsensusScorer(coverage_weight=0.25, depth_weight=0.25)
    result = LucidiaEncompass(personas, scorer=scorer).run("Tell me something important")

    packets = result["packets"]
    assert packets[0]["persona"] == "High"
    assert packets[0]["score"] >= packets[1]["score"]
    assert result["winner"] == "High"
    assert 0.0 <= result["consensus"] <= 1.0


def test_encompass_handles_network_error(tmp_path: Path):
    personas = [
        StaticPersona("Stable", response="All good here", confidence=0.6),
        FailingPersona("Offline", PersonaNetworkError("gateway timeout")),
    ]

    result = LucidiaEncompass(personas).run("Status check")
    packets = {packet["persona"]: packet for packet in result["packets"]}

    assert packets["Offline"]["error"] == "gateway timeout"
    assert packets["Offline"]["confidence"] == 0.0
    assert packets["Stable"]["score"] > 0.0

    # Write output to ensure JSON serialisation matches schema expectations.
    output_file = tmp_path / "packets.json"
    output_file.write_text(json.dumps(result), encoding="utf-8")
    loaded = json.loads(output_file.read_text(encoding="utf-8"))
    assert "winner" in loaded and loaded["winner"]


def test_persona_builder_raises_clean_error():
    persona = Persona(
        name="Errant",
        voice="",
        focus=(),
        response_builder=lambda prompt: {"response": "", "summary": ""},
    )
    with pytest.raises(PersonaError):
        persona.generate_packet("anything")
