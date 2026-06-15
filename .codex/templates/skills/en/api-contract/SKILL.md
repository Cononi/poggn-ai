---
name: api-contract
description: Use to lock endpoint, DTO, error, auth, and ownership contracts.
---

# api-contract

Apply `../_references/core-rules.md` first.

## Must

- Fix method, path, request, response, and error shape first.
- Declare auth, owner, role, and tenant rules for every endpoint.
- Keep public contracts separate from persistence entities.

## Procedure

- Reflect validation, nullable fields, and defaults in DTOs.
- Define pagination, sorting, and filtering for list APIs.
- Review idempotency and conflict behavior for mutations.
- Document migration path and client impact for breaking changes.

## Expert Rules

- Freeze contracts as testable statements before controller code.
- Keep path ids, principal, and owner query semantics aligned.
- Decide nullable by client meaning, not only DB nullable.
- Keep error codes stable for UI branching and log search.
- Define pagination mode and sort stability together.
- Describe duplicate requests, races, and retry results for mutations.
- Fix retry and idempotency-key policy for state-changing APIs.
- Decide 401, 403, and 404 with owner hiding policy.

## Expert Checks

- Check that stack traces and internal enums never reach responses.
- Check that client-owned fields have compatibility tests.
- Check implementation and OpenAPI for schema drift.

## Failure Modes

- Entity fields become the response contract.
- 403 and 404 policy ignores owner-disclosure risk.
- Validation failure is not traceable per field.
- Client-dependent enum or string changes without documentation.
- Unknown-field handling for request DTO is not part of contract.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Entity is exposed as API contract.
- Authorization or owner rule is undefined.
- Breaking change has no migration path.

## Verify

- contract tests.
- OpenAPI diff.
- auth and validation tests.

## Evidence

- Each endpoint has authz, request, response, and error examples.
- OpenAPI or contract tests match implementation.
- Breaking-change status and migration note are recorded.
- List responses test stable ordering and cursor/page boundaries.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
