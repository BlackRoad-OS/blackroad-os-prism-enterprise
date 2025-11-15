# Testing Validation Matrix

## Purpose
This document defines validation rules, input/output expectations, and failure modes for all major components in the BlackRoad Prism Console.

---

## 1. Authentication & Authorization

### JWT Token Generation

| Input | Expected Output | Failure Condition | Validation Rule |
|-------|----------------|-------------------|-----------------|
| Valid user credentials | JWT access + refresh tokens | Invalid credentials | Must return 401 |
| Email + password | Tokens with exp, iat claims | Missing required fields | Must return 400 |
| Valid refresh token | New access token | Expired refresh token | Must return 401 |
| Tampered token | - | Signature verification fails | Must return 401 |
| Expired token | - | Token past expiration | Must return 401 |

**Pre-conditions:**
- User must exist in database
- Password must be hashed with bcrypt
- Secret key must be configured

**Post-conditions:**
- Access token valid for 30 minutes
- Refresh token valid for 7 days
- Tokens include user_id, roles, permissions

### SAML SSO

| Input | Expected Output | Failure Condition | Validation Rule |
|-------|----------------|-------------------|-----------------|
| Valid SAML assertion | User session created | Invalid signature | Must reject |
| IdP metadata | Service provider metadata | Missing required attributes | Must return error |
| SAML request | SAML response with assertion | Assertion expired | Must reject |
| ACS endpoint request | User authenticated | Unknown issuer | Must reject |

**Pre-conditions:**
- SAML IdP configured
- Certificate trust established
- Metadata exchanged

**Post-conditions:**
- User session created
- Attributes mapped to user profile
- Audit log entry created

---

## 2. API Endpoints

### Health Check Endpoints

| Endpoint | Expected Response | Status Code | Validation |
|----------|------------------|-------------|------------|
| GET /health | `{"status": "ok", "timestamp": "..."}` | 200 | Always returns 200 if service up |
| GET /healthz | `OK` or `{"status": "ok"}` | 200 | Kubernetes liveness |
| GET /ready | `{"status": "ready"}` | 200/503 | Checks dependencies |
| GET /metrics | Prometheus metrics text | 200 | Text/plain format |

**Validation Rules:**
- Health endpoints must respond < 100ms
- Readiness checks database, Redis, MQTT
- Returns 503 if any dependency unavailable

### Agent Management Endpoints

| Endpoint | Input | Expected Output | Failure Modes |
|----------|-------|----------------|---------------|
| POST /v1/agents/spawn | `{agent_type, config}` | `{agent_id, status}` | Invalid type → 400 |
| GET /v1/agents/:id/status | agent_id | `{status, metrics}` | Not found → 404 |
| POST /v1/agents/:id/tasks | `{task_type, payload}` | `{task_id}` | Agent busy → 429 |
| POST /v1/agents/:id/shutdown | agent_id | `{success: true}` | Already stopped → 409 |

**Pre-conditions:**
- Agent type must be registered
- User must have `spawn:agents` permission
- System resources available

**Post-conditions:**
- Agent registered in database
- Agent appears in health monitoring
- Agent ID unique and valid format

### User Management Endpoints

| Endpoint | Input | Expected Output | Failure Modes |
|----------|-------|----------------|---------------|
| POST /api/users | `{email, username, password}` | `{id, email}` | Duplicate email → 409 |
| GET /api/users/:id | user_id | User object | Not found → 404 |
| PATCH /api/users/:id | `{field: value}` | Updated user | Unauthorized → 403 |
| DELETE /api/users/:id | user_id | `{success: true}` | Has dependencies → 409 |

**Validation Rules:**
- Email must be valid format
- Password must be 8+ characters
- Username 3-50 alphanumeric
- Roles must exist in system

---

## 3. Database Operations

### User CRUD

| Operation | Input | Expected Result | Failure Mode | Validation |
|-----------|-------|----------------|--------------|------------|
| CREATE | User object | New user in DB | Duplicate email | UNIQUE constraint |
| READ | user_id | User record | Not found | Returns NULL |
| UPDATE | user_id + fields | Updated record | Invalid field | Schema validation |
| DELETE | user_id | Record removed | Foreign key constraint | Cascade or block |

**Constraints:**
- email: UNIQUE, NOT NULL, VARCHAR(255)
- password_hash: NOT NULL, VARCHAR(255)
- created_at: NOT NULL, TIMESTAMP
- id: PRIMARY KEY, AUTO_INCREMENT

### Project CRUD

| Operation | Input | Expected Result | Failure Mode | Validation |
|-----------|-------|----------------|--------------|------------|
| CREATE | Project object | New project | Missing owner_id | FK constraint |
| READ | project_id | Project record | Not found | Returns NULL |
| UPDATE | project_id + fields | Updated project | - | - |
| DELETE | project_id | Cascade delete tasks | Has active tasks | Configurable cascade |

