# Agent pipeline

Agent pipeline is the main execution model for MAW.

## Why it exists

Simple parallel execution only runs implementation lanes together.
Then QA, refactor, and security tend to happen once at the end.

Agent pipeline passes each completed implementation result downstream.

```text
구현/order done -> qa/order ready
implementer/payment running -> continues in parallel
```

## Stages

```text
foundation
implement
test
qa
refactor
security
```

## Dependency

Each lane stores upstream lane ids in deps.

A lane is ready when all deps are done or merged.

```text
$codex-pipeline ready --for-ai
```

## Worktree setup

Only ready lanes get worktrees.

Downstream lanes start from the nearest upstream branch.

```text
$codex-pipeline prepare
```

## CSV batch

```text
$codex-pipeline csv --ready
$codex-pipeline prompt
```

One CSV row maps to one subagent worker.

## Completion

Each worker records a lane commit.

```text
$codex-task commit T002 --lane L002 --message "Order REST API"
```

If a review lane has no code changes, use an empty commit as evidence.

```text
$codex-task commit T006 --lane L006 --message "QA order" --allow-empty
```

## Trace

TASKS.md shows stage, agent, wave, deps, and commit.

Full diffs stay out of TASKS.md.

```text
$codex-task diff T002 --name-status
$codex-task files T002
```
