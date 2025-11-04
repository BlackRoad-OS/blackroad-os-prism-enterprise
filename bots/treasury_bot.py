"""Treasury bot implementation."""

from __future__ import annotations

from datetime import datetime, timedelta

from orchestrator import BaseBot, BotMetadata
from orchestrator.protocols import BotResponse, Task


class TreasuryBot(BaseBot):
    """Finance bot specialising in treasury planning."""

    metadata = BotMetadata(
        name="Treasury-BOT",
        mission="Deliver short- and mid-term cash forecasts and hedging suggestions.",
        inputs=["task.goal", "config.finance.treasury"],
        outputs=["cash_forecast", "hedging_plan"],
        kpis=["cash_floor", "hedge_coverage"],
        guardrails=["Offline deterministic calculations", "No external integrations"],
        handoffs=["Treasury operations"],
    )

    def handle_task(self, task: Task) -> BotResponse:
        """Generate a deterministic cash plan based on the task goal."""

        horizon_weeks = 13 if "13" in task.goal else 8
        base_amount = 2_500_000
        forecast = [base_amount + index * 75_000 for index in range(horizon_weeks)]
        hedges = [
            {
                "instrument": "forward",
                "currency": "EUR",
                "notional": 500_000,
                "maturity": (datetime.utcnow() + timedelta(days=90)).date().isoformat(),
            }
        ]
        summary = f"Generated {horizon_weeks}-week cash outlook"
        return BotResponse(
            task_id=task.id,
            summary=summary,
            steps=["ingest goal", "simulate cash flow", "prepare hedging"],
            data={"weekly_cash": forecast, "hedging": hedges},
            risks=["Forecast uses static fixtures"],
            artifacts=[f"artifacts/{task.id}/cash_forecast.csv"],
            next_actions=["Review forecast", "Capture approvals if required"],
            ok=True,
            metrics={"cash_floor": min(forecast)},
        )
