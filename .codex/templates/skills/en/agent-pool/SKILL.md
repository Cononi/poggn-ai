---
name: agent-pool
description: Use for MAW worker names, thread reuse, cleanup, and context isolation.
---

# agent-pool

Apply `../_references/core-rules.md` first.

## Must

- Separate reusable role definitions from reusable live thread context.
- Default to fresh workers unless workflow and ownership both match.
- Label workers with role, feature, stage, and lane.

## Procedure

- Check pool status and thread cap before spawning.
- Close completed threads after collecting their summaries.
- Reuse a thread only for the same workflow and the same ownership.
- Re-dispatch only the lane that failed main review with the same contract.
- Start fresh when files, branch, or TASK context changed.

## Expert Rules

- Treat thread reuse as context risk, not just cost reduction.
- Name workers so humans can trace incidents later.
- Clean completed threads before spawning at pool capacity.
- Use fresh workers when TASK, branch, or file owner differs.
- Require summaries with changed files, verification, and residual risk.
- Refresh git state before long-lived workers modify files.
- Allow reuse only for same TASK, same lane, and same file ownership.
- Reuse an existing worker for retry only with same TASK/lane/ownership.
- Send only concise blocker findings and expected changes on retry.
- Use worker label format role/task/lane/stage/files-scope.

## Expert Checks

- Check that old context cannot outrank current files.
- Check that workers did not edit outside their ownership.
- Check that completed workers no longer consume max_threads.

## Failure Modes

- Old workflow context overwrites new files.
- Completed threads keep consuming max_threads.
- Worker labels match while actual ownership differs.
- Subagent output conflicts with main diff without integration review.
- Live workers touch the same file concurrently.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Stale worker context is reused across workflows.
- Thread cap is full with completed workers.
- Worker ownership is missing or ambiguous.
- Failed main review is retried without new findings.

## Verify

- agent pool status.
- open thread list.
- worker summary collection.

## Evidence

- Pool status separates running, completed, and closed threads.
- Each worker has an owned file list.
- Final report includes remaining open thread count.
- Collect summary, changed files, tests, and blockers before close.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
