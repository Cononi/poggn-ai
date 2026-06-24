# Django ORM Adapter

## 적용 조건

Django model, QuerySet, migration package 사용을 확인했을 때 읽는다.
Django, Python, database backend와 driver의 실제 version을 확인한다.

## Model과 Schema

- field null과 blank 의미를 구분한다.
- length, precision, timezone, default를 DB와 맞춘다.
- model validation이 DB constraint를 대체한다고 보지 않는다.
- `Meta.constraints`와 index가 실제 migration에 반영되는지 확인한다.
- delete cascade와 `on_delete`의 데이터 범위를 검토한다.

## QuerySet

- QuerySet의 lazy evaluation 시점을 확인한다.
- loop 안 relation 접근은 query count로 검증한다.
- `select_related`와 `prefetch_related`를 관계 형태에 맞게 선택한다.
- `only`와 `defer`가 후속 lazy query를 만들 수 있음을 확인한다.
- pagination에는 안정되고 유일한 ordering을 사용한다.
- raw SQL은 parameter binding을 사용한다.

## Transaction

- 여러 write는 `transaction.atomic` 경계로 묶는다.
- transaction 안에서 DB exception을 숨겨 상태를 손상시키지 않는다.
- request 전체 transaction의 lock과 latency를 검토한다.
- commit 뒤 실행해야 하는 side effect는 `on_commit`을 검토한다.
- multiple database 환경에서 원자성 범위를 명시한다.

## Bulk Operation

- bulk create, bulk update, QuerySet update의 callback 차이를 확인한다.
- `save`, signal, custom method가 우회되는지 확인한다.
- in-memory instance가 stale한지 확인한다.
- 대량 delete의 collector와 cascade 범위를 검토한다.

## Migration

- schema migration과 긴 data migration을 가능하면 분리한다.
- data migration은 historical model을 사용한다.
- `RunPython`의 reverse 동작 가능 여부를 명시한다.
- 적용된 migration 파일을 수정하거나 삭제하지 않는다.
- `makemigrations --check`, `showmigrations`, `sqlmigrate`를 활용한다.

## 테스트

- production과 같은 backend에서 migration과 query를 검증한다.
- query count로 N+1을 검증한다.
- atomic rollback과 concurrent unique race를 검증한다.
- data migration의 재실행과 reverse 가능성을 확인한다.

## 완료 Checklist

```text
[ ] Django, backend, driver version 확인
[ ] model과 migration 정합성 확인
[ ] QuerySet 평가 시점과 query count 검증
[ ] atomic 경계와 on_commit 검토
[ ] bulk operation의 signal 우회 확인
[ ] data migration과 reverse 검증
[ ] 실제 backend integration test 결과 기록
```
