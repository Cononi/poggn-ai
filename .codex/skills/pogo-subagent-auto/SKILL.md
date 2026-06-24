---
name: pogo-subagent-auto
description: `$pogo-subagent-auto` 상태와 정책을 확인하거나 수정할 때 사용한다. Use when checking or changing SubAgent auto on/off/status, SubAgent evidence, `.codex/state/subagent-evidence.json`, or mandatory SubAgents before git commit/push/merge.
---

# Pogo SubAgent Auto

## Purpose

`$pogo-subagent-auto` controls whether development, review, QA, and code-change work must use Subagents.
It is a focused policy skill. `pogo-settings` remains the shared settings and hook implementation owner.

## Command Surface

Use the existing settings entrypoint:

```text
$pogo-subagent-auto [status|on|off|toggle]
$pogo-settings subagent status
$pogo-settings subagent auto on|off|toggle
$pogo-settings evidence status|clear
```

Bare `$pogo-subagent-auto` means `status`.

## Enforcement Model

Hooks cannot spawn Subagents directly.
They can block shortcut prompts and pre-tool git commands.

When `.codex/state/pogo-settings.json` has `subagent.auto=true`:

1. Main orchestrator must start at least one relevant Subagent for development/review/QA work.
2. `pogo-verifier` or `pogo-tester` must produce PASS evidence before completion.
3. Before git `commit`, `push`, or `merge`, the hook requires `.codex/state/subagent-evidence.json`.

Evidence contract:

```json
{
  "version": 1,
  "branch": "feat/example",
  "head": "current HEAD commit",
  "agents": [{"name": "pogo-verifier", "result": "PASS"}],
  "changedFiles": ["path/to/file"]
}
```

Rules:

- `version` must be `1`.
- `branch` must match the current branch.
- `head` must match the current `HEAD`.
- `agents` must include PASS from `pogo-verifier` or `pogo-tester`.
- `changedFiles` must match the current git changed file list.
- evidence 24 hours or older is rejected as a secondary guard.
- stale evidence is cleared with `$pogo-settings evidence clear`.

## Verification

Use focused checks:

```bash
python3 .codex/script/pogo_settings.py subagent status
python3 .codex/script/pogo_settings.py evidence status
printf '%s\n' '{"prompt":"$pogo-subagent-auto status"}' | python3 .codex/hooks/pogo_policy_hook.py user-prompt-submit
printf '%s\n' '{"tool_input":{"cmd":"git commit -m test"}}' | python3 .codex/hooks/pogo_policy_hook.py pre-tool-use
```

Report `PASS`, `FAILED`, `PARTIAL`, or `NOT RUN`.
Do not claim hook enforcement works unless a dry run was executed.
