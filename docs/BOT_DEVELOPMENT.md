# Bot Development Guide

## Prerequisites

- Python 3.11+
- Familiarity with Typer and Pydantic
- Understanding of the policy and memory model described in the architecture docs

## Bot Lifecycle

1. Define metadata using `BotMetadata` and inherit from `BaseBot`.
2. Implement `handle_task()` to process validated tasks.
3. Return a fully populated `BotResponse`.
4. Register the bot in `bots/__init__.py`.
5. Add unit tests under `tests/unit/test_bots/`.

## Minimal Example

```python
from orchestrator.base import BaseBot, BotMetadata
from orchestrator.protocols import BotResponse, Task


class ExampleBot(BaseBot):
    metadata = BotMetadata(
        name="Example-BOT",
        mission="Demonstrate bot structure",
        inputs=["task.goal"],
        outputs=["summary"],
        kpis=["response_time"],
        guardrails=["offline only"],
        handoffs=["demo team"],
    )

    def handle_task(self, task: Task) -> BotResponse:
        return BotResponse(
            task_id=task.id,
            summary=f"Echo: {task.goal}",
            steps=["received", "echoed"],
            data={"goal": task.goal},
            risks=[],
            artifacts=[],
            next_actions=[],
            ok=True,
        )
```

## Best Practices

- Keep business logic deterministic and testable.
- Never perform network I/O inside bots; delegate to adapters.
- Use guardrails to describe safety limits and compliance requirements.
- Document KPIs so operators know how to measure success.

## Testing

- Unit tests should validate success and failure paths.
- Integration tests must exercise routing through the orchestrator.
- Include fixtures in `fixtures/` for representative data sets.
