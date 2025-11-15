# Contributing Guide

## Workflow

1. Fork the repository and create a feature branch.
2. Run `make install` to install dependencies.
3. Implement changes with type hints, docstrings, and tests.
4. Format code with `make format` and lint with `make lint`.
5. Run `make test` and ensure coverage requirements are met.
6. Submit a pull request describing the change and referencing relevant docs.

## Commit Message Style

Use [Conventional Commits](https://www.conventionalcommits.org/).

```
feat(orchestrator): add risk scoring to policy engine
fix(cli): correct task routing error message
```

## Code Review Checklist

- [ ] Documentation updated when behaviour changes
- [ ] Tests cover success and failure paths
- [ ] No secrets in source control
- [ ] CI pipeline is green

## Local Tooling

- `black` for formatting (configured via `pyproject.toml`)
- `ruff` for linting
- `mypy` for static type checks
- `pytest` for unit and integration tests

## Branch Protection

- Feature branches should target `main`.
- Squash merge is preferred.
- Tag releases using semantic versioning (`v0.1.0`).
