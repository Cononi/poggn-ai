# TypeORM Adapter

## 적용 조건

TypeORM dependency, DataSource, entity decorator, repository 사용을 확인했을 때 읽는다.
TypeORM, Node, driver와 DB engine의 실제 version을 확인한다.

## Schema Source of Truth

- production에서 `synchronize: true`를 사용하지 않는다.
- schema sync를 versioned migration의 대체물로 사용하지 않는다.
- generated migration SQL을 직접 검토한다.
- 적용된 migration을 수정하거나 삭제하지 않는다.
- `up`과 `down`이 실제 데이터 보존 역연산인지 확인한다.

## DataSource와 Entity

- entity discovery 경로가 build artifact와 일치하는지 확인한다.
- duplicate entity 또는 `.ts`와 `.js` 동시 로딩을 방지한다.
- null, precision, enum, default, generated column을 DB와 맞춘다.
- cascade와 orphan action의 삭제 범위를 검토한다.
- listener와 subscriber가 bulk operation에서 적용되는지 확인한다.

## Query와 Relation

- eager와 lazy relation의 실제 query 시점을 확인한다.
- QueryBuilder join의 row 중복과 payload를 검토한다.
- relation load 전략이 만드는 N+1을 query log로 검증한다.
- raw expression과 동적 identifier는 parameter와 allowlist를 사용한다.
- pagination에는 안정되고 유일한 ordering을 사용한다.

## Transaction

transaction callback 안에서는 전달받은 transactional manager만 사용한다.
전역 manager나 다른 DataSource repository를 섞어 transaction을 벗어나지 않는다.

- transaction을 짧게 유지한다.
- isolation 지원을 driver와 DB version에서 확인한다.
- retry와 idempotency를 별도로 설계한다.
- lock API가 생성하는 SQL과 timeout을 확인한다.

## Migration

- `migration:generate` 결과는 초안으로 취급한다.
- DataSource 경로와 compiled artifact를 확인한다.
- migration transaction mode를 DDL 특성에 맞게 검토한다.
- fake run 또는 fake revert를 자동 실행하지 않는다.
- transaction을 끄면 실패 중간 상태와 복구 방법을 기록한다.

## 테스트

- 실제 driver와 DB에서 migration을 적용한다.
- relation query 수, transaction rollback, lock을 검증한다.
- generated SQL의 rename, drop, constraint를 확인한다.
- build 후 migration과 entity discovery가 정상인지 확인한다.

## 완료 Checklist

```text
[ ] TypeORM, Node, driver version 확인
[ ] synchronize와 migration 설정 확인
[ ] entity discovery와 build artifact 확인
[ ] relation query와 payload 검증
[ ] transactional manager 사용 확인
[ ] generated migration과 transaction mode 검토
[ ] 실제 DB integration test 결과 기록
```
