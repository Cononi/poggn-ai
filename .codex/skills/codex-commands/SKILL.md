---
name: codex-commands
description: $codex-* shortcut을 우선 실행하고 결과를 정확히 해석할 때 사용합니다.
---

# codex-commands

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- 상태, TASK, gate, context 조회는 shortcut을 우선합니다.
- hook block 출력은 사용자 표시 결과일 수 있음을 구분합니다.
- shortcut 실패는 command, exit, stderr와 함께 보고합니다.

## Procedure

- help나 status 명령으로 사용법을 먼저 확인합니다.
- 긴 JSONL은 summary, trace, pack 명령으로 압축합니다.
- shortcut 결과와 git status가 충돌하면 git status를 다시 확인합니다.
- 반복 실행으로 상태 파일을 불필요하게 오염시키지 않습니다.

## Expert Rules

- shortcut은 상태 원천을 바꾸는 도구인지 읽기 도구인지 구분합니다.
- for-ai 출력이 있으면 사람이 읽기 쉬운 장문 출력보다 우선합니다.
- hook block은 장애가 아니라 정책 판단으로 다룹니다.
- shortcut 실패 후 수동 수정은 원인 기록 없이는 하지 않습니다.
- 같은 명령 반복 전 입력 상태가 바뀌었는지 확인합니다.
- 명령 결과는 git status, staged diff, TASK state와 교차 확인합니다.
- shortcut 사용 전 help 또는 --for-ai 지원 여부를 확인합니다.
- shortcut 우회가 필요하면 수동 검증의 등가성을 남깁니다.

## Expert Checks

- shortcut 실패를 수동 파일 편집으로 우회했는지 봅니다.
- for-ai 출력이 아닌 긴 원본을 먼저 읽었는지 봅니다.
- hook 정책을 무시하고 재실행만 반복했는지 봅니다.

## Failure Modes

- 긴 JSONL을 직접 읽다가 오래된 state를 믿는 상태.
- shortcut이 실패했는데 성공한 것으로 요약하는 상태.
- hook이 막은 작업을 다른 shell 명령으로 우회하는 상태.
- state를 바꾸는 명령을 검증 목적으로 반복 실행하는 상태.
- hook 출력과 실제 command 결과를 혼동하는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- shortcut 실패를 성공으로 해석.
- TASKS.md 직접 편집으로 상태 우회.
- gate shortcut 생략 후 commit.

## Verify

- $codex-context pack --for-ai.
- $codex-quality gate --for-ai.
- $codex-task trace --for-ai.

## Evidence

- 실행한 shortcut, exit code, 핵심 stdout을 보고합니다.
- 실패 시 stderr와 fallback 판단을 남깁니다.
- 최종 git status와 TASK state가 일치합니다.
- 대체 확인 명령과 원 shortcut 실패 원인을 함께 보고합니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
