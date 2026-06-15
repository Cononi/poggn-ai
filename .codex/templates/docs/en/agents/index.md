# Agents

- architecture: contracts and boundaries
- backend: server APIs and domain logic
- frontend: UI, components, and client state
- database: schema and migrations
- test: unit and integration tests
- qa: acceptance and quality gates
- security: auth, secrets, and vulnerabilities
- refactor: behavior-preserving cleanup
- devops: CI/CD and deployment
- git: commit, diff, rollback, PR/MR
- docs: README, wiki, release notes
- integration: external APIs and events
- performance: latency, cache, slow queries
## /agent and $codex-agents

/agent switches or inspects active subagent threads.
It may be empty before a subagent is spawned.

```text
$codex-agents list
$codex-agents check
```

The same agent type can run in many lanes.

```text
L002 backend Order REST API
L003 backend Payment REST API
```
