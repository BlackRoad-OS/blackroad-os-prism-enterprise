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
