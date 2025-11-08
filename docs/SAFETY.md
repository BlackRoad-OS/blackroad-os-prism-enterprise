# Safety Pack Overview

The Safety Pack keeps repository automation in a read-only posture by default.
It pairs a shared environment variable (`SAFE_MODE`) with an optional panic flag
(`.panic`) so potentially destructive scripts and CI jobs can opt into safe
behavior without code duplication.

## SAFE_MODE semantics

- `SAFE_MODE="1"` (default): **Safe mode**. Treat the environment as read-only
  and avoid side effects.
- `SAFE_MODE="0"`: **Write mode**. Explicit opt-in that allows scripts guarded
  with the Safety Pack to execute mutable actions.

Scripts should use `soft_guard` for observational runs (e.g., demos, dry runs)
and `hard_guard` before irreversible operations. The helpers live in
`utils/safety.py`.

### Choosing a guard

- **`soft_guard`** — Logs whether execution is permitted. Use it when the script
  can gracefully continue in read-only mode, perhaps by skipping write paths or
  substituting mock behavior.
- **`hard_guard`** — Aborts execution when the environment does not match the
  allowed value. Use it when proceeding without write access would be unsafe or
  misleading.
- **`panic_guard`** — Immediately exits if a `.panic` file is present. This is a
  manual kill-switch that halts execution regardless of `SAFE_MODE`.

### Example flow

```python
from utils.safety import panic_guard, soft_guard, hard_guard

panic_guard()
if not soft_guard(name="reporting-job"):
    # Skip uploads, but still compute results for logging.
    print("SAFE_MODE enforced; operating in read-only mode.")

hard_guard(name="production-sync")  # Will exit unless SAFE_MODE="0".
```

## CI enforcement

The `.github/workflows/tests.yml` workflow sets `SAFE_MODE="1"` at the job
level and runs a dedicated panic guard step immediately after checkout. If a
`.panic` file is committed (or otherwise present in the workspace), the workflow
fails fast with a clear error, preventing unintended writes or deployments.

## Local development

The `Makefile` exports `SAFE_MODE` (default `1`) so local invocations of
`make test` and `make demo` inherit the safe defaults. Developers can opt into a
write-enabled run by supplying `SAFE_MODE=0`, for example:

```bash
SAFE_MODE=0 make demo
```

This explicit opt-in keeps dangerous operations behind a deliberate flag while
still allowing full functionality when needed.
