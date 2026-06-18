# Customization

Use edit mode before changing .codex.

```text
$codex-edit-mode on
$codex-edit-mode off
```

You can add agents, skills, rules, docs, or thresholds.
Run checks after changes.

```text
$codex-agents check
$codex-wiki build
```

- extension-governance: agent and skill creation gates.


When docs are added or changed, update both `docs/` and
`.codex/templates/docs/ko,en`. Language switching renders `docs/` from templates.
