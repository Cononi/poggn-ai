# SQLAlchemy ORM Adapter

## 적용 조건

SQLAlchemy mapping, `Session`, `AsyncSession`, declarative model 사용을 확인했을 때 읽는다.
SQLAlchemy major version, DB dialect, driver, Alembic 사용 여부를 확인한다.

## Session과 Unit of Work

- Session 수명은 data access 함수 밖의 application 경계에서 관리한다.
- 하나의 Session을 여러 thread에서 공유하지 않는다.
- 하나의 AsyncSession을 여러 concurrent task에서 공유하지 않는다.
- transaction 시작, commit, rollback, close 지점을 명확히 한다.
- flush와 commit을 같은 것으로 취급하지 않는다.
- rollback 뒤 object state와 session 재사용 가능성을 확인한다.

## Mapping

- relationship의 owning 방향과 cascade를 검토한다.
- `delete-orphan`이 제거할 row 범위를 확인한다.
- nullable, default, enum, numeric, temporal type을 DB와 맞춘다.
- Python-side default와 server default를 구분한다.
- identity map이 query cache라고 가정하지 않는다.

## Loading

- lazy load가 request 또는 session 종료 뒤 발생하지 않게 한다.
- `selectinload`, `joinedload` 등 전략을 query shape로 선택한다.
- collection join의 row 증폭과 pagination을 확인한다.
- async 코드에서 암묵적 I/O가 발생하는 경로를 확인한다.
- N+1은 실제 SQL count로 검증한다.

## Write와 Bulk Operation

- autoflush가 query 전에 write를 발생시킬 수 있음을 고려한다.
- bulk update와 delete가 identity map을 어떻게 동기화하는지 확인한다.
- server-generated value와 refresh 시점을 검토한다.
- raw SQL은 bound parameter를 사용한다.
- optimistic version column 필요성을 검토한다.

## Alembic

- autogenerate 결과는 초안으로 취급한다.
- rename, enum, default, constraint, index를 직접 검토한다.
- 적용된 revision을 수정하거나 삭제하지 않는다.
- 빈 DB와 직전 revision에서 upgrade를 검증한다.
- downgrade가 데이터 보존 역연산인지 확인한다.

## 테스트

- production과 같은 dialect의 integration test를 사용한다.
- Session scope와 rollback을 검증한다.
- concurrent task별 별도 Session 사용을 검증한다.
- loader strategy별 SQL 수와 result cardinality를 검증한다.
- Alembic upgrade 경로와 schema 결과를 확인한다.

## 완료 Checklist

```text
[ ] SQLAlchemy, driver, dialect version 확인
[ ] Session 또는 AsyncSession scope 확인
[ ] transaction과 flush 시점 확인
[ ] loader strategy와 query count 검증
[ ] cascade와 bulk DML 영향 확인
[ ] Alembic revision과 generated SQL 검토
[ ] 실제 dialect integration test 결과 기록
```
