---
name: context-control
description: 불필요한 repo scan을 막고 필요한 context만 좁게 읽을 때 사용합니다.
---

# context-control

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- 작업 시작과 재개 시 context pack을 먼저 실행합니다.
- rg와 name-status로 파일 후보를 좁힙니다.
- 필수 계약 파일은 토큰 절약을 이유로 생략하지 않습니다.

## Procedure

- 현재 TASK, 변경 파일, git status를 먼저 확인합니다.
- 전체 diff는 gate 실패나 사용자가 요구할 때만 읽습니다.
- subagent prompt에는 필요한 파일과 기대 출력만 전달합니다.
- 대형 문서는 heading이나 search hit 중심으로 읽습니다.

## Expert Rules

- context는 많이 읽는 것이 아니라 결정에 필요한 것을 읽는 것입니다.
- 대화 기억은 현재 파일, git diff, state pack보다 낮은 신뢰도를 둡니다.
- 민감 파일은 필요성, 목적, 사용 범위를 정한 뒤 엽니다.
- subagent prompt에는 결론이 아니라 필요한 원자료와 done contract를 줍니다.
- 대형 파일은 symbol, heading, search hit로 좁히고 필요한 부분만 엽니다.
- 계약 파일은 토큰 이유로 생략하지 않고 우선순위를 올립니다.
- context pack 이후 변경이 생기면 pack 재실행 전 판단하지 않습니다.
- user change와 agent change가 섞인 파일은 hunk 단위로 소유를 구분합니다.

## Expert Checks

- 오래된 대화 기억을 현재 파일보다 우선했는지 봅니다.
- 전체 repo를 이유 없이 읽었는지 봅니다.
- 민감 파일을 필요 이상으로 열었는지 봅니다.

## Failure Modes

- repo 전체를 읽고도 실제 수정 파일을 놓치는 상태.
- 오래된 TASKS 출력이 JSONL/state보다 우선되는 상태.
- subagent에게 불필요한 history를 넘겨 판단을 오염시키는 상태.
- secret 가능 파일을 검토 이유 없이 여는 상태.
- 추론 근거가 대화 기억뿐인데 현재 파일 확인이 없는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- stale context pack으로 판단.
- 필수 파일 미확인 상태로 구현.
- subagent에 unrelated 파일 대량 전달.

## Verify

- $codex-context pack --for-ai.
- git status --short.
- rg targeted search.

## Evidence

- context pack, rg 결과, 실제 읽은 파일 목록이 있습니다.
- 읽지 않은 관련 파일과 이유를 설명합니다.
- subagent 입력이 필요한 범위로 제한됩니다.
- 민감 파일을 열었다면 TASK 관련성과 사용 범위를 설명합니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
