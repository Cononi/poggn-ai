---
name: jpa
description: Use for JPA entities, repositories, queries, transactions, and N+1 risk.
---

# jpa

Apply `../_references/core-rules.md` first.

## Must

- Fix transaction, fetch-plan, and ownership rules first.
- Define entity lifecycle and aggregate boundary before mapping.
- Find every lazy access path used by DTO mapping.

## Procedure

- Design pagination and fetch plan together for list endpoints.
- Check collection fetch joins for duplicates and pagination skew.
- Validate invariants and ownership inside write transactions.
- Handle persistence-context sync after bulk update or delete.

## Expert Rules

- Design fetch plans per endpoint response model.
- Put transactions around service use-case invariants.
- Verify owner scope in both query predicate and domain check.
- Review collection fetch joins for duplicates and memory before pagination.
- Make DTO mapping work with OSIV off.
- Handle stale persistence context after bulk queries.
- Check blocker rules before collection fetch join in pagination APIs.
- Do not base equals/hashCode on lazy associations or mutable fields.

## Expert Checks

- Check whether entities are returned directly by REST APIs.
- Check whether OSIV hides N+1 or lazy-loading errors.
- Check whether repository methods reveal use-case intent.

## Failure Modes

- Multiple entities mutate without @Transactional.
- Controller or serializer triggers lazy loading.
- Repository method hides business intent.
- Delete or update query lacks tenant or owner predicate.
- cascade or orphanRemoval lacks aggregate ownership rationale.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- N+1 risk is left unaddressed.
- Multi-step write lacks a transaction boundary.
- Update or delete query lacks owner scope.

## Verify

- JPA integration test.
- SQL/fetch-plan review.
- service transaction test.

## Evidence

- SQL log or query count checks N+1 risk.
- Service integration test covers transaction and ownership.
- List API pagination and fetch-plan rationale exist.
- Concurrency write protection covers lock, unique constraint, or retry.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
