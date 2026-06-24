# Migration Runbook: <title>

## Authorization

- Mode: SHARED | PRODUCTION
- Change owner:
- Operator:
- Reviewer:
- Approved target:
- Approved maintenance window:

## Exact Target

- Environment:
- DBMS and version:
- Host or cluster identifier:
- Database and schema:
- Migration tool and version:
- Application versions currently running:

Do not place credentials in this document.

## Preconditions

- [ ] Target identity confirmed
- [ ] Expected schema version confirmed
- [ ] Required free storage confirmed
- [ ] Backup or recovery point confirmed
- [ ] Restore or roll-forward owner confirmed
- [ ] Monitoring dashboards open
- [ ] Stop conditions agreed
- [ ] Old and new application compatibility confirmed

## Expected Impact

- Tables and rows:
- Lock behavior:
- Expected I/O and log growth:
- Replica impact:
- User-visible impact:

## Stop Conditions

- Lock wait:
- Latency:
- Error rate:
- Replication lag:
- Storage or log usage:
- Data count mismatch:
- Other:

## Execution Phases

### Phase 1

- Purpose:
- Exact reviewed command or deployment action:
- Expected result:
- Verification query or check:
- Evidence location:

### Phase 2

- Purpose:
- Exact reviewed command or deployment action:
- Expected result:
- Verification query or check:
- Evidence location:

## Backfill Control

- Selection key:
- Batch size:
- Checkpoint:
- Sleep or throttle:
- Retry limit:
- Progress metric:
- Completion query:

## Failure Response

- Immediate stop action:
- Safe rollback action:
- Roll-forward action:
- Data reconciliation:
- Escalation owner:

## Post-Change Verification

- [ ] Migration state confirmed
- [ ] Constraint and index state confirmed
- [ ] Data counts and invariants confirmed
- [ ] Application error and latency checked
- [ ] Lock waits and long transactions checked
- [ ] Replication health checked
- [ ] Next contract step recorded

## Result

- Started at:
- Finished at:
- Result: PASS | FAILED | PARTIAL | NOT RUN
- Applied versions:
- Rows processed:
- Incidents or deviations:
- Evidence:
