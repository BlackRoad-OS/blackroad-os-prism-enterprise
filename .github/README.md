# 🤖 GitHub Automation & Workflows

This directory contains all GitHub Actions workflows, tools, and documentation for the automated PR system.

## 📁 Directory Structure

```
.github/
├── workflows/          # GitHub Actions workflows
│   ├── pr-orchestrator.yml          # Master PR coordinator
│   ├── commit-verification.yml      # Cryptographic verification
│   ├── enforce-commit-signing.yml   # Signature enforcement
│   ├── pr-auto-remediate.yml        # Auto-fix issues
│   ├── pr-branch-sync.yml           # Branch synchronization
│   ├── auto-merge.yml               # Auto-merge approved PRs
│   └── ... (other workflows)
│
├── tools/              # Automation scripts and tools
│   ├── verify-commit-attestation.sh # Commit verification tool
│   ├── autoheal.sh                  # Auto-heal script
│   └── ... (other tools)
│
└── docs/               # Documentation
    ├── PR_AUTOMATION_SYSTEM.md      # Complete system docs
    └── QUICK_START.md               # Quick start guide
```

## 🚀 Quick Links

- **[Complete Documentation](docs/PR_AUTOMATION_SYSTEM.md)** - Full system overview
- **[Quick Start Guide](docs/QUICK_START.md)** - Get started in 5 minutes
- **[Workflows](workflows/)** - All workflow files

## ⚡ Quick Start

### For Developers

1. **Setup commit signing**:
   ```bash
   git config --global gpg.format ssh
   git config --global user.signingkey ~/.ssh/id_ed25519.pub
   git config --global commit.gpgsign true
   ```

2. **Create a PR** - Everything else is automatic!

### For Admins

1. **Setup branch protection**:
   ```bash
   npx tsx scripts/setup-branch-protection.ts
   ```

2. **Consolidate existing PRs**:
   ```bash
   npx tsx scripts/consolidate-prs.ts
   ```

## 🔐 Security Features

- ✅ **Dual Attestation**: Every commit verified by 2 independent tokens
- ✅ **SHA-256/SHA-512**: Cryptographic hashing of all commits
- ✅ **Signature Enforcement**: All commits must be GPG/SSH signed
- ✅ **Branch Protection**: Main branch protected with required checks
- ✅ **Audit Trail**: 365-day retention of attestation artifacts

## 📊 Workflows Overview

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| **PR Orchestrator** | Coordinates all PR automation | PR events |
| **Commit Verification** | Dual-token cryptographic verification | PR/Push |
| **Signature Enforcement** | Blocks unsigned commits | PR/Push |
| **Auto-Remediation** | Fixes common issues automatically | On failure |
| **Branch Sync** | Keeps PRs updated with base | Daily + manual |
| **Auto-Merge** | Merges approved PRs | Label trigger |

## 🛠️ Available Tools

### Commit Attestation Tool
```bash
.github/tools/verify-commit-attestation.sh <commit> <mode>
```
Modes: `verify`, `attest`, `both`

### Branch Protection Setup
```bash
npx tsx scripts/setup-branch-protection.ts
```

### PR Consolidation
```bash
npx tsx scripts/consolidate-prs.ts
```

## 📚 Documentation

- **[Full System Documentation](docs/PR_AUTOMATION_SYSTEM.md)** - Complete guide
- **[Quick Start](docs/QUICK_START.md)** - Get up and running fast

## 🏷️ Labels

The system uses these labels automatically:

- `automerge` - PR ready for automatic merge
- `automated-pr-flow` - Tracked by orchestrator
- `conflicts-detected` - Has merge conflicts
- `unsigned-commits` - Contains unsigned commits
- `ready-for-review` - All checks passing

## 🔄 Workflow Diagram

```
┌─────────────────┐
│   PR Created    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│   PR Orchestrator       │
│  (Master Coordinator)   │
└──┬──────┬──────┬───────┘
   │      │      │
   │      │      └──────────────┐
   │      │                     │
   ▼      ▼                     ▼
┌──────┐ ┌──────────┐    ┌──────────┐
│Verify│ │  Branch  │    │Validate  │
│Crypto│ │   Sync   │    │  Code    │
└──┬───┘ └────┬─────┘    └────┬─────┘
   │          │               │
   │          │               ▼
   │          │         ┌──────────┐
   │          │         │  Failed? │
   │          │         └────┬─────┘
   │          │              │
   │          │              ▼
   │          │         ┌──────────┐
   │          │         │   Auto   │
   │          │         │ Remediate│
   │          │         └────┬─────┘
   │          │              │
   └──────────┴──────────────┘
                │
                ▼
         ┌──────────────┐
         │ All Passing? │
         └──────┬───────┘
                │
                ▼
         ┌──────────────┐
         │  Auto-Merge  │
         └──────────────┘
```

## 🆘 Need Help?

- Create an issue with the `automation` label
- Tag `@blackroad-bot` in PR comments
- Check the [troubleshooting section](docs/PR_AUTOMATION_SYSTEM.md#-troubleshooting)

---

**Powered by GitHub Actions** 🚀
