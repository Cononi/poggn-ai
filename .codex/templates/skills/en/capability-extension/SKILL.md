---
name: capability-extension
description: Use when a missing agent or skill may require a local capability extension.
---

# capability-extension

Apply `../_references/core-rules.md` first.

## Must

- Try strengthening an existing capability before adding a new one.
- New skills must define trigger, procedure, blocker, and verification.
- New agents must have a narrow mission and forbidden work.

## Procedure

- Run `$codex-capabilities inspect` or `$codex-extend scan` first.
- Strengthen description or references when similar capability exists.
- Record the approval reason and duplicate-check result when creating.
- Verify discovery with list or check commands after creation.

## Expert Rules

- Add capability only when it reduces repeatable failures.
- Make new skill triggers narrow and behavior-changing.
- Give new agents mission, forbidden work, and output format.
- Strengthen existing description or references when similar entries exist.
- Verify discovery, recommendation, and real usage path after extension.
- Record problem, existing options, and why they were insufficient.
- Record duplicate candidates with inspect and extend check before creation.
- Block new capability when strengthening existing one solves it.

## Expert Checks

- Check whether a one-off task is being turned into a skill.
- Check that no all-purpose agent is being created.
- Check that hook and edit-mode policy were not bypassed.

## Failure Modes

- A one-off request becomes a permanent skill.
- A general agent is created to handle every problem.
- Description is broad enough to trigger unexpectedly.
- Creation is reported done without list or check validation.
- File-specific one-off knowledge is promoted to capability.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Duplicate capability exists and was not compared.
- New capability lacks verification rules.
- Capability scope is broader than the problem.

## Verify

- extend scan.
- capability list.
- trigger recommendation check.

## Evidence

- extend scan or capability inspect result exists.
- New trigger and blocker behavior is tested.
- Reason existing capability could not be strengthened is recorded.
- New agents define ownership, input, output, and exit criteria.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
