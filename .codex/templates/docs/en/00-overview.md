# Overview

This template makes Codex safer for Git-based development automation.
The model writes code, while scripts track state, commits, diffs, and rollback data.

Core ideas:

- agent is a role.
- skill is a reusable procedure.
- lane is the real parallel work unit.
- TASK is the tracked unit linked to commits.

For a shop API, Order REST API and Payment REST API are separate lanes.
Spring Boot, JPA, and Swagger are skills used by the backend agent.

$codex-* shortcuts are handled by hooks and scripts to reduce model tokens.
