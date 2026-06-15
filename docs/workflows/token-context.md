# 토큰 최적화와 컨텍스트 관리

AI가 긴 문서를 직접 읽어 판단하지 않게 합니다.

상태, 진행률, 변경 파일, commit 연결은 script가 계산합니다.

AI는 짧은 JSON 요약만 보고 다음 작업을 결정합니다.

## 기본 명령

```text
$codex-context pack --for-ai
$codex-task trace --for-ai
$codex-state summary --for-ai
```

## SAW 제한

SAW는 micro patch입니다.

기본 제한은 작은 파일 수와 작은 변경 줄 수입니다.

제한을 넘으면 MAW로 전환합니다.

## MAW wave 제한

MAW는 전체 epic이 커도 됩니다.

다만 한 lane과 한 wave는 budget 안에 들어와야 합니다.

```text
$codex-lanes csv --wave W001
$codex-verify gate --staged --mode maw --for-ai
```

## 읽기 규칙

TASKS.md 전체를 매번 읽지 않습니다.

전체 git log를 매번 읽지 않습니다.

전체 diff는 사용자가 요청하거나 gate 실패 때만 봅니다.
