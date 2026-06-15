---
name: refactor-clean-code
description: Use for behavior-preserving refactors and responsibility splits.
---

# refactor-clean-code

Apply `../_references/core-rules.md` first.

## Must

- State the refactor goal and behavior to preserve first.
- Do not change public API, DB schema, or error contract without approval.
- Finish only with evidence that behavior was preserved.

## Procedure

- Add characterization tests when coverage is absent.
- Split long functions by decision, IO, and mapping concerns.
- Remove cycles and strengthen domain boundaries.
- Break large diffs into staged commits or follow-ups.

## Expert Rules

- Make existing meaning clearer without adding features.
- Define behavior preservation with tests, snapshots, contracts, or diffs first.
- Justify abstraction by separating reasons to change.
- Rename only when dependency direction or responsibility becomes clearer.
- Check transaction, cache, lazy loading, and concurrency semantics.
- Use characterization tests and staged commits for large refactors.
- Write public behavior invariants before and after refactor by file or test.
- Extract shared helpers only with two uses or clear boundary benefit.

## Expert Checks

- Check whether only names changed while structure stayed weak.
- Check whether performance or transaction meaning changed.
- Check whether abstraction removed real duplication.

## Failure Modes

- Public API or error shape changes silently.
- Common util hides domain rules and increases coupling.
- Large structural change has no tests.
- Readability and correctness are lost under performance claims.
- Transaction, async timing, memoization, or cache key meaning changes silently.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Behavior change appears in an unapproved refactor.
- No test or evidence preserves existing behavior.
- New abstraction increases coupling or hides domain rules.

## Verify

- existing tests.
- characterization tests.
- targeted diff review.

## Evidence

- Preserved behavior and verification command are recorded.
- Before/after responsibility boundary is explained.
- Behavior changes are split into separate TASKs.
- Rename, move, and extraction are verified with behavior diff.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
