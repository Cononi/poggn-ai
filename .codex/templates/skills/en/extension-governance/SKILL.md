---
name: extension-governance
description: Use for approving, deduplicating, and governing capability changes.
---

# extension-governance

Apply `../_references/core-rules.md` first.

## Must

- Break capability requests into problem, repetition, and domain.
- Do not create skills for one-off tasks.
- Strengthen similar capabilities instead of duplicating them.

## Procedure

- Compare existing entries with `$codex-extend scan`.
- Require mission, ownership, and forbidden work for new agents.
- Require expert constraints and failure modes for new skills.
- Verify discovery and recommendation after creation.

## Expert Rules

- Treat extensions as policy changes that reduce repeated failure.
- New entries increase discovery, trigger, permission, and maintenance cost.
- Strengthen similar capabilities before creating duplicates.
- Creating without approval damages trust in the tool ecosystem.
- New skills and agents need removal criteria and ownership scope.
- Verify that recommendations route to the new or updated capability.
- Split approval basis into repetition, expertise, and existing skill gap.
- Define routing priority when triggers overlap with existing skills.

## Expert Checks

- Check whether the capability is too broad.
- Check whether create commands ran without approval.
- Check whether description triggers are specific enough.

## Failure Modes

- Ambiguous description triggers too broadly.
- New agent owns implementation, QA, and security together.
- Duplicate capability is created without scan results.
- Approval reason is a one-off request.
- --approve creation runs without approval log.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Duplicate capability is not resolved.
- Governance approval is missing where required.
- New capability can own unrelated work.

## Verify

- extend scan.
- discovery list.
- recommendation check.

## Evidence

- scan or inspect result and duplicate judgment exist.
- Trigger test exists for the new or updated capability.
- Approval scope and generated files are recorded.
- Discovery, recommendation, and duplicate scan are verified after creation.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
