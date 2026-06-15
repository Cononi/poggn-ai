---
name: task-trace
description: Use to verify TASK, lane, commit links, and change traceability.
---

# task-trace

Apply `../_references/core-rules.md` first.

## Must

- Treat JSONL as source state and TASKS.md as output.
- Check TASK id, lane id, and commit hash together.
- Verify commit, files, and checks before done state.

## Procedure

- Derive file lists from commit diffs.
- Link each TASK when multiple TASKs share one commit.
- Record state commit and product commit relationships.
- Prefer script recovery when trace state breaks.

## Expert Rules

- Treat structured state as source; markdown is rendered output.
- Mark TASK done only when commit, files, verification, and owner link.
- If one commit closes many TASKs, link the same hash to each.
- Check rollback impact through TASK dependency, not only commit graph.
- Recover trace from scripts and git diff, not guesses.
- Treat trace gaps as blockers before final report.
- Check commit hash, changed files, and verification before TASK done.
- When one commit closes many TASKs, record hash and file basis for each.

## Expert Checks

- Check whether TASKS.md changed without JSONL state.
- Check whether multiple TASKs were hidden under one TASK.
- Check rollback impact through trace.

## Failure Modes

- TASKS.md is checked off while JSONL/state is unchanged.
- Commit exists but no TASK owns its output.
- Several work items are hidden inside one TASK.
- State commit and product commit relationship is lost.
- TASKS.md changes without JSONL or state source.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Commit cannot be tied to the TASK.
- Trace source and rendered TASK output disagree.
- Rollback impact cannot be reconstructed.

## Verify

- task trace.
- git show --name-only.
- state consistency check.

## Evidence

- TASK id, lane id, commit hash, and file list are linked.
- Trace command and git show agree.
- Verification result is recorded before done.
- Trace links rollback, follow-up, and state-only commit relationships.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
