---
name: nextjs
description: Use for Next.js routes, server/client boundary, and cache policy.
---

# nextjs

Apply `../_references/core-rules.md` first.

## Must

- Define server and client component boundaries first.
- Keep `page.tsx` to route composition and data boundary.
- Keep secrets and server-only env out of the client bundle.

## Procedure

- Separate validation, authz, and mutation in server actions.
- Set cache, revalidate, and dynamic policy by data sensitivity.
- Review loading, error, and not-found boundaries by route.
- Plan optimistic form updates with rollback behavior.

## Expert Rules

- Verify server/client boundaries through the import graph.
- Separate validation, authz, mutation, and revalidation in server actions.
- State cache policy by data sensitivity and mutation frequency.
- Ensure route loading/error/not-found segments preserve user flow.
- Keep client components to interaction state, never secrets or server env.
- Make SEO metadata a route responsibility, not client-only data.
- Keep `use client` at leaf components and stop spread into page or layout.
- Review static rendering impact when using cookies, headers, or auth session.

## Expert Checks

- Check whether client-only dependencies entered server paths.
- Check whether stale-sensitive mutations have cache policy.
- Check whether metadata and SEO responsibility match the route.

## Failure Modes

- server-only module reaches the client bundle.
- Stale cache misrepresents auth or billing state after mutation.
- Form validation exists only on the client.
- Page needing dynamic rendering is frozen by static cache.
- Middleware matcher is broad enough to create redirect loops.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Secret or server-only value can reach client bundle.
- Mutation lacks validation or authorization.
- Cache policy can serve stale sensitive data.

## Verify

- build.
- typecheck.
- route/server-action tests.

## Evidence

- Build or bundle check passes.
- Server action tests cover validation and authz.
- Cache and revalidate policy is visible in code or docs.
- Mutation revalidatePath or revalidateTag path was checked.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
