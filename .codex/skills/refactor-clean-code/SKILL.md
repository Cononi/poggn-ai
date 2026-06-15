---
name: refactor-clean-code
description: 동작 보존 리팩토링, 중복 제거, 책임 분리에 사용합니다.
---

# refactor-clean-code

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- 리팩토링 목표와 보존할 동작을 먼저 적습니다.
- public API, DB schema, error contract 변경은 승인 없이 하지 않습니다.
- 동작 보존 증거가 있을 때만 완료합니다.

## Procedure

- 테스트가 없으면 characterization test를 고려합니다.
- 긴 함수는 decision, IO, mapping 단위로 나눕니다.
- 순환 의존을 끊고 domain boundary를 강화합니다.
- diff가 커지면 단계별 commit이나 follow-up으로 나눕니다.

## Expert Rules

- refactor는 새 기능이 아니라 기존 의미를 더 선명하게 만드는 작업입니다.
- 동작 보존 기준을 테스트, snapshot, contract, diff로 먼저 잡습니다.
- 추상화는 중복 제거보다 변경 이유를 분리할 때 정당합니다.
- 이름 변경은 dependency 방향과 responsibility가 바뀔 때만 가치가 큽니다.
- transaction, cache, lazy loading, concurrency 의미가 바뀌지 않는지 봅니다.
- 큰 리팩토링은 characterization test와 단계별 commit이 필요합니다.
- 리팩토링 전후 public behavior invariant를 파일 또는 테스트 단위로 적습니다.
- shared helper 추출은 두 곳 이상 호출부나 명확한 boundary 이득이 있을 때만 합니다.

## Expert Checks

- 이름만 바꾸고 구조가 그대로인지 봅니다.
- 성능이나 transaction 의미가 바뀌었는지 봅니다.
- 추상화가 실제 중복을 줄였는지 봅니다.

## Failure Modes

- public API나 error shape가 몰래 바뀌는 상태.
- 공통 util이 domain 규칙을 숨겨 더 결합되는 상태.
- 테스트 없이 구조 변경만 대량으로 일어나는 상태.
- 성능 최적화라는 이름으로 가독성과 correctness를 잃는 상태.
- transaction, async timing, memoization, cache key 의미가 몰래 바뀌는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- 숨은 동작 변경.
- 테스트 없는 대규모 구조 변경.
- 책임 분리 없는 rename-only cleanup.

## Verify

- existing tests.
- targeted regression test.
- $codex-quality gate --for-ai.

## Evidence

- 보존할 동작과 검증 명령이 기록됩니다.
- before/after 책임 경계가 설명됩니다.
- 동작 변경이 있으면 별도 TASK로 분리됩니다.
- rename, move, extraction은 behavior diff와 함께 검증합니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
