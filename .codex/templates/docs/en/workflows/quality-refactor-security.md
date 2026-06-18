# Quality, refactor, and security flow

No implementation is complete without verification.

MAW and SAW use different verification shapes.

## MAW flow

MAW is for large work and may use separate TASKs and lanes.

```text
implement -> test -> QA -> quality gate -> refactor check -> security gate -> review
```

A MAW feature lane commit must pass the quality gate first.

```text
$codex-quality gate --staged --for-ai
```

Tests and security can be handled by separate test, QA, and security TASKs.

## SAW flow

SAW is for small work and does not create an agent chain.

It still must run tests and security checks.

SAW verifies with one gate.

```text
$codex-verify gate --staged --for-ai
```

This gate runs these checks.

```text
staged quality gate
changed-code targeted test
staged security gate
```

If code changed and no test command exists, the gate fails.
Default verification includes modified files and new untracked files.

Configure test commands here.

```text
.codex/state/verify.json
```

## Refactor decision

Refactoring must preserve behavior.

Do not change public APIs, DB schema, or auth policy without approval.

Check the need with a script first.

```text
$codex-refactor analyze --for-ai
```

## Security standard

The security gate scans for secrets, tokens, private keys, and passwords.

Do not prepare a PR or MR while security findings remain.
