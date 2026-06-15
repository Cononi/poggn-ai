---
name: codex-edit-mode
description: Use to manage `.codex` edits versus product code edits.
---

# codex-edit-mode

Apply `../_references/core-rules.md` first.

## Must

- Classify the change as `.codex` feature or product code first.
- Keep those scopes in separate commits when practical.
- Respect edit-mode results and hook policy.

## Procedure

- Adjust mode or request scope when permissions block the work.
- Treat skills, agents, hooks, and scripts as code requiring checks.
- Verify rendered language output after skill or template edits.
- Stage only files belonging to the approved edit scope.

## Expert Rules

- Treat .codex edits as tool-behavior and policy changes first.
- Changing mode expands scope and needs reason plus rollback path.
- Hook, script, and skill edits are execution-system changes.
- Check source templates and rendered output together.
- Separate product code and .codex commits when scopes mix.
- Check policy before solving permission issues with chmod or write workarounds.
- Classify .codex, product code, and generated output before work.
- Require syntax check and dry run for .codex script or hook changes.

## Expert Checks

- Check whether `.codex` changes and product code are mixed.
- Check whether edit mode was used to bypass hooks.
- Check script syntax before committing script changes.

## Failure Modes

- Unrelated files are staged while edit mode remains open.
- Only templates are changed and rendered skills stay stale.
- Hook behavior changes without script syntax validation.
- Product code changes are committed with .codex tool work.
- A change requiring edit mode is bypassed with normal file edits.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Requested edit crosses scope without approval.
- Mode blocks writes and no safer path exists.
- Hook policy rejects the edit.

## Verify

- edit-mode status.
- language render test.
- quality gate.

## Evidence

- Edit scope and excluded files are recorded.
- Render or script syntax validation ran.
- Staged diff stays inside approved scope.
- Record whether source template or rendered output was changed.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
