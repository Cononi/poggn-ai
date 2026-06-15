---
name: frontend-typescript
description: Use for React TS/TSX, typed props, DTOs, and client boundaries.
---

# frontend-typescript

Apply `../_references/core-rules.md` first.

## Must

- Use `.tsx` for UI and `.ts` for logic, clients, and models.
- Type props, DTOs, API responses, and error shapes explicitly.
- Guard or parse unknown input before using it.

## Procedure

- Model nullable and optional fields in UI state.
- Encapsulate status, error, and body parsing in typed clients.
- Avoid leaking domain persistence types into component props.
- Do not relax tsconfig strictness without approval.

## Expert Rules

- Make types express runtime contracts, not only compiler satisfaction.
- Convert unknown API response through guard or parser to UI model.
- Split DTO, form state, and view model when nullable meanings differ.
- Use discriminated unions and exhaustive checks for UI transitions.
- Encapsulate status, retry, error body, and cancellation in typed clients.
- Treat any avoidance as a way to avoid hidden errors, not as ceremony.
- Separate API DTO and ViewModel, including date, money, and enum mapping.
- Forbid `as` assertions at external input boundaries before parsing.

## Expert Checks

- Check whether `any` or `as any` hides a real type error.
- Check API types against the actual contract.
- Check event handler and form value types.

## Failure Modes

- as any hides backend contract drift.
- One optional field represents both loading and missing data.
- Component props move directly with API DTO changes.
- Event target values are handled with implicit any.
- Generated types are edited directly.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Unknown API data is trusted without validation.
- Type errors are silenced instead of fixed.
- Client contract and UI assumptions disagree.

## Verify

- typecheck.
- lint.
- targeted component/client tests.

## Evidence

- typecheck passes with strict settings.
- API boundary has guard, parser, or typed client.
- UI state union covers empty, loading, error, and success.
- Error types separate transport, validation, auth, and unknown.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
