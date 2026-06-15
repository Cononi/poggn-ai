# Frontend Component Guide

React frontend code defaults to TypeScript and TSX.

New UI files with JSX must use `.tsx`.

Types, hooks, clients, and utilities without JSX use `.ts`.

New `.js` or `.jsx` files are allowed only for explicit legacy work.

## Component layers

Reuse components by nature, not by name.

Primitives own minimal UI meaning and accessibility.

Compounds group parts that are used together.

Features compose domain screen fragments.

Pages and screens only handle route composition.

## Reuse criteria

Merge similar visual intent with variant and tone props.

Absorb size differences with a size prop.

Absorb state differences with state, disabled, and loading props.

Absorb structure differences with slots, children, or render props.

Absorb behavior differences with callbacks such as onChange and onSubmit.

## Repeated extraction targets

Button, Input, Modal, and Table are not the only targets.

Card, FormField, Select, Checkbox, and Radio are also targets.

Tabs, Accordion, Drawer, Popover, and Tooltip are also targets.

Toolbar, FilterBar, SearchBox, and Pagination are also targets.

EmptyState, ErrorState, and LoadingState are also targets.

DataTable, DetailPanel, and StatusBadge are also targets.

Extract after the same JSX pattern appears three times.

## Forbidden patterns

Do not put API, state, style, and validation in one page.

Do not repeat fetch or axios calls inside components.

Do not create many similar buttons with different names only.

Do not hide props behind any, as any, or wide object types.

Components over 160 lines are refactor candidates.

## Recommended structure

```text
src/
  app/ or pages/
  features/order/
    components/
    hooks/
    api/
    types.ts
  shared/ui/
    Button.tsx
    Modal.tsx
    DataTable.tsx
  shared/lib/
```

Run `$codex-quality frontend --for-ai` to inspect frontend quality.
