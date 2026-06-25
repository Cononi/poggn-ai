---
name: pogo-codex-edit
description: `$pogo-codex-edit`와 `$pogo-settings codex-edit` 명령으로 Codex 내부 파일 수정 허용을 on/off/toggle/status로 관리한다.
---

# Pogo Codex Edit

## 목적

`Pogo Codex Edit`는 `.codex/**`와 `AGENTS.md`에 대한 자동 보호를 제어한다.
`off`일 때는 해당 경로의 수정 요청이 hook에서 `decision: block`으로 차단된다.

## 사용법

```text
$pogo-codex-edit
$pogo-codex-edit status
$pogo-codex-edit on|off|toggle
$pogo-settings codex-edit status
$pogo-settings codex-edit on|off|toggle
```

## 상태 규칙

- `status`는 현재 설정을 출력한다.
- `toggle`은 현재 값의 반대값으로 변경한다.
- `off`는 `.codex/**`와 `AGENTS.md` 쓰기/변경 작업을 막는다.
