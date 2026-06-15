---
name: frontend-component-architecture
description: Use to split frontend UI into reusable components, hooks, and clients.
---

# frontend-component-architecture

Apply `../_references/core-rules.md` first.

## Must

- Keep pages limited to route, data boundary, and composition.
- Move state to hooks and API access to typed clients or services.
- Design loading, error, empty, and disabled states.

## Procedure

- Choose primitive, compound, and feature component layers.
- Use variant, size, tone, and slots for intentional differences.
- Treat forms, tables, filters, and toolbars as reuse candidates.
- Verify labels, roles, focus order, and keyboard paths.

## Expert Rules

- Split components by state, IO, and domain responsibility, not appearance.
- Keep pages as route composition; move decisions to hooks or services.
- Compound components must include keyboard, focus, and aria contracts.
- Expose variants as meaningful APIs, not className branches.
- Design table, form, and filter states together.
- Extract reuse on the third repetition without losing domain meaning.
- Validate modal and drawer focus trap, escape, inert, and back navigation.
- Define URL state, pagination, and reset ownership for table/filter/search.

## Expert Checks

- Check whether a component exceeds roughly 160 lines.
- Check whether the same JSX pattern appears three times.
- Check responsive overflow and text wrapping.

## Failure Modes

- Page owns data fetch, mutation, rendering, and validation.
- Shared component depends on feature DTOs.
- Long text breaks responsive overflow.
- Icon button lacks accessible name or tooltip.
- Arbitrary colors or spacing bypass design tokens.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Component mixes data access, layout, and business rules.
- Expected UI state is missing.
- Accessibility name or keyboard path is absent.

## Verify

- component tests.
- typecheck.
- responsive screenshot or manual check.

## Evidence

- Component tree and state ownership are explainable.
- Loading, error, empty, and disabled states exist.
- Typecheck and responsive check pass.
- Shared promotion has at least two uses and stable props API.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
