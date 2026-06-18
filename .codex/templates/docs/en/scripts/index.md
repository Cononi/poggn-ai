# Script reference

Python files under .codex/script are token-saving execution units.

Scripts compute state so AI does not read and rewrite long documents.

## Core scripts

```text
codex_state.py       workflow, TASK, VERSION state
codex_task_git.py    TASK to commit links, diff, revert
codex_lanes.py       MAW lanes and worktrees
codex_waves.py       split MAW lanes into execution waves
codex_work_items.py  split requests into feature TASKs
codex_design_gate.py classify product, platform, framework, and stack contracts
codex_saw.py         SAW micro workflow
codex_verify.py      minimal verification before TASK completion
codex_test_runner.py no-dependency runner for trusted .codex tests
codex_quality.py     code quality, frontend TSX, duplicate checks
codex_security.py    secret, token, private key checks
codex_refactor.py    refactor need analysis
codex_wiki.py        build docs/index.html
codex_language.py    render ko/en docs and skills
codex_shortcuts.py   run $codex-* shortcuts
```

## codex_waves.py

Large MAW work is split into waves instead of being blocked by total size.

```text
$codex-waves assign
$codex-waves plan
$codex-waves next
$codex-waves prompt --wave W002
```

Prepare and run one wave only.

```text
$codex-lanes prepare --wave W002
$codex-lanes csv --wave W002
$codex-lanes prompt --wave W002
```

## codex_verify.py

SAW does not skip verification.

It only reduces the verification scope.

```text
$codex-verify gate --for-ai
$codex-verify gate --staged --for-ai
```

The order is:

```text
budget gate
quality gate
security gate
changed-code test command
```

Docs-only changes can skip tests.

Code changes require a test command. The default verification includes both
modified files and new untracked files. Internal `.codex` Python changes run the
trusted no-dependency test runner automatically.

Commands can be configured in `.codex/state/verify.json`.

```json
{
  "commands": ["npm run test", "npm run typecheck"]
}
```

If no command is configured, package.json, pytest, Gradle, and Maven are detected.

If no command is found, the gate fails.

`codex_test_runner.py` is only for trusted `.codex/tests/test_*.py` files.
Do not use it to execute arbitrary test files from an external source.

## risk, context, budget

These commands are the core token-saving loop.

```text
$codex-risk classify --text "request" --for-ai
$codex-context pack --for-ai
$codex-budget status
```

See scripts/risk-context-budget.md for details.

## Commit link

TASK commit runs verification again.

```text
$codex-task commit T001 --message "fix dto"
```

TASK is marked done only after verification passes.

## context and doctor

```text
$codex-context pack --for-ai
$codex-context pack --staged --for-ai
$codex-doctor --deep --for-ai
```

context compresses workflow, next TASK, and changed files.

doctor checks git, hooks, docs, Python syntax, and document line length.
## codex_pipeline.py

Computes ready lanes across implement, test, QA, refactor, and security.

```text
$codex-pipeline status --for-ai
$codex-pipeline ready --for-ai
$codex-pipeline prepare
$codex-pipeline csv --ready
$codex-pipeline prompt
```

```text
$codex-extend check agent --name NAME --purpose "PURPOSE"
$codex-extend create skill --name NAME --purpose "PURPOSE" --approve
```
