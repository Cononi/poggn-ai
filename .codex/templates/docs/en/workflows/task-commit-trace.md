# TASK and commit trace

Each TASK needs linked commits. Commit messages include Codex footers.

```text
Codex-Task: T002
Codex-Lane: L002
Codex-Agent: backend
Codex-Skills: spring-boot,jpa
```

TASKS.md shows A, M, D, and R file summaries. Use scripts for full diffs.

```text
$codex-task files T002
$codex-task diff T002 --name-status
```