**Constraints:**
- owner_id: FOREIGN KEY → users(id)
- name: NOT NULL, VARCHAR(255)
- status: ENUM('active', 'archived')

### Agent Registry CRUD

| Operation | Input | Expected Result | Failure Mode | Validation |
|-----------|-------|----------------|--------------|------------|
| CREATE | Agent manifest | Registered agent | Duplicate agent_id | UNIQUE constraint |
| READ | agent_id | Agent record | Not found | Returns NULL |
| UPDATE | agent_id + status | Updated status | Invalid status | ENUM validation |
| DELETE | agent_id | Deregistered | Still active | Status check required |

**Constraints:**
- agent_id: UNIQUE, NOT NULL, VARCHAR(50)
- status: ENUM('active', 'idle', 'busy', 'error', 'shutdown')
- capabilities: JSON or TEXT
- last_heartbeat: TIMESTAMP

---

## 4. Agent Orchestration

### Agent Lifecycle

| Phase | Input | Expected Behavior | Failure Recovery |
|-------|-------|------------------|------------------|
| Spawn | Agent config | Agent initialized, status=active | Retry 3x, then fail |
| Register | Agent manifest | Added to registry | Rollback if fails |
| Execute Task | Task object | Task completed, results returned | Mark failed, retry |
| Health Check | - | Heartbeat response | Mark unhealthy after 3 missed |
| Shutdown | Shutdown signal | Graceful cleanup, status=shutdown | Force kill after 30s |

**Pre-conditions:**
- Agent type registered
- Resources available (CPU, memory)
- Dependencies (DB, message bus) healthy

**Post-conditions:**
- Agent in registry with valid ID
- Metrics initialized
- Event listeners registered

### Task Distribution

| Scenario | Input | Expected Routing | Fallback |
|----------|-------|------------------|----------|
| Exact capability match | Task requiring "quantum" | Route to quantum agent | Queue if none idle |
| Multi-capability | Task requiring ["security", "audit"] | Route to agent with both | Fail if none available |
| Load balancing | 10 identical tasks | Distribute evenly across pool | Round-robin |
| Priority routing | High-priority task | Route to dedicated agent pool | Pre-empt low-priority |

**Validation Rules:**
- Task must specify required capabilities
- Agent must be in 'idle' or 'active' status
- Agent must have capacity (queue size < max)

### Multi-Agent Coordination

| Formation | Agents Required | Coordination Pattern | Failure Mode |
|-----------|----------------|----------------------|--------------|
| DELTA | 1 leader + N workers | Hierarchical, leader delegates | Leader fails → elect new |
| HALO | N nodes (ring) | Each communicates with neighbors | Node fails → reform ring |
| LATTICE | N² nodes (grid) | Grid-based messaging | Node fails → route around |
| CAMPFIRE | N nodes (circle) | Broadcast to all | Node fails → continue |

**Pre-conditions:**
- Minimum number of agents available
- Agents have formation capability
- Message bus operational

**Post-conditions:**
- Formation ID created
- Agents aware of neighbors
- Coordination state synchronized

---

## 5. Event Processing

### MQTT Message Handling

| Event Type | Payload | Expected Processing | Failure Handling |
|------------|---------|---------------------|------------------|
| agent.spawned | `{agent_id, type}` | Add to registry, log event | Retry 3x, dead letter queue |
| task.assigned | `{task_id, agent_id}` | Update agent status, start task | Rollback status |
| task.completed | `{task_id, result}` | Store result, notify subscribers | Log error, retry |
| agent.heartbeat | `{agent_id, metrics}` | Update last_heartbeat | Mark stale after 60s |
| system.shutdown | `{reason}` | Graceful shutdown all agents | Force after timeout |

**Validation Rules:**
- Payload must match schema
- agent_id must exist in registry
- Event timestamp within 5 minutes

### Event Mesh Routing

| Source | Topic | Subscribers | Routing Rule |
|--------|-------|------------|--------------|
| Agent | `agents/{agent_id}/events` | Orchestrator, Monitor | Route by agent_id |
| Task System | `tasks/{task_id}/updates` | Assigned agent, Dashboard | Route by task_id |
| Health Monitor | `health/alerts` | All managers | Broadcast |
| Quantum Service | `quantum/jobs/{job_id}` | Requesting agent | Route by job_id |

**Pre-conditions:**
- Subscribers registered for topics
- Message bus operational
- Event schema validated

**Post-conditions:**
- Event delivered to all subscribers
- Event persisted in event store
- Metrics updated

---

## 6. Quantum Computing Operations

### Circuit Execution

| Input | Expected Output | Failure Mode | Validation |
|-------|----------------|--------------|------------|
| Bell state circuit | Counts: {00: ~500, 11: ~500} | Invalid gate | Validate circuit structure |
| Grover search (4 qubits) | Target state > 90% probability | Too many qubits | Limit to simulator capacity |
| QFT circuit | Transformed statevector | Phase errors | Verify unitarity |
| VQE optimization | Converged energy value | No convergence | Max iterations limit |

