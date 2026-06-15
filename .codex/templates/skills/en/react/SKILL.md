---
name: react
description: Use for React components, hooks, state, and typed-client UI work.
---

# react

Apply `../_references/core-rules.md` first.

## Must

- Limit each component responsibility to one clear sentence.
- Move state to hooks and API access to typed clients.
- Verify a11y labels, focus, and keyboard paths.

## Procedure

- Represent variant, size, tone, and state in props.
- Model form validation, dirty, error, and submit state.
- Give lists stable keys plus empty, loading, and error states.
- Check layout on mobile and desktop for overflow.

## Expert Rules

- Separate rendering, state, side effects, and IO boundaries.
- Make hooks explicit about browser lifecycle and domain transitions.
- Split validation, dirty, touched, and pending state in controlled forms.
- Check list key stability, virtualization need, and empty/error states.
- Give every interactive control an accessible name.
- Consider rollback and reduced motion for animation and optimistic UI.
- Use useEffect only for external synchronization, not derived state.
- Handle unmount, abort, and stale responses in async state updates.

## Expert Checks

- Check for copy-pasted JSX.
- Check that buttons and icon controls have accessible names.
- Check that animation never blocks user action.

## Failure Modes

- useEffect handles data dependency and mutation together.
- Component directly interprets API DTO and domain rules.
- Loading skeleton causes layout shift.
- Mobile toolbar or button text overflows.
- Initial value model can trigger controlled/uncontrolled warnings.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Interactive control lacks accessible name.
- UI misses loading, error, or empty state for async data.
- Component hides business logic that belongs elsewhere.

## Verify

- component tests.
- typecheck.
- responsive visual check.

## Evidence

- Component, hook, and client separation is visible in diff.
- A11y label, focus, and keyboard path were checked.
- Typecheck and key UI state checks pass.
- Focus is preserved after reorder, filter, or pagination.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
