# Spring Boot Backend Rules

## Must

- Keep controllers limited to HTTP shape, validation, principal, and mapping.
- Keep transactions, business rules, and state transitions in services.
- Keep repositories focused on persistence access, not business branching.
- Use request/response DTOs and stable error shapes for REST APIs.
- Separate identity authentication from ownership or role authorization.

## Never

- Do not log or return passwords, tokens, secrets, or sensitive exceptions.
- Do not use controller transactions to hide lazy loading problems.
- Do not trust a request body userId over the authenticated owner.

## Blocker

Unauthorized mutation, missing service transaction, or entity response blocks done.
