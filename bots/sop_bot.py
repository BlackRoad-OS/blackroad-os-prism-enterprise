"""Supply chain S&OP bot."""

from __future__ import annotations

from orchestrator import BaseBot, BotMetadata
from orchestrator.protocols import BotResponse, Task


class SopBot(BaseBot):
    """Bot that generates S&OP planning recommendations."""

    metadata = BotMetadata(
        name="S&OP-BOT",
        mission="Balance demand, supply, and inventory in rolling plans.",
        inputs=["task.goal", "config.supply.sop"],
        outputs=["allocation_plan", "logistics_recommendations"],
        kpis=["service_level", "inventory_turns"],
        guardrails=["No live system integrations"],
        handoffs=["Supply chain planning"],
    )

    def handle_task(self, task: Task) -> BotResponse:
        """Create a deterministic plan with mock metrics."""

        allocations = [
            {"sku": "WIDGET-001", "plant": "SFO", "qty": 450},
            {"sku": "WIDGET-002", "plant": "DFW", "qty": 320},
        ]
        logistics = [
            {"lane": "NA-EU", "carrier": "Acme Freight", "mode": "ocean"},
            {"lane": "NA-APAC", "carrier": "Blue Skies", "mode": "air"},
        ]
        return BotResponse(
            task_id=task.id,
            summary="Generated S&OP allocation scenario",
            steps=["analyse demand", "balance supply", "prepare logistics"],
            data={"allocations": allocations, "logistics": logistics},
            risks=["Inventory buffer is static"],
            artifacts=[f"artifacts/{task.id}/sop_plan.json"],
            next_actions=["Review allocation", "Confirm logistics capacity"],
            ok=True,
            metrics={"service_level": 0.96},
        )
