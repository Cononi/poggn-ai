---
name: language-policy
description: Use for document language, ko/en rendering, and line limits.
---

# language-policy

Apply `../_references/core-rules.md` first.

## Must

- Check current language status first.
- Make docs and skill bodies follow the active language.
- Do not translate commands, API paths, or code identifiers.

## Procedure

- Update template sources and rendered output together for ko/en.
- Validate SKILL.md line count and frontmatter after render.
- Measure line limits by actual character count.
- Test render scripts in an isolated copy before touching live output.

## Expert Rules

- Treat language switching as source/render synchronization.
- Do not translate technical identifiers; translate explanatory text.
- Keep ko/en templates equally strong in meaning and constraints.
- Test render scripts in an isolated copy first.
- Measure line length in markdown source and consider table width.
- Allow mixed language only for user input, proper names, or identifiers.
- Validate 100-character limit on rendered final files.
- Do not translate commands, paths, APIs, env vars, or class names.

## Expert Checks

- Check whether translation weakened technical meaning.
- Check whether mixed language has a valid reason.
- Check whether product code and language render changes are mixed.

## Failure Modes

- Korean is strong while English template becomes generic.
- Rendered SKILL.md differs from its template source.
- Translated command options or paths break execution.
- Language switch overwrites unrelated docs.
- ko/en meaning or strength diverges.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Render script would overwrite the wrong language.
- Source template and rendered skill disagree.
- Technical terms become ambiguous after translation.

## Verify

- language status.
- isolated render test.
- line-count check.

## Evidence

- Current language status and render target are recorded.
- Isolated ko/en render test passes.
- Line count and long-line checks pass.
- Blocker, must, and verify strength remain after translation.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
