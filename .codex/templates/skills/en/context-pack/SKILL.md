---
name: context-pack
description: Use to compact TASK, lane, and changed-file context.
---

# context-pack

Apply `../_references/core-rules.md` first.

## Must

- Run before work, after resume, and before subagent spawn.
- Interpret workflow, phase, and changes from the pack.
- Recheck git status when pack and repository state differ.

## Procedure

- In SAW, read around changed files first.
- In MAW, rerun pack in the lane worktree.
- Use task trace to narrow an overly broad pack.
- Include a short pack summary in subagent prompts.

## Expert Rules

- Use pack as workflow surface, not final proof.
- Refresh pack before later decisions if files changed.
- Separate main worktree pack from lane worktree pack in MAW.
- Narrow broad packs with task trace, git diff, and rg.
- Check untracked and staged state even when change_count is zero.
- Send subagents a short pack summary, not the whole pack.
- Summarize TASK, lane, phase, and changed files before work.
- Explain TASK-scope fit before editing files absent from the pack.

## Expert Checks

- Check whether files changed after the pack was captured.
- Check whether files outside the pack were read without reason.
- Check whether full repo scanning replaced pack usage.

## Failure Modes

- Files outside the pack are changed without reason.
- Pack and git status conflict is ignored.
- Commit-time judgment uses an old pack.
- Large TASKS is read instead of using pack.
- MAW lane uses only root pack and skips lane worktree pack.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Pack command fails and state cannot be reconstructed.
- Pack shows an active conflicting workflow.
- Pack lacks the TASK needed for safe edits.

## Verify

- context pack.
- task trace.
- git status.

## Evidence

- Pack timestamp and workflow path are reported.
- Pack and git status differences are resolved.
- Subagent prompt includes relevant pack summary.
- Pack and git status mismatch resolution is recorded.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
