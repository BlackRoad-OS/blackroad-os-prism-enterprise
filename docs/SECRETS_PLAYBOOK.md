# Secrets Rotation Playbook

1. **Identify** the secret (source, scope, owner, blast radius).
2. **Revoke/rotate** at the upstream provider (create new credential; timebox to ≤15 min).
3. **Purge**: remove from code/history if needed (e.g., `git filter-repo`), or accept baseline with justification if false positive.
4. **Validate** CI passes (pre-commit, GitHub scan, Gitleaks). Regenerate the baseline with `detect-secrets scan --baseline .secrets.baseline` after closing out findings so existing files stay unblocked.
5. **Document**: add note to `SECURITY.md` or incident log (who/when/where/rotation ticket).
6. **Prevent**: add custom allow/deny patterns if recurring.
