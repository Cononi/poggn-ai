# Security Guide

Security is not only a final review step.
`$codex-verify gate` runs budget, quality, security, and test checks together.

```text
$codex-verify gate --for-ai
$codex-security gate
$codex-quality gate --for-ai
```

Do not do these things.

- Do not write secrets, tokens, passwords, or private keys into code.
- Do not read `.env` contents or paste them into docs.
- Do not rely on frontend checks for authentication or authorization.
- Do not pass unvalidated user input into a database query or shell command.
- Do not open CORS or redirect policy broadly.
- Treat permission, payment, and deployment changes as high risk.

## Trust Boundaries

- `$codex-*` shortcuts execute only allow-listed scripts under `.codex/script`.
- Edit `.codex` only while `$codex-edit-mode on` is active.
- `codex_test_runner.py` is for trusted `.codex/tests/test_*.py` files only.
- Review external test files, fixtures, and generated artifacts before running them.
- Language rendering rewrites `docs/` from templates, so update templates too.

## Done Criteria

Do not complete a TASK when a security issue is present.
A security or refactor agent should handle the fix in a separate TASK.
Report the security check result and residual risk in the final summary.
