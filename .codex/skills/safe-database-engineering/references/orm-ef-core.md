# Entity Framework Core Adapter

## 적용 조건

EF Core package, `DbContext`, entity configuration, migration 사용을 확인했을 때 읽는다.
.NET, EF Core, database provider의 실제 version을 확인한다.

## DbContext

- DbContext는 짧은 unit of work로 사용한다.
- thread-safe가 아니므로 여러 thread나 병렬 작업에서 공유하지 않는다.
- async 호출을 완료한 뒤 같은 context를 다시 사용한다.
- unrecoverable exception이 발생한 context를 계속 사용하지 않는다.
- DI lifetime과 background job scope를 확인한다.

## Schema Source of Truth

code-first, database-first, hybrid 중 저장소의 실제 방식을 확인한다.
model snapshot, migration, 실제 DB schema가 같다고 가정하지 않는다.

- generated migration을 항상 검토한다.
- rename이 drop과 add로 생성되지 않았는지 확인한다.
- 적용된 production migration을 remove 또는 재생성하지 않는다.
- `EnsureCreated`를 migration 관리 DB에 혼용하지 않는다.
- production startup auto-migration은 별도 운영 검토 없이 사용하지 않는다.

## Query

- tracking이 필요한 query와 read-only query를 구분한다.
- `Include`가 만드는 join과 payload를 확인한다.
- 여러 collection include의 cartesian explosion을 검토한다.
- split query의 round trip과 consistency trade-off를 확인한다.
- projection으로 필요한 column만 가져오는 방식을 검토한다.
- pagination ordering을 fully unique하게 만든다.

## Write와 Concurrency

- `SaveChanges`가 하나의 transaction에서 보장하는 범위를 확인한다.
- concurrency token 또는 row version 필요성을 검토한다.
- concurrency exception의 retry 또는 사용자 충돌 의미를 정의한다.
- cascade delete와 required relationship의 삭제 범위를 검토한다.
- raw SQL과 interpolated SQL의 parameterization을 확인한다.

## Migration 배포

production에는 검토 가능한 SQL script 또는 승인된 bundle을 우선 검토한다.
runtime migration은 schema 권한, 다중 instance, rollback 문제를 분석한다.

- 이전 migration에서 latest로 script를 생성하고 검토한다.
- idempotent script도 정확한 대상과 provider에서 시험한다.
- model snapshot과 migration code를 함께 review한다.

## 테스트

- 실제 provider에서 integration test를 수행한다.
- InMemory provider 성공을 relational DB 증거로 사용하지 않는다.
- tracking, split query, concurrency, cascade를 검증한다.
- 이전 migration DB에서 upgrade와 application startup을 확인한다.

## 완료 Checklist

```text
[ ] EF Core와 provider version 확인
[ ] DbContext lifetime과 병렬 사용 확인
[ ] model, snapshot, migration 정합성 확인
[ ] generated migration의 data loss 검토
[ ] tracking과 related-data query 검증
[ ] concurrency와 cascade 검증
[ ] production 적용 script 또는 bundle 검토
```
