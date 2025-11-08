"""Unit tests for Lucidia Encompass scoring."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.lucidia_encompass import score_packets


def test_score_packets_prefers_positive_signal() -> None:
    packets = [
        {
            "persona": "Origin",
            "balanced_ternary": "+",
            "confidence": 0.9,
            "verdict": "approve",
            "justification": "Stable positive outcome",
        },
        {
            "persona": "Analyst",
            "balanced_ternary": "0",
            "confidence": 0.6,
            "verdict": "defer",
            "justification": "Needs more data",
        },
    ]

    result = score_packets(packets)
    assert result["winner"] == "Origin"
    assert result["consensus_r"] == 0.5


def test_score_packets_handles_negative_votes() -> None:
    packets = [
        {
            "persona": "Origin",
            "balanced_ternary": "-",
            "confidence": 0.4,
            "verdict": "reject",
            "justification": "High risk",
        },
        {
            "persona": "Designer",
            "balanced_ternary": "-",
            "confidence": 0.8,
            "verdict": "reject",
            "justification": "Poor UX impact",
        },
    ]

    result = score_packets(packets)
    assert result["winner"] == "Designer"
    assert result["consensus_r"] == 1.0
