# Prisma ORM Adapter

## 적용 조건

다음 사용 증거를 확인했을 때만 읽는다.

- `schema.prisma`
- `@prisma/client`
- Prisma Client 호출
- `prisma/migrations`

Prisma CLI, Client, schema format의 실제 version과 datasource provider를 확인한다.
MongoDB와 relational database의 migration 절차를 같은 것으로 취급하지 않는다.

## Schema Source of Truth

프로젝트가 Prisma Migrate를 사용하면 다음을 함께 version control한다.

- `schema.prisma`
- 전체 migration history
- 필요한 generator와 client 생성 설정

Prisma schema만 수정하고 migration이 존재한다고 가정하지 않는다.
생성된 SQL은 초안이며 rename, drop, default, constraint를 직접 검토한다.

## Migration

- `migrate dev`는 개발용으로만 사용한다.
- test, staging, production에는 승인된 배포 경로를 사용한다.
- relational production 적용은 일반적으로 `migrate deploy`를 사용한다.
- production URL을 로컬에서 임시 교체해 직접 배포하지 않는다.
- 적용된 migration SQL을 수정하거나 삭제하지 않는다.
- drift와 실패 처리는 `resolve`를 자동 실행하지 않고 원인을 먼저 확인한다.
- `db push`를 versioned production migration의 대체물로 사용하지 않는다.

`migrate deploy`가 drift를 탐지한다고 가정하지 않는다.
배포 전 별도의 history와 schema 검증이 필요한지 확인한다.

## Query와 Fetch

- relation include가 만드는 query 수와 payload를 확인한다.
- 필요한 field만 `select`하는 방식을 검토한다.
- pagination은 안정되고 유일한 ordering을 사용한다.
- relation filter와 nested query의 실제 SQL을 확인한다.
- N+1이 발생하는 호출 패턴은 query log로 검증한다.

## Transaction

- nested write의 원자성 범위를 확인한다.
- interactive transaction은 짧게 유지한다.
- transaction 안에서 긴 외부 API 호출을 수행하지 않는다.
- retry 전에 idempotency와 commit 결과 불명확성을 설계한다.
- transaction option 지원과 isolation은 provider와 version에서 확인한다.

## Raw SQL

parameterized raw query API를 사용한다.
unsafe API나 문자열 보간은 allowlist와 별도 검토 없이는 사용하지 않는다.

## Mapping과 Constraint

- optional field와 DB null 의미를 맞춘다.
- native type으로 precision, length, timezone을 확인한다.
- referential action의 delete와 update 범위를 검토한다.
- unique와 FK를 application check만으로 대체하지 않는다.
- generated client type이 DB runtime constraint를 보장한다고 과장하지 않는다.

## 테스트

- 빈 DB와 이전 migration 상태에서 배포 migration을 검증한다.
- client 재생성 후 typecheck와 integration test를 실행한다.
- 실제 provider에서 unique race와 transaction rollback을 검증한다.
- generated SQL과 migration table 상태를 확인한다.

## 완료 Checklist

```text
[ ] Prisma CLI, Client, provider version 확인
[ ] schema와 migration history 정합성 확인
[ ] generated SQL의 drop, rename, constraint 검토
[ ] production 배포 명령과 대상 확인
[ ] query 수와 payload 검증
[ ] transaction과 raw SQL 안전성 검증
[ ] 실제 provider integration test 결과 기록
```
