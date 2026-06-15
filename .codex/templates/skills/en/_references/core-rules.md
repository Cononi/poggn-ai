# Core Skill Rules

Apply these rules whenever a skill is active.

## Must

- Check TASK scope, ownership, changed files, and verification commands first.
- Keep implementation small and declare public contract changes explicitly.
- Do not hide business rules in controllers, UI, or script glue.
- Check validation, authorization, error shape, and testability at boundaries.
- Report failed test, build, lint, security, sandbox, or network results.

## Never

- Do not revert, overwrite, stage, or commit unrelated user changes.
- Do not commit secrets, tokens, private keys, real credentials, or bulky output.
- Do not report done, pass, safe, or complete without verification evidence.
- Do not leave large files, duplicated logic, or mixed responsibility in scope.

## Done

A completion report includes changed files, verification run, skipped or blocked
checks, remaining risk, and TASK/commit linkage.
