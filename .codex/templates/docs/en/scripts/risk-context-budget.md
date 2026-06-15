# risk, context, budget

This page explains token saving and safe workflow routing.

## Principle

AI should not read the whole repository first.
Scripts compute risk and context summaries first.

```text
$codex-risk classify --text "request" --for-ai
$codex-context pack --for-ai
$codex-budget status
```

## $codex-budget

SAW budget is the limit for a small patch.

MAW budget is not the total epic limit.

For MAW, apply budget per lane, wave, and PR/MR.

```text
$codex-budget suggest --text "order payment" --for-ai
$codex-budget gate --staged --mode maw --for-ai
$codex-waves plan
```

## Wave execution

Split large work into waves.

```text
$codex-waves assign
$codex-waves next
$codex-lanes list --wave W001
$codex-lanes csv --wave W001
$codex-lanes prompt --wave W001
```

Verify and merge W001 before moving to W002.

## Recommended loop

Use SAW like this.

```text
$codex-risk classify --text "request" --for-ai
$codex-saw init ...
$codex-context pack --for-ai
small edit
$codex-verify gate --staged --mode saw --for-ai
$codex-task commit T001 --message "message"
```

Use MAW like this.

```text
$codex-risk classify --text "request" --for-ai
$codex-state init --workflow maw ...
$codex-work-items apply ...
$codex-waves plan
$codex-lanes csv --wave W001
```
