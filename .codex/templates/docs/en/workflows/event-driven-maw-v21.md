# Event-driven MAW

MAW selects downstream agents from TASK completion events.

Implementation agents implement only.

Test code is written by test_writer.

Test execution is handled by test_runner.

QA, refactor, and security run based on changes and risk.

Not every downstream agent runs every time.

```text
code changed -> test_writer, test_runner
public API or large change -> qa
large maintainability risk -> refactor
payment, auth, token, secret -> security
```

When a TASK becomes `[x]`, the event bus creates downstream lanes.

While downstream agents run, backend continues the next ready TASK.

```text
implementer/order done
-> test_writer/order and qa/order ready

implementer/payment running
-> implementation can continue
```

Check the ready queue:

```text
$codex-pipeline ready --for-ai
```

Check workers:

```text
$codex-events workers --for-ai
```
