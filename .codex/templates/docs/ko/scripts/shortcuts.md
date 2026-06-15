# shortcut 명령

$codex-* 명령은 UserPromptSubmit hook에서 처리합니다.

모델로 전달되지 않으므로 상태 조회와 자동 처리 토큰을 줄입니다.

## SAW

SAW는 초저토큰 단일 작업 모드입니다.

```text
$codex-saw suggest --text "fix dto mapping"
$codex-saw init --title dto-fix --branch hotfix/dto-fix --text "fix dto"
$codex-saw prompt
$codex-saw gate
$codex-task commit T001 --message "fix dto mapping"
```

필요할 때만 후속 TASK를 만듭니다.

```text
$codex-saw followup --kind test --title "missing regression test"
$codex-saw followup --kind refactor --title "duplicate cleanup"
$codex-saw followup --kind security --title "auth rule check"
```

## MAW

```text
$codex-work-items apply --text "shop order payment" --agents backend,test,qa
$codex-pipeline ready --for-ai
$codex-pipeline prepare
$codex-pipeline csv --ready
$codex-pipeline prompt
```

## 상태와 추적

```text
$codex-state summary --for-ai
$codex-task trace --for-ai
$codex-task files T001
$codex-task diff T001 --name-status
```

## 품질과 보안

```text
$codex-quality gate --for-ai
$codex-quality frontend --for-ai
$codex-refactor analyze --for-ai
$codex-security gate
```

## 언어와 wiki

```text
$codex-language ko
$codex-language en
$codex-wiki build
```


## capability

```text
$codex-capabilities inspect --text "요청" --agents "name" --skills "name"
```
