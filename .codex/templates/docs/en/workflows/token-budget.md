# Token budget and wave budget

SAW is for small patches.

If files, code files, or changed lines exceed the budget, stop SAW.
Then switch to MAW or split into a follow-up TASK.

MAW is different.

MAW budget is not the total size limit for a large epic.

```text
An epic may exceed 80 files or 3000 lines.
Only one lane and one wave must stay within budget.
```

Default limits are:

```text
lane: 30 files, 900 changed lines
wave: 6 lanes, 80 files, 3000 changed lines
```

Split large work into waves.

```text
W001 contract, schema
W002 order, payment, member backend
W003 product, cart, coupon backend
W004 frontend screens
W005 test, QA, quality, security
```

Use these commands.

```text
$codex-budget status
$codex-budget suggest --text "order payment rest api" --for-ai
$codex-waves plan
$codex-waves next
```

Prepare and run only one wave.

```text
$codex-lanes prepare --wave W002
$codex-lanes csv --wave W002
$codex-lanes prompt --wave W002
```

If one lane is too large, split the feature again.

```text
order all -> order create, order read, order state, order cancel
payment all -> payment request, payment callback, payment refund
```

Before reading the whole repository, pack context first.

```text
$codex-context pack --for-ai
$codex-context pack --task T001 --for-ai
```

Full diff and full file reads are the last resort.
