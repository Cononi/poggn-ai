# Shortcut commands

$codex-* commands are handled by the UserPromptSubmit hook.

They are not sent to the model, so state checks and automation use fewer tokens.

## SAW

SAW is the low-token single-task mode.

```text
$codex-saw suggest --text "fix dto mapping"
$codex-saw init --title dto-fix --branch hotfix/dto-fix --text "fix dto"
$codex-saw prompt
$codex-saw gate
$codex-task commit T001 --message "fix dto mapping"
```

Create follow-up TASKs only when needed.

```text
$codex-saw followup --kind test --title "missing regression test"
$codex-saw followup --kind refactor --title "duplicate cleanup"
$codex-saw followup --kind security --title "auth rule check"
```

## MAW

```text
$codex-work-items apply --text "shop order payment" --agents backend,test,qa
$codex-lanes prepare
$codex-lanes csv
$codex-lanes prompt
```

## State and trace

```text
$codex-state summary --for-ai
$codex-task trace --for-ai
$codex-task files T001
$codex-task diff T001 --name-status
```

## Quality and security

```text
$codex-quality gate --for-ai
$codex-quality frontend --for-ai
$codex-refactor analyze --for-ai
$codex-security gate
```

## Language and wiki

```text
$codex-language ko
$codex-language en
$codex-wiki build
```

## MAW pipeline

```text
$codex-pipeline ready --for-ai
$codex-pipeline prepare
$codex-pipeline csv --ready
$codex-pipeline prompt
```


## capability

```text
$codex-capabilities inspect --text "request" --agents "name" --skills "name"
```
