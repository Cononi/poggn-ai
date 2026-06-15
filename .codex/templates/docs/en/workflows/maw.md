# MAW multi-agent pipeline

$maw is for large work split into feature lanes.
It recommends agents first, then lets the user select, add, or remove them.

## Core concepts

```text
agent = role
skill = procedure
lane = real parallel execution unit
wave = lanes run and merged together
pipeline = lane dependency graph
epic = whole goal
```

Order and payment are separate lanes.

```text
T002 Order REST API   L002 backend implement
T003 Payment REST API L003 backend implement
```

Both use the backend agent, but each runs in its own worktree.
Spring Boot, JPA, and Swagger are skills used by the backend agent.

## Real multi-agent flow

MAW does not only run backend, QA, and security at the end.
When an implementation task finishes, downstream agents receive it.

```text
L002 backend order implement
  -> L004 test order
  -> L006 qa order
  -> L008 refactor order
  -> L010 security order

L003 backend payment implement
  -> L005 test payment
  -> L007 qa payment
  -> L009 refactor payment
  -> L011 security payment
```

At first, backend/order and backend/payment are ready together.
If order finishes first, order QA can start while payment continues.

## Ready queue

Show runnable lanes only.

```text
$codex-pipeline ready --for-ai
```

Prepare worktrees for ready lanes only.

```text
$codex-pipeline prepare
```

Create a CSV for ready lanes only.

```text
$codex-pipeline csv --ready
```

Create the subagent execution prompt.

```text
$codex-pipeline prompt
```

## /agent and agent lists

/agent is for switching or inspecting active subagent threads.
It may be empty before agents are spawned.

Use these commands to list configured custom agents.

```text
$codex-agents list
$codex-agents check
```
