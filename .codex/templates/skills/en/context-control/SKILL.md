---
name: context-control
description: Use to keep repo reading narrow and context relevant.
---

# context-control

Apply `../_references/core-rules.md` first.

## Must

- Run context pack at task start and after resume.
- Use `rg` and name-status to narrow candidate files.
- Do not skip required contract files to save tokens.

## Procedure

- Check current TASK, changed files, and git status first.
- Read full diffs only for gate failures or explicit requests.
- Pass only required files and expected output to subagents.
- Read large docs by heading or search hit.

## Expert Rules

- Read the context needed for decisions, not the maximum context.
- Rank current files, git diff, and state pack above conversation memory.
- Open sensitive files only with purpose and usage bounds.
- Give subagents source artifacts and done contract, not conclusions.
- Narrow large files by symbol, heading, or search hit.
- Do not skip contract files to save tokens.
- Do not rely on context pack after files change until rerun.
- Separate user and agent ownership by diff hunk when mixed.

## Expert Checks

- Check that old conversation memory did not outrank current files.
- Check that the whole repo was not read without need.
- Check that sensitive files were not opened unnecessarily.

## Failure Modes

- Whole repo is read while actual modified files are missed.
- Old TASKS output outranks JSONL or state.
- Subagent prompt is polluted with unnecessary history.
- Potential secret file is opened without reason.
- Only conversation memory supports the inference; current files are unchecked.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Required contract or config cannot be read.
- Context pack contradicts git status.
- Task scope is too ambiguous to choose files safely.

## Verify

- context pack.
- targeted file list.
- git status.

## Evidence

- Context pack, rg hits, and read files are listed.
- Unread relevant files and reasons are explained.
- Subagent input is scope-limited.
- If sensitive files were opened, TASK relevance and use bounds are stated.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
