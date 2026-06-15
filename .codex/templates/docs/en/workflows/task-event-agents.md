# TASK completion events and downstream agents

MAW does not run every agent unconditionally at the start.

A TASK emits an event when a commit is linked and the checkbox becomes `[x]`.

That event creates only the downstream agents that are needed.

Example:

```text
implementer/order done
-> test_writer/order
-> test_runner/order
-> qa/order
-> refactor/order when needed
-> security/order when needed
```

Order review can start while payment implementation is still running.

backend continues the next ready implementation TASK.

Each downstream agent performs only its own role.

test_writer writes tests but does not run them.

test_runner runs tests but does not implement product code.

qa reviews user flow and regression risk.

refactor performs behavior-preserving cleanup only.

security reviews security risks only.

Check ready queue:

```text
$codex-pipeline ready --for-ai
```

Check workers:

```text
$codex-events workers --for-ai
```
