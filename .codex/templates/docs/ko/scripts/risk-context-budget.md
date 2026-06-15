# risk, context, budget

이 문서는 토큰 절약과 안전한 workflow 선택을 설명합니다.

## 원칙

AI가 전체 저장소를 먼저 읽지 않습니다.
먼저 script가 위험도와 필요한 context를 짧게 계산합니다.

```text
$codex-risk classify --text "요청" --for-ai
$codex-context pack --for-ai
$codex-budget status
```

## $codex-budget

SAW budget은 작은 패치 상한입니다.

MAW budget은 전체 epic 상한이 아닙니다.

MAW에서는 lane, wave, PR/MR 단위로 예산을 적용합니다.

```text
$codex-budget suggest --text "order payment 구현" --for-ai
$codex-budget gate --staged --mode maw --for-ai
$codex-waves plan
```

## wave 실행

대형 작업은 wave로 나눕니다.

```text
$codex-waves assign
$codex-waves next
$codex-lanes list --wave W001
$codex-lanes csv --wave W001
$codex-lanes prompt --wave W001
```

W001을 검증하고 병합한 뒤 W002로 넘어갑니다.

## 권장 루프

SAW는 아래 순서로 사용합니다.

```text
$codex-risk classify --text "요청" --for-ai
$codex-saw init ...
$codex-context pack --for-ai
작은 수정
$codex-verify gate --staged --mode saw --for-ai
$codex-task commit T001 --message "message"
```

MAW는 아래 순서로 사용합니다.

```text
$codex-risk classify --text "요청" --for-ai
$codex-state init --workflow maw ...
$codex-work-items apply ...
$codex-waves plan
$codex-lanes csv --wave W001
```
