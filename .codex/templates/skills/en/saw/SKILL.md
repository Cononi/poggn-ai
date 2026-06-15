---
name: saw
description: Use SAW after fixing vague requests into requirement/security contracts.
---

# saw

Apply `../_references/core-rules.md` first.

## Must

- Use only for small single-scope changes.
- Suggest MAW when risk is high or work is cross-stack.
- Use verify gates for validation, not an agent chain.
- Turn vague "build/implement/improve" requests into a requirement contract first.
- Do not start when security, authz, data, or public contract decisions are open.

## Clarification Contract

- Proceed without questions when the single change is already clear.
- If vague, ask at most 2 rounds with at most 3 questions per round.
- Ask for goal, in/out scope, acceptance criteria, editable area, and verification.
- After 2 unclear rounds, stop and report confirmed items, gaps, defaults, and safety.
- Before implementation, fix confirmed requirements, non-goals, criteria, and checks.

## Security Contract

- Find assets, entry points, and trust boundaries first.
- Review authentication and authorization separately.
- Ask security questions for auth, owner, role, tenant, API mutation, or DB query impact.
- Also check external input, file/URL/path, secret, PII, CORS/CSRF/cookie, redirect, webhook.
- Validate input by type, size, format, and authorization context.
- Do not expose token, password, secret, PII, or internal id in errors, responses, or logs.
- Block mutations without owner/role checks and queries without tenant predicates.
- Block secret exposure risk and CORS wildcard with credentials.
- If security impact exceeds SAW scope, suggest MAW or a security lane.

## Guidance Contract

- Surface material scope, architecture, data, auth, API, UX, or verification risk immediately.
- Give advice as risk, recommended approach, tradeoff, and confirmation need.
- Decide small implementation details directly; confirm behavior or contract changes.

## Procedure

- Run risk classify and context pack before work.
- Confirm the requirement and security contracts are satisfied.
- Split into follow-ups when file budget is exceeded.
- Find a test command for code changes.
- Do not mark done without TASK commit link.

## Expert Rules

- Use SAW to finish small changes quickly, not to reduce verification.
- Switch to MAW when file count, risk, or stack count grows.
- Apply strict gates to auth, DB, or deploy impact even in one TASK.
- Move scope creep to follow-up without delaying current done.
- Do not mark done without a commit link.
- Classify unverifiable work by environment, missing tool, or approval need.
- Confirm risk classify result is low and small before starting.
- Suggest MAW for auth, DB, API contract, or cross-stack changes.
- Do not start implementation without acceptance criteria.
- Prefer fail-closed security defaults and confirm public behavior changes.

## Expert Checks

- Check auth, DB, and API changes strictly even when small.
- Check whether budget overflow was ignored.
- Check whether staged quality and security gates ran.
- Check whether implementation guessed requirements instead of using criteria.
- Reject security review that cannot explain an exploitable path in one line.

## Failure Modes

- Small change skips quality or security gate.
- One-file edit hides cross-stack contract change.
- Test failure is called unrelated without evidence.
- TASK is not split after budget overflow.
- File count, test scope, or token budget is exceeded without splitting.
- Vague "build/implement/improve" request is implemented without criteria.
- Authn is mistaken for authz, or owner/tenant checks rely on client input.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Change is too broad for SAW.
- No safe verification path for code changes.
- TASK cannot be linked to the commit.
- Public contract, authz, tenant isolation, secret handling, or validation is open.

## Verify

- risk classify.
- context pack.
- verify and quality gates.
- If security impact exists, record a negative auth test or exploit scenario.

## Evidence

- Risk classify and context pack results exist.
- Confirmed requirements, non-goals, acceptance criteria, and verification plan exist.
- Staged diff stays inside one TASK scope.
- Commit hash links to verify, quality, and security results.
- Code changes have at least one test or explicit verification substitute.
- Security impact records assets, entry points, trust boundaries, authz, and validation.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
