# TASK and commit trace

Each TASK needs linked commits. Commit messages follow the current language
setting and include a subject, body, and footer.

The subject uses conventional commit format.

```text
feat: implement order creation API
```

The body records intent and verification evidence.

```text
Purpose: implement the order creation API.
Scope: TASK T002 / lane L002 / workflow maw
Acceptance: verification and TASK trace are complete.
Verification: codex_verify gate --staged --mode maw
```

The footer records structured Codex trace data.

```text
Codex-Task: T002
Codex-Lane: L002
Codex-Workflow: v1-shop
Codex-Agent: backend
Codex-Skills: spring-boot,jpa
Codex-Verification: codex_verify gate --staged --mode maw
Codex-Language: en
```

TASKS.md shows A, M, D, and R file summaries. Use scripts for full diffs.

```text
$codex-task files T002
$codex-task diff T002 --name-status
```
