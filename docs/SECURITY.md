# Security Model

## Threat Model

The console is assumed to operate in a restricted corporate environment. We defend
against:

- Credential leakage through source control
- Tampering with audit logs
- Injection attacks via CLI parameters
- Accidental disclosure of PII within task payloads

## Authentication & Authorization

Operators authenticate to the console using OS-level credentials. Roles and access
levels are configured in `config/users.json`. Policy enforcement checks approval
requirements before sensitive tasks are executed.

## Data Protection

- **PII redaction**: `orchestrator.redaction` tokenises PII as
  `{{REDACTED:<type>:<hash8>}}` before writing to disk.
- **Encryption**: Secrets must be provided via environment variables or secret
  management platforms. File-based keys are not stored in the repository.
- **Audit logging**: Every task event is appended to `memory.jsonl` with a detached
  signature and hash chain.

## Secrets Management

- Generate signing keys with `scripts/deploy.py keys --output <path>` (see deployment doc).
- Store credentials in a vault or environment variables.
- Never commit secrets to version control. `.gitignore` excludes sensitive paths.

## Security Checklist

- [ ] All credentials in env vars or vault
- [ ] Input validation on all CLI commands
- [ ] PII redaction tested and verified
- [ ] Audit trail integrity verified
- [ ] Dependencies scanned for vulnerabilities
# Lucidia Auto-Box Security Notes (TTF-01)

These notes capture the initial security posture for the Auto-Box prototype. They will expand into a full threat model during the next codex drop.

## Guiding Controls
- **Encryption**: Require TLS 1.3 for transport. Data at rest is encrypted with per-owner data keys wrapped by a configurable key-encryption key (KEK). Algorithms are configurable to enable PQC-ready swaps.
- **Least privilege**: Services operate with the minimum scopes necessary. No background processing runs without an explicit consent receipt.
- **Auditability**: Every action touching user data must emit an owner-visible audit log entry.
- **Purge semantics**: A single deletion action wipes items, assignments, boxes, and their associated encryption material.

## Immediate Tasks
1. Harden `/classify` to reject unconsented requests and throttle abusive clients.
2. Implement consent receipts before persisting any data.
3. Extend audit logging beyond the in-memory prototype to persistent, user-visible history.
4. Finalize key management with client-held keys where browser capabilities allow.
