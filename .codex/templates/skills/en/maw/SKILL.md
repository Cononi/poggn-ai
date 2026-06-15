---
name: maw
description: Run MAW with subagents after fixing vague requests into secure lane contracts.
---

# maw

Apply `../_references/core-rules.md` first.

## Must

- Treat ready lanes as real subagent work, not main-thread notes.
- Do not implement before checking the ready queue.
- Run implementation lanes through actual subagent threads.
- Turn vague "build/implement/improve" requests into requirement, security, and lane contracts.
- Do not spawn when security, authz, data, public contract, or file ownership is open.

## Clarification Contract

- Ask at most 3 rounds with at most 3 questions per round.
- Round 1 confirms user goal, core scenario, and expected result.
- Round 2 confirms in/out scope, acceptance criteria, editable area, and verification.
- Round 3 fixes lane split, owner files, forbidden files, public contract, and security.
- After 3 unclear rounds, stop and report confirmed items, gaps, defaults, and safety.
- Before spawn, fix confirmed requirements, non-goals, criteria, lane contract, and checks.

## Security Contract

- Find assets, entry points, and trust boundaries first.
- Review authentication and authorization separately.
- Put auth, owner, role, tenant, API mutation, and DB query impact in the security contract.
- Also check external input, file/URL/path, secret, PII, CORS/CSRF/cookie.
- Put redirect or webhook impact into a security lane or security gate.
- Each implementation lane names input validation, output encoding, error/log exposure,
  and owner/tenant predicate responsibility.
- Block mutations without owner/role checks and queries without tenant predicates.
- Block secret exposure risk and CORS wildcard with credentials.
- Security agents record an exploit path, negative authz test, or explicit substitute.

## Guidance Contract

- Surface material scope, architecture, data, auth, API, UX, or verification risk immediately.
- Give advice as risk, recommended approach, tradeoff, and confirmation need.
- Let lane owners decide small details; main confirms behavior or contract changes.

## Token Contract

- Do not send full TASKS.md, full conversation, or full ready JSON to subagents.
- Use `$codex-pipeline ready --for-ai` only for a sample and hidden count.
- Use `$codex-pipeline csv --ready` as the full spawn table.
- Subagent prompts include lane id, purpose, acceptance, owner files, and forbidden files.
- Summarize large logs and diffs to failing command, cause lines, and relevant files.

## Procedure

- Confirm the requirement and security contracts are satisfied.
- Use `$codex-pipeline ready/csv/prompt` as spawn input.
- Give each subagent task, lane, files, skills, and done contract.
- Process downstream events after commit links are recorded.
- Close completed threads after integrating their results.

## Expert Rules

- Treat MAW as an actual subagent thread contract, not a plan document.
- Keep main as coordinator; it must not implement ready lanes directly.
- Implementation agents implement only; QA/security/refactor agents judge later.
- Create downstream lanes only after completion commit events.
- Give each lane owner files, forbidden files, done contract, and verification.
- Allow done only after commit link and aligned TASK/thread state.
- Start MAW only when the ready queue has a real implementation lane.
- Put file scope, forbidden scope, done contract, and checks in each prompt.
- Put the compact row contract in prompts instead of full TASKS.md.
- Do not spawn a ready lane without acceptance criteria and lane contract.
- Prefer fail-closed security defaults and confirm public behavior changes.

## Expert Checks

- Check whether `/agent` still shows only main.
- Check whether the main thread implemented lane work itself.
- Check whether downstream lanes were created but not spawned.
- Check whether lanes were split from guessed requirements instead of criteria.
- Reject security review that cannot explain an exploitable path in one line.

## Failure Modes

- /agent shows only main while MAW is reported complete.
- Main implements before checking the ready queue.
- Implementation agent marks its own change as QA pass.
- Completed worker stays open and consumes pool capacity.
- Downstream event runs after lane completion without a commit link.
- Vague "build/implement/improve" request is split into lanes without criteria.
- Authn is mistaken for authz, or owner/tenant checks rely on client input.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- No real subagent thread for a ready implementation lane.
- Lane has no file ownership or done contract.
- Downstream required gate is skipped.
- Public contract, authz, tenant isolation, secret handling, validation, or owner files are open.

## Verify

- agent thread list.
- pipeline ready output.
- downstream gate reports.
- If security impact exists, run security gate and record a negative auth test or exploit path.

## Evidence

- Ready queue, prompt, and spawned agent id are recorded.
- Confirmed requirements, non-goals, acceptance criteria, lane contract, and checks exist.
- Each subagent final report and changed files are integrated.
- Commit link and downstream event result are reported.
- Record spawn evidence with /agent thread id and lane id.
- Security impact records assets, entry points, trust boundaries, authz, and validation.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
