# Silas Local Router

This repository ships with a local-first client that prefers self-hosted models before
falling back to external APIs. The router lives in `agents/silas_router.py` and supports
three backends in priority order:

1. **vLLM** – `http://localhost:8000/v1`
2. **Ollama** – `http://localhost:11434/v1`
3. **xAI** – `https://api.x.ai/v1` (requires `XAI_API_KEY`)

## Running the Router

```bash
export SAFE_MODE=0
python -c "from agents.silas_router import silas; print(silas('ping', None))"
```

Set `BASE_URL` to override autodetection. When using Ollama, ensure the target model is
available locally or set `SILAS_OLLAMA_MODEL`.

## Tests

```bash
export SAFE_MODE=0
pytest tests/test_silas_router_local.py tests/test_colorize.py tests/test_schema_shape.py
```

The color utilities in `utils/colorize.py` require `rich`. If spaCy is installed the POS
highlighting will use it automatically; otherwise a lightweight heuristic tagger is used.
