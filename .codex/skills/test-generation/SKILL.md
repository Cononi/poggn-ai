---
name: test-generation
description: 비즈니스 로직, 권한, 상태 전이, API 계약 테스트를 작성할 때 사용합니다.
---

# test-generation

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- 테스트 이름은 business behavior를 설명해야 합니다.
- happy path보다 invariant와 negative path를 우선합니다.
- bug fix는 실패 재현 테스트를 먼저 작성합니다.

## Procedure

- auth 변경은 unauthorized와 forbidden case를 분리합니다.
- JPA query는 mapping과 fetch behavior를 검증합니다.
- API test는 status, validation, response, error shape를 봅니다.
- time, random, network는 deterministic boundary로 격리합니다.

## Expert Rules

- 테스트는 implementation detail이 아니라 깨지면 안 되는 behavior를 고정합니다.
- negative path는 보안, 권한, validation, state transition에서 우선합니다.
- fixture는 읽는 사람이 business precondition을 이해할 만큼 작아야 합니다.
- mock은 외부 경계에 쓰고 domain rule을 대체하지 않습니다.
- 시간, 랜덤, 네트워크, 동시성은 deterministic boundary로 격리합니다.
- 회귀 테스트는 실패 재현이 먼저이고 green 확인은 그 다음입니다.
- 권한 테스트는 본인, 타인, 미인증, 권한 부족 case를 분리합니다.
- API validation은 누락, null, 빈 값, 형식 오류를 분리합니다.

## Expert Checks

- mock이 domain rule을 가리고 있는지 봅니다.
- fixture가 과도하거나 의도를 숨기는지 봅니다.
- 기대값 완화가 원인 분석 없이 이뤄졌는지 봅니다.

## Failure Modes

- happy path만 있어 권한 우회나 validation 실패를 못 잡는 상태.
- mock이 service invariant를 대신 검증하는 상태.
- assertion이 너무 느슨해 실제 contract drift를 통과시키는 상태.
- flaky 원인을 모른 채 retry만 늘리는 상태.
- migration 테스트가 기존 데이터 전환을 포함하지 않는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- getter/wiring 테스트만 추가.
- auth 변경에 negative test 없음.
- 실패 원인 분석 없이 expectation 완화.

## Verify

- unit/integration test command.
- coverage of negative path.
- $codex-verify gate --for-ai.

## Evidence

- 테스트명이 business behavior를 설명합니다.
- unauthorized와 forbidden case가 분리됩니다.
- targeted test 실행 결과와 실패 재현 여부를 보고합니다.
- persistence 테스트는 SQL 수나 lazy access 실패를 관측합니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
