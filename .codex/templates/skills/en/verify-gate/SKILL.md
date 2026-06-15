---
name: verify-gate
description: Use to enforce quality, test, and security checks before TASK completion.
---

# verify-gate

Apply `../_references/core-rules.md` first.

## Must

- Choose test, lint, build, and security checks by change type.
- Prefer `$codex-verify` when available.
- Report failed command, error, and approval need exactly.

## Procedure

- Do not treat missing tools as pass when tests exist.
- Separate staged-gate results from full-gate results.
- For MAW downstream, verify against the upstream commit.
- Record rerun evidence and pattern for suspected flaky tests.

## Expert Rules

- Use verify to collect completion evidence, not just run tests.
- Choose gates separately for docs, code, and config changes.
- Treat missing tools as skipped with reason, not pass.
- State whether staged or full gate is trusted when they differ.
- Use failure pattern evidence for flaky suspicion.
- Verify MAW downstream against the upstream commit hash.
- Map each changed file type to a minimum verification command.
- Do not pass DB, API, or security changes with unit tests only.

## Expert Checks

- Check whether allow-no-test is used outside docs or metadata.
- Check whether security or quality gates are missing.
- Summarize only root-cause log lines.

## Failure Modes

- allow-no-test skips code verification.
- Full failure log is pasted without root-cause summary.
- Quality or security is missing but verify is called complete.
- Environment failure and product failure are not separated.
- Snapshot change is not checked as a contract change.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Required verification command fails.
- Security or quality gate is skipped for code changes.
- Test environment failure cannot be distinguished from code failure.

## Verify

- verify gate.
- quality gate.
- security gate when relevant.

## Evidence

- Commands, exit codes, and key failure lines are listed.
- Skipped checks include reason and risk.
- Final verdict is pass, fail, or blocked.
- Record repro log line, command, and environment variables.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
