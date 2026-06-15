---
name: token-budget
description: SAW/MAW token, context, lane/wave 예산을 관리할 때 사용합니다.
---

# token-budget

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- 작업 크기를 파일 수, diff 줄, context 양으로 봅니다.
- SAW 예산 초과는 MAW 전환 신호입니다.
- 예산이 부족하면 검증을 줄이지 말고 scope를 줄입니다.

## Procedure

- MAW는 전체 epic이 아니라 lane/wave 단위 예산을 씁니다.
- context pack과 targeted read로 토큰을 아낍니다.
- subagent에는 필요한 파일과 목표만 전달합니다.
- 큰 reference는 heading과 검색어로 부분 로드합니다.

## Expert Rules

- budget은 답변 길이가 아니라 안전하게 처리 가능한 변경 표면입니다.
- 토큰 절약은 필수 파일 생략이 아니라 scope 축소로 해결합니다.
- MAW는 epic 전체가 커도 lane과 wave가 review 가능해야 합니다.
- subagent에는 목표, owner files, 금지 파일, output contract만 전달합니다.
- 로그는 원인 라인 중심으로 요약하고 반복 stack trace는 줄입니다.
- budget 초과는 실패가 아니라 분할 설계 신호입니다.
- 예산 산정 입력은 파일 수, diffstat, 참조 문서 수, 로그 크기입니다.
- compact 이후 최신 TASK, HEAD, changed files를 재확인합니다.

## Expert Checks

- 토큰 절약을 이유로 필수 파일을 읽지 않았는지 봅니다.
- 반복 로그 원문을 과도하게 붙였는지 봅니다.
- lane이 review 불가능한 크기인지 봅니다.

## Failure Modes

- 필수 contract 파일을 읽지 않고 구현하는 상태.
- 한 lane이 너무 커서 review와 rollback이 불가능한 상태.
- 검증을 생략해 예산을 맞추는 상태.
- subagent prompt에 전체 대화와 불필요한 history를 넣는 상태.
- 필수 파일 미확인을 예산 문제로 축소 보고하는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- budget 때문에 test/security 생략.
- 너무 큰 lane을 그대로 배정.
- 필수 계약 미확인.

## Verify

- $codex-budget status.
- $codex-context pack --for-ai.
- diff stat review.

## Evidence

- 파일 수, diff 라인, context 양 추정이 있습니다.
- 분할 기준과 남은 follow-up이 기록됩니다.
- 검증 항목이 예산 축소 후에도 유지됩니다.
- 긴 로그는 실패 명령, 핵심 에러, 관련 파일 위치로 압축됩니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
