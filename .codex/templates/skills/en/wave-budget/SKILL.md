---
name: wave-budget
description: Use to split large MAW work into waves and verification order.
---

# wave-budget

Apply `../_references/core-rules.md` first.

## Must

- Split epics into contract, schema, backend, frontend, and verification.
- Keep each wave within reviewable file and diff size.
- Finish schema and API contract before implementation waves.

## Procedure

- Group high-integration-risk files in the same wave.
- Always place a verification wave after implementation waves.
- Run merge and quality gates between waves.
- Split large lanes into feature slices.

## Expert Rules

- Treat a wave as a verifiable release slice.
- Run contract and schema waves before implementation waves.
- Give each wave budget, owner, merge order, and rollback rule.
- Reevaluate start conditions after a failed wave.
- Split by risk slice when safer than feature slice.
- Check integration diff and quality gate between waves.
- Set wave limits by file count, diff lines, and ownership count.
- Enter next wave only after commit, quality gate, and no blockers.

## Expert Checks

- Check whether parallelism outranks mergeability.
- Check whether the next wave started after a failed wave.
- Check TASK and commit links for every wave.

## Failure Modes

- All implementation is one wave and verification is last.
- Schema and frontend-dependent changes conflict in one wave.
- Next wave commits after prior wave failure.
- TASK and commit links are not retained per wave.
- Dependent wave continues after contract or schema wave failure.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Wave is too large to review.
- Failed wave has unresolved downstream work.
- Contract or verification wave is missing.

## Verify

- wave plan.
- between-wave gate.
- TASK/commit trace.

## Evidence

- Wave plan lists dependencies and owners.
- Each wave commit passes budget gate.
- Merge and verify results are reported after every wave.
- After wave failure choose scope cut, split, or rollback.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
