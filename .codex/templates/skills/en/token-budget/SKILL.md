---
name: token-budget
description: Use to manage SAW/MAW token, context, lane, and wave budgets.
---

# token-budget

Apply `../_references/core-rules.md` first.

## Must

- Estimate size by file count, diff lines, and context volume.
- Treat SAW budget overflow as a signal to switch to MAW.
- Reduce scope, not verification, when budget is tight.

## Procedure

- Budget MAW by lane and wave, not by the whole epic.
- Save tokens with context pack and targeted reads.
- Give subagents only required files and goals.
- Load large references by heading and search term.

## Expert Rules

- Treat budget as safely reviewable change surface, not answer length.
- Resolve token pressure by reducing scope, not skipping required files.
- Keep MAW lanes and waves reviewable even when the epic is large.
- Give subagents only goal, owner files, forbidden files, and output contract.
- Summarize logs by root-cause lines and trim repeated traces.
- Treat budget overflow as a split-design signal.
- Estimate budget from files, diffstat, references, and log size.
- After compaction, resync latest TASK, HEAD, and changed files.

## Expert Checks

- Check whether required files were skipped to save tokens.
- Check whether raw repeated logs were pasted needlessly.
- Check whether a lane is too large to review.

## Failure Modes

- Implementation starts without required contract files.
- One lane is too large to review or roll back.
- Verification is omitted to fit budget.
- Subagent prompt includes whole conversation and irrelevant history.
- Missing required files is reported merely as a budget issue.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Required context cannot fit without splitting work.
- Verification would be omitted to stay under budget.
- Subagent prompt would be ambiguous or oversized.

## Verify

- context pack size.
- lane split.
- verification retained.

## Evidence

- File count, diff lines, and context-size estimate exist.
- Split rule and follow-ups are recorded.
- Verification remains after scope reduction.
- Long logs are reduced to command, key error, and file location.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
