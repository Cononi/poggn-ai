---
name: parallel-lanes
description: MAW lane, wave, dependency graph와 병렬 실행 기준을 정할 때 사용합니다.
---

# parallel-lanes

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- dependency graph를 먼저 그리고 lane을 나눕니다.
- 같은 파일 ownership은 한 implementation lane에만 둡니다.
- contract/schema lane은 feature 구현보다 먼저 둡니다.

## Procedure

- 독립 기능만 병렬화하고 순서 의존 기능은 분리합니다.
- wave는 review 가능한 크기로 제한합니다.
- conflict 가능 파일은 통합 lane에서 다룹니다.
- downstream 검증은 upstream commit 뒤에 둡니다.

## Expert Rules

- 병렬화 단위는 사람 수가 아니라 독립적으로 merge 가능한 ownership입니다.
- shared contract는 모든 feature lane보다 앞선 선행 lane으로 둡니다.
- 같은 파일을 건드릴 가능성이 있으면 병렬 lane이 아니라 integration lane입니다.
- wave는 review, test, rollback 가능한 크기를 넘지 않아야 합니다.
- lane dependency는 코드 의존과 검증 의존을 분리해 표시합니다.
- 병렬 lane은 서로의 output을 전제로 하지 않도록 done contract를 씁니다.
- 병렬화 전 파일 ownership matrix를 만들고 겹치는 파일은 한 lane에 묶습니다.
- dependency edge는 schema, client, implementation, tests, QA 순서를 기본값으로 둡니다.

## Expert Checks

- 같은 파일을 여러 lane이 소유하는지 봅니다.
- agent 수가 ownership 선명도보다 우선됐는지 봅니다.
- 검증 wave가 빠졌는지 봅니다.

## Failure Modes

- agent 수를 맞추려고 artificial lane을 만드는 상태.
- schema와 API contract가 feature lane에서 동시에 바뀌는 상태.
- merge conflict 가능 파일을 여러 lane이 소유하는 상태.
- verification lane 없이 구현 lane만 끝나는 상태.
- shared type, config, generated artifact를 여러 lane이 동시에 수정하는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- dependency 무시한 병렬화.
- 동일 파일 다중 implementation lane.
- review 불가능한 대형 wave.

## Verify

- $codex-pipeline ready --for-ai.
- $codex-pipeline csv --ready.
- lane dependency review.

## Evidence

- lane graph와 owner file map이 있습니다.
- wave별 budget과 gate 결과가 있습니다.
- integration lane이 필요한 파일을 따로 표시합니다.
- 병렬 lane 완료 후 통합 검증 명령과 conflict review가 있습니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
