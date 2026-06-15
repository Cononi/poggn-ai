# MAW Subagent Execution Contract

MAW is not complete when it only creates TASK, lane, or CSV state.
Actual Codex subagent threads must be spawned for ready lanes.

## Must

1. Run `$codex-risk classify --for-ai` first.
2. Keep MAW when the user explicitly invoked `$maw`, even if risk suggests SAW.
3. Run `$codex-context pack --for-ai` to inspect current state compactly.
4. Create implementation lanes with `$codex-work-items apply`.
5. Inspect `$codex-pipeline ready --for-ai` plus csv/prompt output.
6. Check agent configuration with `$codex-agents check/list`.
7. Spawn one real subagent per ready lane with the current session capability.
8. Spawn downstream lanes only after the implementation TASK has a commit link.
9. Close completed subagent threads after integrating results.

## Never

- Do not let the main thread implement ready implementation lanes.
- Do not mark TASKs done without commit linkage.
- Do not create downstream lanes and skip actual execution.

## Blocker

MAW fails if `/agent` shows only main or the main thread implements the lane.
