---
name: git-automation
description: Use for git init, commits, TASK links, rollback, and PR preparation.
---

# git-automation

Apply `../_references/core-rules.md` first.

## Must

- Check git status for unrelated changes before work.
- Stage only files within the requested scope.
- Pass the quality gate before commit.
- Commit subject, body, and footer follow the current language policy.

## Procedure

- Write TASK commits with the correct lane id and message.
- Use conventional commit subject format `{type}: {title}`.
- Body records purpose, scope, acceptance criteria, and verification.
- Footer records Codex-Task, Codex-Lane, and Codex-Verification.
- Verify existing commit links by hash and TASK.
- Review diffs as stat, name-only, then targeted diff.
- Separate state commits from product commits when needed.

## Expert Rules

- Prioritize change isolation over generating changes.
- Classify user changes, generated output, and state files before staging.
- Commit messages should explain why this scope belongs together.
- Separate unrelated scopes to keep rollback possible.
- Check worktree and staged diff before merge or rebase.
- Do not bypass failed automation with manual git commands immediately.
- Check unstaged and cached name-status separately before staging.
- Keep TASK id, purpose, and verification traceable in commit messages.

## Expert Checks

- Check that unrelated files are not staged.
- Check that destructive reset or checkout was avoided.
- Check that commit message explains the intent.

## Failure Modes

- Large untracked set is added with add -A accidentally.
- User changes are mixed into your commit.
- Commit is made after a quality gate failure.
- Destructive checkout or reset loses work.
- --no-verify is used after hook failure without approval.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Unrelated staged files cannot be separated safely.
- Quality gate fails before commit.
- Commit would include user changes outside request.

## Verify

- git status.
- staged diff.
- quality gate.

## Evidence

- git status, staged name-only, and diff stat were checked.
- Commit hash and TASK link are recorded.
- Excluded unrelated files are explained.
- Generated files, lockfiles, and snapshots have inclusion rationale.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
