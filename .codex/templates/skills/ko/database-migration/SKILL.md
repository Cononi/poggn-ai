---
name: database-migration
description: DB schema, migration, index, constraint, backfill 변경에 사용합니다.
---

# database-migration

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- schema 변경을 expand, backfill, switch, contract로 나눕니다.
- 데이터 손실 가능 변경은 rollback과 restore path를 먼저 둡니다.
- large table DDL은 lock과 online option을 검토합니다.

## Procedure

- nullable 추가 후 backfill 뒤 not null 전환을 검토합니다.
- rename은 add-copy-read-switch-drop 순서를 우선합니다.
- constraint 추가 전 기존 데이터 위반을 검사합니다.
- app deploy와 DB deploy 순서를 분리합니다.

## Expert Rules

- migration은 코드 변경이 아니라 데이터 생명주기 변경으로 봅니다.
- expand/contract 전략은 두 앱 버전이 동시에 떠도 안전해야 합니다.
- large table DDL은 lock, replication lag, rollback 시간을 계산합니다.
- index는 query plan, cardinality, write overhead 근거가 있어야 합니다.
- backfill은 재시작 가능하고 chunk 단위 진행률을 남겨야 합니다.
- constraint는 기존 데이터 위반 검사 후 단계적으로 강화합니다.
- down migration 가능 여부와 복구 불가 변경을 분리해 표시합니다.
- backfill은 chunk size, 재시작 위치, timeout, 관측 지표를 가집니다.

## Expert Checks

- ORM entity와 migration 순서가 맞는지 봅니다.
- index가 실제 query와 cardinality 근거를 갖는지 봅니다.
- partial failure 후 재실행 가능한지 봅니다.

## Failure Modes

- rename/drop을 한 번에 수행해 이전 앱 버전을 깨는 상태.
- not null 추가 전에 backfill과 default 전략이 없는 상태.
- rollback이 schema만 되돌리고 데이터 보정은 없는 상태.
- ORM entity가 migration보다 먼저 배포되는 상태.
- prod와 test DB 방언 차이로만 통과하는 migration.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- rollback 없는 destructive migration.
- 대형 테이블 blocking DDL 위험 무시.
- app/DB가 동시에만 성공하는 배포 순서.

## Verify

- migration dry run.
- schema diff review.
- rollback rehearsal 또는 plan.

## Evidence

- deploy 순서와 호환 버전 matrix가 있습니다.
- dry-run 또는 migration test 결과가 있습니다.
- rollback/forward-fix 절차가 기록됩니다.
- FK, unique, not null 전 orphan과 duplicate 탐지 쿼리가 있습니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
