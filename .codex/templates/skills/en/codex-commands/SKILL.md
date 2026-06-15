---
name: codex-commands
description: Use when running `$codex-*` shortcuts and interpreting their output.
---

# codex-commands

Apply `../_references/core-rules.md` first.

## Must

- Prefer shortcuts for state, TASK, gates, and context queries.
- Treat hook block output as user-visible policy output.
- Report command, exit code, and stderr when a shortcut fails.

## Procedure

- Check help or status before guessing command syntax.
- Use summary, trace, or pack commands for long JSONL state.
- Recheck git status when shortcut state and git state conflict.
- Avoid repeated runs that needlessly mutate state files.

## Expert Rules

- Distinguish read-only shortcuts from state-mutating shortcuts.
- Prefer --for-ai output over verbose human output when available.
- Treat hook blocks as policy decisions, not glitches.
- Do not manually edit around shortcut failure without recording cause.
- Before rerunning a command, check whether input state changed.
- Cross-check shortcut output with git status, staged diff, and TASK state.
- Check help or --for-ai support before using shortcuts.
- Record manual verification equivalence when bypassing a shortcut.

## Expert Checks

- Check that shortcut failure was not bypassed by manual edits.
- Check that `--for-ai` output was used when available.
- Check that hook policy was not ignored through retries.

## Failure Modes

- Long JSONL is read directly and stale state is trusted.
- Shortcut failure is summarized as success.
- A hook block is bypassed with another shell command.
- State-mutating command is repeated as if it were verification.
- Hook output is confused with command result.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- State shortcut is broken and no fallback is safe.
- Hook explicitly blocks the requested action.
- Command output contradicts git status.

## Verify

- shortcut status.
- git status.
- gate output.

## Evidence

- Report shortcut, exit code, and key stdout.
- On failure, record stderr and fallback reasoning.
- Final git status and TASK state agree.
- Fallback command and original shortcut failure cause are reported.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
