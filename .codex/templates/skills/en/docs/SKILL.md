---
name: docs
description: Use for README, API docs, release notes, and operations docs.
---

# docs

Apply `../_references/core-rules.md` first.

## Must

- Document only current code and verified behavior.
- Follow current language policy and line-length limits.
- Do not translate commands, API paths, or code identifiers.

## Procedure

- Include auth, request, response, and error shape for API docs.
- Include rollback, migration, and secret cautions for runbooks.
- Use the repo's real package manager and scripts in examples.
- Avoid unverified performance claims and success language.

## Expert Rules

- Document verified current behavior, not desired behavior.
- Runbooks must say who rolls back what when failure happens.
- API docs must emphasize auth, validation, errors, and pagination.
- Examples must use real repo commands and package managers.
- Translation must preserve technical meaning and command reproducibility.
- Release notes must separate user impact, migration, and risk.
- Mark unverified code, config, or script claims as unverified or omit them.
- Include rollback trigger and recovery metrics in runbooks.

## Expert Checks

- Check that docs do not conflict with code.
- Check that examples do not look like real secrets.
- Check that TODO text has a linked follow-up.

## Failure Modes

- Docs promise features code does not implement.
- TODO remains without follow-up ownership.
- Example secrets look like real credentials.
- Ops docs explain deploy but omit rollback.
- Docs-only changes imply behavior changes.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Documentation would describe behavior not implemented.
- Security-sensitive guidance is missing for an ops change.
- Language render would overwrite the wrong locale.

## Verify

- docs diff.
- link/path check.
- language status.

## Evidence

- Documented commands and paths exist in repo.
- Docs diff matches changed code or API.
- Language policy and line length were checked.
- API docs separate auth, validation, and ownership failure responses.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
