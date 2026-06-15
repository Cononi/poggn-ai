---
name: jpa
description: JPA entity, repository, query, transaction, lazy loading, N+1에 사용합니다.
---

# jpa

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- transaction, fetch plan, ownership 기준을 먼저 고정합니다.
- entity lifecycle과 aggregate boundary를 먼저 정합니다.
- DTO mapping 경로의 lazy access를 모두 찾습니다.

## Procedure

- list endpoint는 pagination과 fetch plan을 함께 설계합니다.
- collection fetch join은 duplicate와 pagination 왜곡을 확인합니다.
- write transaction 안에서 invariant와 ownership을 검증합니다.
- bulk update/delete는 persistence context 동기화를 고려합니다.

## Expert Rules

- fetch plan은 endpoint별 응답 모델과 함께 설계합니다.
- transaction boundary는 service use case의 invariant 단위로 둡니다.
- owner scope는 query predicate와 domain check 둘 다에서 확인합니다.
- collection fetch join은 pagination 전에 duplicate와 memory 폭증을 검토합니다.
- OSIV off에서도 DTO mapping이 동작하도록 lazy access를 통제합니다.
- bulk query 후 persistence context stale 상태를 명시적으로 처리합니다.
- pagination API에서 collection fetch join 사용은 차단 조건을 먼저 검토합니다.
- equals/hashCode는 lazy association이나 mutable field에 의존하지 않습니다.

## Expert Checks

- entity가 REST response로 직접 반환되는지 봅니다.
- OSIV로 N+1이나 lazy error를 숨겼는지 봅니다.
- repository method가 use case를 드러내는지 봅니다.

## Failure Modes

- @Transactional 없이 여러 entity를 변경하는 상태.
- controller나 serializer가 lazy loading을 유발하는 상태.
- repository method name이 business intent를 숨기는 상태.
- delete/update query가 tenant나 owner predicate 없이 실행되는 상태.
- cascade와 orphanRemoval에 aggregate 소유권 근거가 없는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- N+1 위험 방치.
- transaction 없는 multi-step write.
- owner scope 없는 update/delete query.

## Verify

- JPA integration test.
- SQL/fetch plan review.
- service transaction test.

## Evidence

- SQL log 또는 query count로 N+1을 확인했습니다.
- service integration test가 transaction과 ownership을 검증합니다.
- list API의 pagination과 fetch plan 근거가 있습니다.
- lock, unique constraint, retry 등 동시성 write 보호 근거가 있습니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
