---
name: database-migration
description: Use for schema, migration, index, constraint, and backfill changes.
---

# database-migration

Apply `../_references/core-rules.md` first.

## Must

- Split schema work into expand, backfill, switch, and contract phases.
- Define rollback and restore paths before data-loss changes.
- Review lock risk and online options for large table DDL.

## Procedure

- Add nullable fields, backfill, then enforce not-null when safe.
- Prefer add-copy-read-switch-drop for renames.
- Check existing data before adding constraints.
- Separate app deploy order from DB deploy order.

## Expert Rules

- Treat migration as data lifecycle change, not only code change.
- Make expand/contract safe for two app versions running together.
- Estimate lock, replication lag, and rollback time for large DDL.
- Justify indexes with query plan, cardinality, and write overhead.
- Make backfill restartable with chunk-level progress.
- Check existing data before strengthening constraints.
- Mark down migration possibility separately from irreversible changes.
- Give backfills chunk size, resume point, timeout, and metrics.

## Expert Checks

- Check ORM entity changes against migration order.
- Check indexes against real query patterns and cardinality.
- Check that partial failures can be rerun safely.

## Failure Modes

- Rename or drop breaks the previous app version in one step.
- not null is added before backfill and default strategy.
- Rollback reverts schema but not damaged data.
- ORM entity deploys before migration compatibility exists.
- Migration passes only because test and prod DB dialects differ.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Destructive migration lacks backup or rollback path.
- Large table DDL may block writes without mitigation.
- App version and schema version are incompatible.

## Verify

- migration dry run.
- rollback plan.
- query/index review.

## Evidence

- Deploy order and compatibility matrix exist.
- Dry run or migration test result exists.
- Rollback or forward-fix procedure is recorded.
- FK, unique, and not-null checks include orphan and duplicate queries.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
