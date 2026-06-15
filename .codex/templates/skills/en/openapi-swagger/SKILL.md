---
name: openapi-swagger
description: Use for OpenAPI/Swagger docs and REST contract validation.
---

# openapi-swagger

Apply `../_references/core-rules.md` first.

## Must

- Keep the spec synchronized with implementation.
- Use stable, unique operationId values.
- Declare auth scheme and security requirement per endpoint.

## Procedure

- Match required, nullable, default, and examples to validation.
- Include common error shape and status for error responses.
- Document pagination, sorting, and filtering parameters.
- Add version or migration notes for breaking changes.

## Expert Rules

- Treat OpenAPI as client generation contract, not marketing docs.
- Keep operationId stable and unique for SDK method names.
- Check endpoint overrides before relying on global security defaults.
- Use oneOf/anyOf only when generated clients can model it.
- Make examples pass validation and real error shape.
- Document replacement field and removal date for deprecations.
- Check generated clients for oneOf, allOf, enum, and date-time.
- Block required/default drift in path, query, and header parameters.

## Expert Checks

- Check for endpoints documented but not implemented.
- Check for implemented endpoints missing from the spec.
- Check generated-client compatibility.

## Failure Modes

- Spec contains endpoints with no controller.
- required or nullable disagrees with validation or TS types.
- Error response differs from exception handler output.
- Generated client misses a breaking change.
- Binary upload/download or streaming content type is unspecified.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- OpenAPI and implementation disagree on contract.
- Security requirement is missing for protected endpoint.
- Breaking contract change lacks migration note.

## Verify

- OpenAPI validation.
- contract tests.
- client generation check.

## Evidence

- Spec validation and implementation diff were checked.
- Protected endpoints declare security requirements.
- Generated client or contract test result exists.
- Error schema matches handler code, message, and fieldErrors.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
