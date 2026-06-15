---
name: worker-pool
description: Use for MAW worker reuse, thread cleanup, and context isolation.
---

# worker-pool

Apply `../_references/core-rules.md` first.

## Must

- Treat workers as actual subagent threads.
- Separate role config reuse from thread context reuse.
- Default to fresh workers; reuse is the exception.

## Procedure

- Use worker labels that humans can trace later.
- Collect summaries before closing completed workers.
- Clean completed threads before hitting max_threads.
- Check pool status together with the ready queue.

## Expert Rules

- Treat workers as live threads with context and file ownership.
- Reuse only within same workflow, owner, and branch state.
- Tell workers not to revert others because they are not alone.
- Collect summary, review diff, then close completed workers.
- Read pool status together with ready queue for idle versus bottleneck.
- Include forbidden files and conflict rules in prompts.
- Use worker states new, running, needs-review, closed, and blocked.
- Never reuse thread context across TASKs even for the same role.

## Expert Checks

- Check whether workers were reused outside the same workflow.
- Check whether a worker touched files outside ownership.
- Include open worker status in the final report.

## Failure Modes

- Stale worker edits without current main diff.
- Two workers change the same file in conflicting ways.
- Completed thread blocks new worker spawn.
- Main guesses worker result without final report.
- Unresponsive abandoned worker remains without criteria.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Worker context is stale or cross-workflow.
- Completed worker still occupies capacity.
- Ownership cannot be assigned to the worker.

## Verify

- worker pool status.
- thread cleanup.
- final worker report.

## Evidence

- Worker thread id, owner, and status are listed.
- Completed worker changed files and verification are collected.
- Open worker and close status are reported.
- Final report includes open, closed, and blocked worker counts.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
