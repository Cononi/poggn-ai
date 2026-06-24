---
status: draft
risk: D1
owner: unknown
database: unknown
database-version: unknown
migration-tool: unknown
data-access: unknown
---

# Database Change: <title>

## Context

- Problem:
- Expected outcome:
- Related Issue or Spec:

## Current Evidence

- Schema or migration path:
- Query or repository path:
- Runtime configuration path:
- Current DBMS and version:
- Table size and traffic evidence:

## Invariants

- INV-001:
- INV-002:

## Access Patterns

| ID | Operation | Predicate or join | Order | Result bound | Frequency |
|---|---|---|---|---:|---:|
| Q-001 | read |  |  |  |  |

## Proposed Schema and SQL

- Tables:
- Columns and types:
- Constraints:
- Indexes and query mapping:
- Data lifecycle:

## Compatibility

- Old app with expanded schema:
- New app with old schema:
- New app with expanded schema:
- Contract precondition:

## Migration Plan

### Phase 1: Expand

- Change:
- Lock or rewrite risk:
- Verification:
- Abort condition:

### Phase 2: Migrate

- Backfill selection:
- Batch and checkpoint:
- Idempotency:
- Throttle and metrics:
- Verification:

### Phase 3: Switch

- Read path:
- Write path:
- Feature flag or rollout:
- Consistency check:

### Phase 4: Contract

- Removal:
- Preconditions:
- Verification:

## Transactions and Concurrency

- Transaction boundary:
- Isolation:
- Lock order:
- Conflict handling:
- Retry and idempotency:

## ORM or Data-Access Impact

- Technology and version:
- Mapping or mapper changes:
- Generated or explicit SQL:
- Fetch, cascade, flush, cache impact:

## Verification

| Check | Command or method | Environment | Result |
|---|---|---|---|
| Migration from baseline |  |  | NOT RUN |
| Empty schema migration |  |  | NOT RUN |
| Constraint tests |  |  | NOT RUN |
| Query plan |  |  | NOT RUN |
| Concurrency test |  |  | NOT RUN |
| Recovery test |  |  | NOT RUN |

## Operations

- Metrics:
- Alert or stop conditions:
- Backup or recovery point:
- Rollback or roll-forward:
- Post-deploy checks:

## Open Items

- [OPEN]
- [UNKNOWN]
- [ASSUMPTION]
