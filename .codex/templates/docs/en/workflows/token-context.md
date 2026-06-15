# Token optimization and context control

Do not make the AI read long documents to decide state.

Scripts calculate state, progress, changed files, and commit links.

The AI sees short JSON summaries and then acts.

## Basic commands

```text
$codex-context pack --for-ai
$codex-task trace --for-ai
$codex-state summary --for-ai
```

## SAW limit

SAW is micro patch mode.

It has small file and changed-line limits.

If it exceeds the limit, switch to MAW.

## MAW wave limit

A MAW epic may be large.

Only one lane and one wave must fit the budget.

```text
$codex-lanes csv --wave W001
$codex-verify gate --staged --mode maw --for-ai
```

## Reading rule

Do not read all of TASKS.md every time.

Do not read the whole git log every time.

Full diffs are used only when requested or when a gate fails.
