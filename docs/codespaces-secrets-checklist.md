# Codespaces Secrets Checklist

This checklist helps BlackRoad maintainers wire GitHub Codespaces secrets into local automation so builds, tests, and agents can run without exposing credentials.

## 1. Identify required secrets

- List every token the repository needs during development (for example `OPENAI_API_KEY`, `GH_TOKEN`, third-party API keys, and internal service tokens).
- Split the list into:
  - **Personal secrets** (unique per developer) that should live at the user level.
  - **Shared secrets** that support team-wide workflows (CI helpers, agent service accounts, etc.).

## 2. Configure Codespaces secrets

1. **User-level secrets** (personal tokens that work across repositories)
   - GitHub ➝ **Settings** ➝ **Codespaces** ➝ **Secrets** ➝ **New secret**.
   - Add the secret name and value, then select the repositories allowed to consume it.
2. **Repository/Organization-level secrets** (shared tokens or those required during prebuilds)
   - Navigate to the repository (or organization) ➝ **Settings** ➝ **Secrets and variables** ➝ **Codespaces** ➝ **New secret**.
   - Grant access to each repository or environment that needs the secret.
3. **Document ownership**
   - Track the owner and rotation policy for each secret in the internal secrets inventory or runbook.

## 3. Wire secrets into the devcontainer

- Confirm every required secret is listed in `.devcontainer/devcontainer.json` under `customizations.codespaces.secrets.required` so Codespaces prompts contributors to add them on create.
- Avoid storing secrets in `.env` files or committing them to source control.
- For secrets injected during `postCreateCommand`, guard the script with `if [[ -n "$SECRET_NAME" ]]; then … fi` checks so the build keeps running if a developer has not yet added their keys.

## 4. Validate the developer experience

- Rebuild a Codespace and verify that required secrets are prompted during creation.
- Inside the running Codespace, run `echo "$SECRET_NAME" | head -c 8` to confirm the variable is populated.
- Ensure tooling that depends on secrets (tests, agents, CLI helpers) reads from environment variables.
- Add smoke tests (for example `npm test -- --grep="requires OPENAI_API_KEY"`) to fail fast when required secrets are missing in CI-style runs.

## 5. Maintain operational hygiene

- Rotate secrets regularly and update their Codespaces entries immediately after rotation.
- Remove repository access for secrets no longer needed by a project.
- Audit prebuild logs to confirm no secret values are printed.
- Consider external secret managers (e.g., Vault, AWS Secrets Manager) if additional controls or auditing is required.

## 6. Pull request gating

- Update contributor docs to reference this checklist so new team members follow the same process.
- During PR reviews, verify that any new automation includes guidance for the necessary secrets.
- Use the following `gh` CLI helpers for one-off audits or rotations:
  - `gh codespace secrets list --repo <org/repo>` to confirm the required repository-level secrets exist.
  - `gh secret list --env codespaces --org <org>` to review organization-level entries.

## 7. Track ownership with an inventory

Maintain a simple inventory (for example in Notion or a `secrets-inventory.md`) that answers:

| Secret name      | Scope (user / repo / org) | Owner          | Rotation frequency | Last rotated |
| ---------------- | ------------------------- | -------------- | ------------------ | ------------ |
| `OPENAI_API_KEY` | User                       | Developer name | Quarterly          | 2024-04-03   |
| `GH_TOKEN`       | Repository                 | Platform team  | Monthly            | 2024-05-11   |

Make it part of quarterly reviews to confirm each entry is current and that expiring credentials have a rotation plan.

By following this checklist, developers can safely provision tokens while keeping Codespaces builds, local tests, and automation agents running smoothly.
