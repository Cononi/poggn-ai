---
name: agent-selection
description: Use to choose MAW/SAW agents and skills without duplicate work.
---

# agent-selection

Apply `../_references/core-rules.md` first.

## Must

- Split the request by feature, layer, risk, and artifact.
- Use agents for roles and skills for procedure.
- Reuse existing agents and skills before creating new ones.

## Procedure

- Define backend, frontend, database, devops, and docs boundaries first.
- Put contract or schema lanes before cross-stack implementation.
- Force security-gate when auth, secret, or permission changes exist.
- Separate test writing from test execution when ownership differs.

## Expert Rules

- Keep agents as responsible actors and skills as procedures.
- Do not combine implementation, test writing, execution, and approval.
- Add security or ops lanes for auth, billing, deletion, or deploy impact.
- Put contract changes before backend or frontend implementation.
- Split by merge-conflict risk before raw file count.
- Check existing descriptions before creating new agents.
- Use risk classify output to decide agent count and validation lanes.
- Run capability inspect and extend check before creating a new agent.

## Expert Checks

- Check that backend agents are not grading their own security.
- Check that test_runner is not implementing product code.
- Check that refactor lanes do not include behavior changes.

## Failure Modes

- One agent owns both implementation and final approval.
- Parallel lanes edit the same files for artificial parallelism.
- test_runner is assigned product implementation.
- New agent is created without duplicate capability review.
- Docs-only or test-only work is unnecessarily expanded into MAW.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Role owns both implementation and final approval.
- Security-impacting change has no security lane.
- Lane boundary overlaps on the same files.

## Verify

- selected agent list.
- skill trigger fit.
- lane ownership map.

## Evidence

- Each selected agent has owner, input, output, and forbidden work.
- Security impact is recorded as yes or no.
- Duplicate capability check result is recorded.
- Excluded agent candidates and reasons are recorded.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
