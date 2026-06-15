---
name: test-generation
description: Use for business logic, auth, state transition, and API contract tests.
---

# test-generation

Apply `../_references/core-rules.md` first.

## Must

- Name tests after business behavior.
- Prioritize invariants and negative paths over happy paths.
- For bug fixes, write the failing reproduction first.

## Procedure

- Separate unauthorized and forbidden cases for auth changes.
- Verify JPA mapping and fetch behavior for query code.
- Check status, validation, response, and error shape for APIs.
- Make time, random, and network deterministic at boundaries.

## Expert Rules

- Lock behavior that must not break, not implementation details.
- Prioritize negative paths for security, permission, validation, and state.
- Keep fixtures small enough to reveal business preconditions.
- Mock external boundaries, not domain rules.
- Isolate time, randomness, network, and concurrency deterministically.
- For regressions, prove the failing reproduction before green.
- Split auth tests into self, other user, unauthenticated, and insufficient role.
- Separate missing, null, blank, and format errors in API validation tests.

## Expert Checks

- Check whether mocks hide domain rules.
- Check whether fixtures are excessive or unclear.
- Check whether expectations were loosened without root cause.

## Failure Modes

- Only happy path exists, missing auth bypass and validation failures.
- Mock replaces service invariant.
- Assertions are loose enough to allow contract drift.
- Retries grow without flaky root-cause analysis.
- Migration test omits transition with existing data.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Security or ownership behavior lacks negative tests.
- Bug fix has no regression test when feasible.
- Flaky external dependency controls test outcome.

## Verify

- targeted tests.
- coverage of negative paths.
- flaky boundary review.

## Evidence

- Test names describe business behavior.
- Unauthorized and forbidden cases are separate.
- Targeted test result and reproduction status are reported.
- Persistence tests observe SQL count or lazy access failure.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
