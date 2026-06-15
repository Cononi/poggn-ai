# Implementation agent rules

In MAW, `backend` is only an example.

An implementation agent creates deliverables in its own area.

Default implementation agents are:

```text
backend
frontend
database
integration
devops
docs
performance
```

A custom agent becomes an implementation agent when registered in
`.codex/state/agent_roles.json`.

When an implementation TASK becomes `[x]`, the event bus selects downstream agents.

```text
implementer/order done
-> needed test_writer
-> needed test_runner
-> needed qa
-> needed refactor
-> needed security
```

Other implementation agents keep working on the next ready TASK.

```text
frontend/order under review
backend/payment implementation running
integration/webhook implementation running
```

Downstream agents are not always created.

They are selected from changed files, risk, feature, and policy.
