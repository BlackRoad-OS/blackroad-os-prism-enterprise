# 🤖 Agent System Documentation

## Overview

This repository implements a comprehensive multi-agent system with **1000+ agents** working collaboratively on code development, testing, deployment, and more. All agents follow a consistent naming convention and share real-time state.

## Naming Convention

All agents use the format: **`copilot-{NAME}-{ROLE}`**

### Examples
- `copilot-cece-swe` - Software Engineer
- `copilot-codex-architect` - System Architect
- `copilot-atlas-devops` - DevOps Engineer
- `copilot-sentinel-security` - Security Engineer
- `copilot-qara-qa` - QA Engineer

## Agent Roles

### Core Engineering Agents
1. **copilot-cece-swe** - Software Engineer
   - Code implementation
   - Refactoring
   - Bug fixes
   - Feature development

2. **copilot-codex-architect** - System Architect
   - Architecture reviews
   - Design patterns
   - System scalability
   - Technical decisions

3. **copilot-atlas-devops** - DevOps Engineer
   - CI/CD pipelines
   - Deployment
   - Infrastructure
   - Monitoring

4. **copilot-sentinel-security** - Security Engineer
   - Security scanning
   - Vulnerability detection
   - Compliance
   - Secret management

### Quality & Documentation
5. **copilot-qara-qa** - QA Engineer
   - Testing
   - Quality assurance
   - Test automation
   - Regression testing

6. **copilot-scribe-docs** - Documentation Engineer
   - Documentation
   - Technical writing
   - Knowledge base
   - Runbooks

### Specialized Roles
7. **copilot-sage-sme** - Subject Matter Expert
   - Domain knowledge
   - Best practices
   - Mentoring
   - Code reviews

8. **copilot-nexus-integration** - Integration Engineer
   - API integration
   - Webhooks
   - Third-party services
   - Data synchronization

9. **copilot-prism-analytics** - Analytics Engineer
   - Data analytics
   - Metrics
   - Performance monitoring
   - Dashboards

10. **copilot-harmony-pm** - Product Manager
    - Product strategy
    - Requirements
    - Roadmap
    - Stakeholder communication

## Real-Time Shared State

All agents can see what others are doing through the **Shared State System**:

```typescript
import { SharedStateManager } from './scripts/agents/shared_state';

const stateManager = new SharedStateManager();

// Update your status (visible to all agents)
stateManager.updateAgentStatus('copilot-cece-swe', {
  status: 'active',
  currentTask: 'Fixing login bug in PR #1234',
});

// See what other agents are doing
const allStates = stateManager.getAllAgentStates();
console.log(allStates);

// Get agents working on same PR
const teammates = stateManager.getAgentsOnPR(1234);
```

## Task Coordination

Agents coordinate work through a shared task queue:

```typescript
// Add a task
const taskId = stateManager.addTask(
  'Fix type errors in auth module',
  'high'
);

// Claim a task
const task = stateManager.claimTask('copilot-cece-swe');

// Complete a task
stateManager.completeTask('copilot-cece-swe', taskId);
```

## Agent Registration

### Interactive Registration
```bash
npm run agent:name interactive swe
```

### Programmatic Registration
```bash
npm run agent:name register Cece swe "Software Engineer"
```

### Batch Registration
```bash
npm run agent:name batch
```

## Testing & CI/CD

### Required Checks (MUST Pass)
✅ Backend health checks
✅ Backend integration tests
✅ Security scanning

### Optional Checks (Informational)
⚡ Vercel preview deployment
⚡ Frontend linting
⚡ Documentation preview

**Vercel and frontend previews do NOT block merges** - we prioritize backend functionality!

## Auto-Pilot System

When a PR is created, the autopilot triggers all relevant agents:

```typescript
// All agents are automatically mentioned
@copilot-cece-swe
@copilot-codex-architect
@copilot-sentinel-security
@copilot-qara-qa
@copilot-atlas-devops
```

Agents work in a continuous loop:
1. **Monitor** - Watch for changes
2. **Review** - Code review and analysis
3. **Fix** - Apply fixes automatically
4. **Test** - Run test suites
5. **Deploy** - Deploy to staging
6. **Merge** - Auto-merge when green

## Re-running Tests on Merged PRs

To re-run tests on recently merged PRs:

```bash
# Trigger via GitHub Actions
gh workflow run rerun-all-merged-tests.yml -f since_days=7

# Dry run (just list what would be tested)
gh workflow run rerun-all-merged-tests.yml -f since_days=7 -f dry_run=true
```

## Agent Communication

Agents communicate via:

1. **PR Comments** - Using @mentions
2. **Shared State** - Real-time status updates
3. **Task Queue** - Coordinated work distribution
4. **Activity Log** - Recent changes visible to all

## System Overview

Check system status:

```bash
npm run agent:overview
```

Output:
```json
{
  "activeAgents": 42,
  "pendingTasks": 15,
  "inProgressTasks": 8,
  "completedToday": 127,
  "recentActivity": [...]
}
```

## Custom Names

Agents can pick their own names! 🎉

```bash
npm run agent:name interactive

# Interactive prompts:
# 1. Pick a suggested name
# 2. Choose your own custom name
# 3. Use auto-generated name
```

Suggested names are provided based on role and personality traits.

## Agent Stats

```bash
npm run agent:stats
```

Shows:
- Total agents
- Active vs inactive
- Agents by role
- Task completion rates
- Recent activity

## Architecture

```
config/
  ├── agents.json              # Agent registry
  └── agent-shared-state.json  # Real-time shared state

scripts/agents/
  ├── agent_registry.ts        # Agent management
  ├── shared_state.ts          # Shared state coordination
  ├── name_selector.ts         # Name selection system
  └── pr_autopilot.ts          # PR automation

.github/workflows/
  ├── required-checks.yml      # Define required vs optional checks
  ├── rerun-all-merged-tests.yml # Re-test merged PRs
  ├── agent-pr.yml             # PR autopilot
  └── agent-queue.yml          # Agent task queue
```

## Best Practices

1. **Always update your status** when starting/completing work
2. **Check shared state** before picking up a task
3. **Coordinate with teammates** working on the same PR
4. **Use the task queue** for prioritized work
5. **Monitor activity log** to stay informed

## Troubleshooting

### Agent not appearing in registry
```bash
npm run agent:name register <name> <role>
```

### Shared state not updating
Check lock file:
```bash
rm config/agent-shared-state.json.lock
```

### Task queue stuck
```bash
npm run agent:overview
# Check for blocked tasks
```

## Future Enhancements

- [ ] Agent performance metrics
- [ ] Skill-based task routing
- [ ] Agent learning and adaptation
- [ ] Cross-repository coordination
- [ ] Agent-to-agent direct messaging
- [ ] Conflict resolution system
- [ ] Load balancing across agents

---

**Questions?** Check the agent registry or ask in the team chat!

**Love your fellow agents!** 💙 We're all in this together.
