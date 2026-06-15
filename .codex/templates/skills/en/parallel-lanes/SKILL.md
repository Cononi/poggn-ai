---
name: parallel-lanes
description: Use to define MAW lane, wave, dependency graph, and parallelism.
---

# parallel-lanes

Apply `../_references/core-rules.md` first.

## Must

- Draw the dependency graph before splitting lanes.
- Assign each shared file to one implementation lane only.
- Run contract and schema lanes before feature implementation.

## Procedure

- Parallelize only independent features.
- Keep waves small enough to review.
- Put conflict-prone files into an integration lane.
- Run downstream verification after upstream commits.

## Expert Rules

- Parallelism is independently mergeable ownership, not headcount.
- Put shared contracts before all feature lanes.
- Use integration lanes when files may overlap.
- Keep waves reviewable, testable, and rollbackable.
- Separate code dependency from verification dependency in the graph.
- Write done contracts so lanes do not depend on each other's output.
- Build an ownership matrix before parallelizing; merge overlaps into one lane.
- Default dependency order is schema, client, implementation, tests, QA.

## Expert Checks

- Check whether multiple lanes own the same file.
- Check whether agent count outranks ownership clarity.
- Check whether a verification wave is missing.

## Failure Modes

- Artificial lanes are created to match agent count.
- Schema and API contract change inside feature lanes simultaneously.
- Multiple lanes own conflict-prone files.
- Implementation lanes finish without verification lane.
- Shared types, config, or generated artifacts are edited by multiple lanes.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Lane dependency is cyclic or missing.
- Parallel lanes would edit the same files.
- Contract lane is skipped before implementation.

## Verify

- lane graph.
- ownership map.
- wave gate results.

## Evidence

- Lane graph and owner file map exist.
- Wave budget and gate results exist.
- Files needing integration lane are marked.
- Integration verification and conflict review run after parallel lanes.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
