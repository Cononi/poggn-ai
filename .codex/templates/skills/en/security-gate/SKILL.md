---
name: security-gate
description: Use for auth, authorization, secrets, validation, and deployment leaks.
---

# security-gate

Apply `../_references/core-rules.md` first.

## Must

- Identify assets, entry points, and trust boundaries first.
- Review authentication separately from authorization.
- Search secrets in source, logs, config, docs, and fixtures.

## Procedure

- Check user, tenant, and role ownership in data queries.
- Check input validation and output encoding.
- Set session, CSRF, CORS, and cookie flags by endpoint type.
- Review error messages and audit logs for sensitive data.

## Expert Rules

- Pass security only when the exploit path is explainable.
- Do not treat authentication as authorization.
- Verify owner and tenant in service checks and data queries.
- Search secrets in source, logs, docs, artifacts, caches, and images.
- Validate input by type, size, format, and authorization context.
- Balance audit usefulness with sensitive data minimization.
- Verify tenant isolation in query predicates, not controller conditions only.
- Check JWT/session expiration, refresh, and revocation per endpoint.

## Expert Checks

- State the exploit scenario in one clear sentence.
- Check dependency and build artifacts for secret exposure.
- Check whether auth-only was mistaken for authorization.

## Failure Modes

- IDOR endpoint checks only principal existence.
- CORS, CSRF, or cookie flags mismatch endpoint type.
- Token, password, or internal id appears in response or log.
- Dependency or generated artifact contains a secret.
- CORS wildcard is combined with credentials.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Protected resource lacks owner or tenant check.
- Secret is committed, logged, or bundled.
- User-controlled input reaches dangerous sink unvalidated.

## Verify

- security gate.
- secret scan.
- authz tests.

## Evidence

- Asset, entry point, and trust boundary are listed.
- Negative authz test or exploit scenario exists.
- Secret scan and staged security gate pass.
- SSRF, path traversal, and mass-assignment inputs were reviewed.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
