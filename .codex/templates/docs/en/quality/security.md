# Security

Run security checks at the end.

```text
$codex-security gate
$codex-quality gate --for-ai
```

Never commit secrets, tokens, passwords, or private keys.
Do not rely on frontend-only authorization. Validate user input.
