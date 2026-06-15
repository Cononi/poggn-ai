---
name: quality-gate
description: Use to inspect quality, duplication, size, ownership, and security smells.
---

# quality-gate

Apply `../_references/core-rules.md` first.

## Must

- Set large-file, duplication, ownership, and security-smell criteria first.
- Run `$codex-quality gate --for-ai`.
- Add purpose/contract doc comments to public or exported symbols.
- Classify each quality failure as blocker or follow-up.

## Procedure

- Classify changed files as feature, test, docs, or config.
- Inspect large files, duplication, and mixed responsibility first.
- For backend, check transactions, ownership, and N+1 risk.
- For frontend, check TSX size, component split, and typed clients.
- Comments explain why, contracts, and constraints, not repeated code mechanics.

## Expert Rules

- Treat quality gate as maintainability-risk control, not aesthetics.
- Judge large files by responsibilities and change reason, not only lines.
- Treat repeated business rules as more dangerous than repeated text.
- Allow false positives only with evidence and owner.
- Route security smells to security-gate.
- Separate current-task blockers from follow-up quality debt.
- Decide whether public API changes and internal refactor must be split.
- Check new helpers against existing utils, framework, and domain services.
- Treat missing doc comments as blockers under strict quality verification.

## Expert Checks

- Check whether business rules are hidden in controllers or UI.
- Record evidence before excluding a false positive.
- Check that public/exported symbol docs explain purpose and contract.

## Failure Modes

- Business rules live in controllers, UI, or script glue.
- Assertions are weakened to make tests pass.
- Huge diff is not split into reviewable units.
- Quality failure is reported as warning and still committed.
- Feature flag, dead code, or TODO remains in deploy path.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Quality gate fails on staged changes.
- Security smell is unresolved or untriaged.
- Mixed responsibility makes review unsafe.
- Public/exported purpose or contract doc comment is missing.

## Verify

- quality gate.
- targeted diff review.
- security-gate when needed.

## Evidence

- Quality gate output and action or exception rationale exist.
- Large, duplicate, and mixed-responsibility findings are classified.
- Residual quality risk links to TASK or follow-up.
- Generated and hand-edited files use separate quality criteria.
- Doc comment exceptions have private trivial helper or generated-file evidence.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
