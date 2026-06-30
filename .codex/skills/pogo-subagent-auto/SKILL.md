---
name: pogo-subagent-auto
description: `$pogo-subagent-auto` 상태와 정책을 확인하거나 수정할 때 사용한다. Use when checking or changing SubAgent auto on/off/status, SubAgent evidence, `pogo-state/subagent-evidence.json`, or mandatory SubAgents before git commit/push/merge.
---

# Pogo SubAgent Auto

## Purpose

`$pogo-subagent-auto` controls whether development, review, QA, and code-change work should primarily use Subagents.
It is a focused policy flag for the main orchestrator, not a hook-driven spawn mechanism.
`pogo-settings` remains the settings owner for storage and command parsing.

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

`subagent.auto` is a policy switch read by the main orchestrator.
Hooks cannot spawn Subagents directly.
Current hook limits are: shortcut prompt blocking and pre-tool git/evidence gate checks.
Actual parallel/Subagent execution must be started by main via multi-agent tools.

When `pogo-state/pogo-settings.json` has `subagent.auto=true`:

1. Main orchestrator must post a pre-work plan report (goal, scope, delegation targets, expected evidence) and then start at least one relevant Subagent for development/review/QA work.
2. Main orchestrator should minimize direct exploration and delegate first; it should start with least direct analysis and immediate Subagent launch.
3. Main orchestrator may do direct work only for: user request, confirmed failure, Subagent disagreement, security/data-loss risk, or unavailable Subagent.
4. Release note draft/check work uses deterministic helper output plus Subagent review; main consumes only the summary, report path, command evidence, and blocker decision.
5. Main must not repeatedly read full diffs, raw logs, large `pogo-state` reports, or full release bodies unless a failure, disagreement, or user request requires it.
6. `pogo-verifier` or `pogo-tester` must produce PASS evidence before completion.
7. Before git `commit`, `push`, or `merge`, the hook requires `pogo-state/subagent-evidence.json`.

Thin Mode rules:

- Main orchestrator consumes `summary`, `changed_files`, `evidence`, `risks`, `report_file`, `reviewer_decision` from Subagent results by default.
- `report_file` should be under `pogo-state/subagent-reports/<YYYY-MM-DD>/<HHMMSS>-<sanitized-branch>/<task-id>/<agent-name>.md` and include timezone-aware date/time and sanitized branch path info in the path.
- `summary` must include: reason for work, done work, outcome, reviewer-agent result, recheck-needed flag, and completion quality.
- Report language follows `pogo-state/pogo-settings.json` `lang` (ko/en/bilingual with bilingual summaries).
- Subagent `summary` is 3 lines or less, `risks` is 3 bullets or less, and `evidence` is command/status proof instead of raw logs.
- Raw logs, full diffs, and tool traces are requested only for user request, failure, Subagent disagreement, Subagent unavailability, or security/data-loss risk.
- `pogo-state/subagent-evidence.json` stores status fields only. Do not store logs, diffs, prompts, or long analysis in evidence.

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
- `changedFiles` must match the current git changed file list. It can be an empty list when the current git changes are empty.
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
