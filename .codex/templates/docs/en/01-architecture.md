# Architecture

The workflow is layered.

```text
request -> agents -> skills -> TASKs -> lanes
lanes -> worktrees -> commits -> gates -> review
```

Agents own narrow responsibilities.
Examples include backend, frontend, database, integration, devops, docs, QA, and security.
Skills provide procedures such as JPA, OpenAPI, quality gate, and refactoring.
Lanes make same-agent work parallel, such as order and payment backend work.
TASKS.md is only a human summary. JSONL files are the source of truth.
