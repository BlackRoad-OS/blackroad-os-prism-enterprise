# CLI Reference

All commands follow the `module:action[:subaction]` pattern.

## Global Flags

- `--log-level [debug|info|warning|error]`
- `--memory <path>` override memory log location

## Commands

### `bot:list`
Lists available bots and their missions.

```bash
python -m cli.console bot:list
```

### `task:create`
Creates a task and stores it in the registry.

```bash
python -m cli.console task:create --goal "Build Q3 cash forecast" \
    --owner finance.ops --priority high --due-date 2025-07-01
```

### `task:route`
Routes a task to a bot.

```bash
python -m cli.console task:route --id TSK-20250214-001 --bot Treasury-BOT
```

### `task:history`
Shows the audit history for a task.

```bash
python -m cli.console task:history --id TSK-20250214-001
```

### `policy:list`
Displays policy rules and approval requirements.

```bash
python -m cli.console policy:list
```

### `config:validate`
Validates configuration files against the Pydantic models.

```bash
python -m cli.console config:validate
```

See `python -m cli.console --help` for the complete command tree.
