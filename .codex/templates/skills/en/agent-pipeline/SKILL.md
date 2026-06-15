---
name: agent-pipeline
description: Use when routing MAW results to test, QA, refactor, and security lanes.
---

# agent-pipeline

Apply `../_references/core-rules.md` first.

## Must

- Create downstream lanes only after the upstream TASK is linked to a commit.
- Include commit, changed files, risk, and expected output in each prompt.
- Keep validation agents focused on verdicts and minimal fix advice.

## Procedure

- Inspect ready queues and lane dependencies before spawning work.
- Deduplicate downstream lanes by root_lane_id and commit.
- Record QA, refactor, and security results as pass, fail, or blocked.
- Turn failures into follow-up TASK candidates when implementation is needed.

## Expert Rules

- Treat lane creation as an execution reservation, not a note.
- Limit downstream agents to the upstream diff and commit.
- Keep QA and security verdict authority separate from implementers.
- Make event idempotency use root lane, commit, and target role.
- Convert failed lanes into follow-ups with cause, repro, and owner.
- Read blockers and unresolved risk before pass summaries.
- Require downstream input to include SHA, diffstat, owned files, and risk.
- Use the most conservative verdict when QA, refactor, and security conflict.

## Expert Checks

- Check that two downstream agents cannot edit the same file at once.
- Check that security failure cannot be overwritten by QA pass.
- Classify test_runner failure as environment, fixture, or product code.

## Failure Modes

- Lane records exist without real threads.
- Multiple downstream lanes report the same failure repeatedly.
- Test failure is recorded as QA failure without rerun evidence.
- Security blocker is buried under refactor advice.
- Security fail is offset by QA pass or test pass.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Downstream lane created but no subagent spawned.
- Validation agent modifies product code without ownership.
- Missing upstream commit link.

## Verify

- pipeline ready output.
- downstream result summaries.
- final gate after fixes.

## Evidence

- Ready queue entries match spawned thread ids.
- Each downstream report references the upstream commit hash.
- Final report summarizes pass, fail, and blocked counts.
- Failure report includes repro command and follow-up TASK candidate.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
