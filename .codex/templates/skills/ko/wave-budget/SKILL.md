---
name: wave-budget
description: 대형 MAW 작업을 wave로 분할하고 검증 순서를 관리할 때 사용합니다.
---

# wave-budget

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- epic을 contract, schema, backend, frontend, verification으로 나눕니다.
- 각 wave는 review 가능한 파일 수와 diff 크기를 유지합니다.
- schema/API contract는 구현 wave 전에 완료합니다.

## Procedure

- 통합 위험이 큰 파일은 같은 wave에 묶습니다.
- 검증 wave는 구현 wave 뒤에 반드시 둡니다.
- wave 사이에는 merge와 quality gate를 실행합니다.
- 큰 lane은 feature slice로 다시 나눕니다.

## Expert Rules

- wave는 작업 묶음이 아니라 검증 가능한 release slice입니다.
- contract/schema wave는 구현 wave보다 앞서고 독립 검증을 갖습니다.
- 각 wave는 budget, owner, merge 순서, rollback 기준을 가져야 합니다.
- 실패한 wave 뒤의 wave는 시작 조건을 다시 평가합니다.
- 큰 diff는 기능 slice보다 위험 slice로 나누는 것이 안전할 때가 많습니다.
- wave 사이에는 integration diff와 quality gate를 확인합니다.
- wave 크기 상한은 파일 수, diff 줄 수, ownership 수로 구체화합니다.
- 다음 wave 진입 조건은 commit, quality gate, blocker 없음입니다.

## Expert Checks

- parallelism이 merge 가능성보다 우선됐는지 봅니다.
- wave 실패 후 다음 wave가 시작됐는지 봅니다.
- 모든 wave의 TASK/commit 연결을 확인합니다.

## Failure Modes

- 모든 구현을 한 wave에 넣고 검증을 마지막으로 미루는 상태.
- schema 변경과 frontend 의존 변경이 같은 wave에서 경합하는 상태.
- wave 실패 후 다음 wave가 이미 commit된 상태.
- TASK/commit link가 wave별로 남지 않는 상태.
- contract/schema wave 실패 후 dependent wave가 계속 진행되는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- contract 없이 feature 구현 시작.
- review 불가능한 대형 wave.
- 검증 wave 생략.

## Verify

- $codex-waves plan.
- $codex-waves next.
- $codex-pipeline ready --for-ai.

## Evidence

- wave plan에 dependency와 owner가 있습니다.
- 각 wave commit이 budget gate를 통과합니다.
- wave 종료마다 merge/verify 결과를 보고합니다.
- wave 실패 후 scope 축소, split, rollback 중 하나를 선택합니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
