---
name: rollback
description: Use for single-TASK revert, full rollback, and safe recovery scope.
---

# rollback

Apply `../_references/core-rules.md` first.

## Must

- Separate feature removal from incident mitigation.
- Use TASK trace to find related commits and files.
- Never revert unrelated changes.

## Procedure

- Prefer revert commits; avoid reset for shared history.
- Review forward fix and data repair when migrations exist.
- Separate config, secret, and deploy rollback by environment.
- Run tests and smoke paths after rollback.

## Expert Rules

- Treat rollback as reducing current incident impact, not time travel.
- Choose targets by user impact and dependencies, not only commits.
- Rollback schema, data, and app compatibility separately.
- Review previous/current client and server combinations for partial rollback.
- Consider propagation time and cache for config and secret rollback.
- Run smoke and user-path checks before root-cause analysis.
- Map forward dependencies and follow-up commits before rollback.
- Plan DB, queue, cache, and external API recovery separately from code revert.

## Expert Checks

- Check compatibility matrix for partial rollback.
- Check conflicts instead of resolving them by guesswork.
- Check whether user changes would be reverted.

## Failure Modes

- reset loses shared history or user changes.
- Migration revert damages data further.
- Feature flag rolls back but background job continues.
- Rollback commit includes unrelated files.
- Partial rollback lacks API or schema compatibility table.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Rollback would remove unrelated user changes.
- Migration rollback risks data loss without plan.
- Target commit set is ambiguous.

## Verify

- task trace.
- revert diff.
- post-rollback smoke test.

## Evidence

- TASK trace and target commit list exist.
- Revert diff excludes unrelated changes.
- Post-rollback smoke result and residual risk are reported.
- Revert conflicts record per-file intent and test evidence.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
