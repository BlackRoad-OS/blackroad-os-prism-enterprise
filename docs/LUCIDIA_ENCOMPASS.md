# Lucidia Encompass Starter Kit

The Lucidia Encompass stack fans out a prompt across several personas, scores
all of the packets, and surfaces a consensus winner.  Everything runs locally so
it is safe to execute in the repository without external services.

## Layout

| Path | Description |
| --- | --- |
| `agents/personas.py` | Persona definitions and helpers. |
| `agents/lucidia_encompass.py` | Aggregator that scores persona packets. |
| `schemas/persona_packet.json` | JSON schema describing persona packets. |
| `scripts/encompass_demo.py` | CLI harness for local experimentation. |
| `tests/test_encompass_vote.py` | Regression tests for scoring and failures. |
| `ui/lucidia_viewer/` | Token colouriser to inspect persona packets. |

## Running the demo

1. Activate the environment variables you use for persona experiments, e.g.

   ```bash
   export SILAS_BASE_URL=http://localhost:8000/v1
   export SAFE_MODE=1
   ```

2. Execute the demo script with a prompt:

   ```bash
   python scripts/encompass_demo.py --prompt "Who are we?" --pretty --output ui/lucidia_viewer/packets.json
   ```

   The script prints the JSON response to stdout and, when `--output` is
   provided, also writes the payload to disk so it can be opened by the viewer.

## Visualising persona packets

The viewer is a lightweight Vite application.  It expects a file named
`packets.json` in the same directory.  Use the demo script (or any other
workflow) to create that file, then run:

```bash
cd ui/lucidia_viewer
npm install
npm run preview
```

Open the URL reported by Vite (default `http://localhost:5173`) to explore the
packets.  Tokens are colour coded by their weight and persona metadata is shown
alongside the text.

## Testing

Run the dedicated unit tests with:

```bash
pytest tests/test_encompass_vote.py
```

The tests cover scoring order, network failure handling, and persona validation
behaviour.
