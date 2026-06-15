---
name: event-driven-maw
description: Use to trigger downstream agents from TASK completion events.
---

# event-driven-maw

Apply `../_references/core-rules.md` first.

## Must

- Treat the event source as a TASK completion linked to a commit.
- Select downstream agents from changed files and risk.
- Always include security for auth, permission, or secret changes.

## Procedure

- Attach database or JPA checks to schema and query changes.
- Attach component and TS checks to frontend UI changes.
- Deduplicate events by root lane and commit.
- Spawn ready lanes, not just records describing them.

## Expert Rules

- Trust events only after TASK completion is linked to a commit.
- Select downstream lanes from changed files, risk, and domain tags.
- Force security events for auth, secret, permission, or deploy changes.
- Attach DB/JPA validation to schema and query changes.
- Attach type, accessibility, and visual-state checks to frontend changes.
- Record lane creation and subagent spawn separately.
- Use TASK id, commit SHA, and changed-file hash as event idempotency key.
- Map file patterns into auth, DB, API, UI, CI, and docs downstream lanes.

## Expert Checks

- Check that downstream lanes were actually spawned.
- Check that high-risk changes have QA and security coverage.
- Check that finalize conditions are explicit and satisfied.

## Failure Modes

- Downstream is created from a TASK completion without commit.
- Duplicate events run the same validation repeatedly.
- Ready lane stays on dashboard without spawning.
- Downstream failure does not affect upstream completion assessment.
- Delete, rename, or migration changes are treated as normal file risk.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- No commit link for the completion event.
- Ready downstream lane remains unspawned.
- Security-impacting change skips security review.

## Verify

- event log.
- ready queue.
- downstream reports.

## Evidence

- Event id, root lane, and commit hash are recorded.
- Selected downstream roles and exclusions are explained.
- Spawn result is linked to final report.
- Event result is one of spawned, deduped, blocked, or skipped.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