**Pre-conditions:**
- Circuit compiled successfully
- Simulator initialized
- Qubit count within limits

**Post-conditions:**
- Results match expected distribution
- Circuit diagram generated
- Execution time logged

### Qiskit Integration

| Operation | Input | Expected Output | Failure Recovery |
|-----------|-------|----------------|------------------|
| Submit to IBM Quantum | Circuit + backend | Job ID | Fallback to simulator |
| Job status check | Job ID | Status + results | Retry if timeout |
| Backend selection | Backend name | Backend object | Use default if unavailable |

---

## 7. Security Validation

### Input Sanitization

| Input Type | Validation Rule | Example Valid | Example Invalid |
|------------|----------------|---------------|-----------------|
| Email | RFC 5322 format | `user@blackroad.io` | `invalid.email` |
| User ID | UUID v4 | `123e4567-e89b-12d3-a456-426614174000` | `123-456` |
| Agent ID | Format: `[A-Z]+-[A-Z0-9]+-[A-Z]+-[A-Z0-9]+` | `CECILIA-7C3E-SPECTRUM-9B4F` | `invalid-id` |
| Task Payload | JSON, max 1MB | `{"key": "value"}` | `<script>...</script>` |

**XSS Prevention:**
- All user input HTML-escaped
- Content-Security-Policy headers
- No eval() or innerHTML

**SQL Injection Prevention:**
- Parameterized queries only
- ORM usage enforced
- Input validation on all fields

### Rate Limiting

| Endpoint | Rate Limit | Time Window | Action on Exceed |
|----------|-----------|-------------|------------------|
| /auth/login | 5 requests | 15 minutes | 429 + lockout |
| /api/* (authenticated) | 1000 requests | 1 hour | 429 |
| /v1/agents/spawn | 10 requests | 1 minute | 429 |
| /health | Unlimited | - | - |

**Pre-conditions:**
- Redis available for rate limit tracking
- Client IP or user ID identified

**Post-conditions:**
- Rate limit headers in response
- Metrics tracked
- Abuse logged

---

## 8. Performance Benchmarks

| Component | Metric | Target | Failure Threshold |
|-----------|--------|--------|-------------------|
| Health endpoint | Response time | < 50ms | > 100ms |
| Database query (single) | Response time | < 10ms | > 50ms |
| Agent spawn | Time to active | < 2s | > 5s |
| Task completion (simple) | Execution time | < 1s | > 5s |
| API throughput | Requests/sec | > 1000 | < 100 |
| Event processing | Messages/sec | > 5000 | < 500 |

---

## 9. Error Handling Matrix

| Error Type | HTTP Status | Response Format | User Action |
|------------|-------------|----------------|-------------|
| Validation error | 400 | `{error, details: [...]}` | Fix input |
| Unauthorized | 401 | `{error, message}` | Authenticate |
| Forbidden | 403 | `{error, required_permission}` | Request access |
| Not found | 404 | `{error, resource_type, id}` | Check ID |
| Conflict | 409 | `{error, conflicting_field}` | Use different value |
| Rate limited | 429 | `{error, retry_after}` | Wait and retry |
| Server error | 500 | `{error, request_id}` | Report to support |

**Logging Requirements:**
- All errors logged with correlation ID
- Stack traces for 500 errors
- User action logged for audit

---

## 10. Integration Points Validation

### Stripe Webhooks

| Event | Validation | Action | Failure Recovery |
|-------|-----------|--------|------------------|
| payment_intent.succeeded | Verify signature | Update subscription | Retry 3x |
| customer.subscription.deleted | Verify signature | Deactivate user | Manual review |
| invoice.payment_failed | Verify signature | Send notification | Queue for retry |

**Validation Rules:**
- Signature must match using webhook secret
- Event ID must be unique (idempotency)
- Timestamp within 5 minutes

### GitHub Webhooks

| Event | Validation | Action | Failure Recovery |
|-------|-----------|--------|------------------|
| pull_request.opened | Verify signature | Trigger PR agent | Log and alert |
| push | Verify signature | Trigger CI/CD | Manual trigger |
| issues.opened | Verify signature | Create task | Queue |

---

## Summary

This validation matrix ensures:

1. **Input Validation**: All inputs validated against defined rules
2. **Output Verification**: Expected outputs clearly defined
3. **Failure Modes**: All failure scenarios documented
4. **Recovery Procedures**: Clear recovery paths for failures
5. **Pre/Post Conditions**: State requirements documented
6. **Performance Targets**: SLAs defined for critical paths
7. **Security Controls**: Security validation at all layers
8. **Integration Contracts**: External integration validation rules

Use this matrix when:
- Writing new tests
- Debugging failures
- Reviewing code
- Designing new features
- Conducting security audits
