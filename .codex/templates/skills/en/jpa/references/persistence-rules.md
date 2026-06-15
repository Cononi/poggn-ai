# JPA Persistence Rules

## Must

- Identify every lazy association touched by DTO mapping.
- Fix fetch plans for list/detail responses with EntityGraph, fetch join,
  projection, or DTO query.
- Keep aggregate mutation inside one service transaction.
- Check stock, balance, ownership, and status invariants in the write transaction.
- Consider optimistic or explicit locking when lost updates matter.

## Never

- Do not hide lazy loading or N+1 issues with OSIV.
- Do not return entities directly from REST APIs.
- Do not use cascade remove across aggregate boundaries by default.
- Do not create update/delete queries without owner scope.

## Blocker

N+1 risk, missing transaction, entity response, or missing owner scope blocks done.
