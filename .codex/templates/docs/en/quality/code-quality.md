# Code Quality Guide

Run the quality gate before completion commits.

The default command is `$codex-quality gate --for-ai`.

Use staged or git diff mode to inspect only changed files.

## Hard rules

Source files must stay under 200 lines.

Frontend component files should stay under 160 lines.

New React UI must use `.tsx`.

Logic and types without JSX must use `.ts`.

Do not create duplicate code or duplicate features.

Secret, token, and password traces are errors.

## Frontend rules

Pages and screens only compose.

Move state to hooks, API to typed clients, and validation to schemas.

Extract same-nature UI into primitive, compound, and feature components.

First consider variant, size, tone, state, slot, and render props.

## Refactor rules

When tests fail, fix tests before refactoring.

Do not complete a TASK while the quality gate has errors.

QA reviews warnings and decides whether to create a refactor TASK.
