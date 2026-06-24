# PostgreSQL Adapter

## 활성화 조건

PostgreSQL driver, JDBC URL, container image, deployment 설정,
운영 정보 중 하나 이상의 명확한 증거가 있을 때만 사용한다.

먼저 server major와 minor version을 확인한다.
문법과 DDL 동작을 `current` 문서만 보고 모든 버전에 적용하지 않는다.

## 타입과 스키마

- 절대 시점은 `timestamptz` 사용을 우선 검토한다.
  애플리케이션의 직렬화와 표시 timezone은 별도 계약이다.
- 금액과 정밀 계산은 `numeric`의 precision과 scale을 명시한다.
- `jsonb`는 제약과 접근 패턴을 확인하고 사용한다.
- 대소문자 구분 식별자를 만들기 위해 무분별하게 quote하지 않는다.
- sequence, identity, UUID의 생성 위치와 batching 영향을 확인한다.

## DDL과 잠금

많은 DDL은 table lock을 획득하며 형태와 버전에 따라 영향이 다르다.

변경 전에 다음을 확인한다.

- 필요한 lock mode
- lock 대기 중 신규 transaction에 미치는 영향
- table rewrite 또는 full scan 여부
- transaction 안에서 실행 가능한지
- 실패 후 남는 객체와 재시도 방법

`CREATE INDEX CONCURRENTLY`는 일반 index 생성과 동작이 다르다.
transaction 제약, 추가 scan, 실패한 invalid index를 확인한다.
이름에 `CONCURRENTLY`가 있다고 무영향이라고 단정하지 않는다.

일부 CHECK와 FK는 검증을 분리할 수 있다.
`NOT VALID`와 `VALIDATE CONSTRAINT`의 지원 범위와 lock을
실제 PostgreSQL 버전에서 확인한다.

## Transaction과 Lock

PostgreSQL은 MVCC를 사용하지만 모든 경합을 제거하지 않는다.

- row lock mode의 실제 충돌 표를 확인한다.
- `SELECT FOR UPDATE`가 일반 SELECT까지 막는다고 가정하지 않는다.
- 여러 행을 잠글 때 안정적인 순서를 사용한다.
- deadlock은 한 transaction을 중단시킬 수 있으므로 처리한다.
- `lock_timeout`과 `statement_timeout`의 범위를 구분한다.
- session 수준 설정이 pool에 남지 않도록 transaction-local 설정을 검토한다.

잠금 진단에는 `pg_stat_activity`와 `pg_locks`를 함께 검토한다.
운영 조회도 개인정보와 SQL 원문 노출에 주의한다.

## 실행 계획

- `EXPLAIN`은 계획을 보여준다.
- `EXPLAIN ANALYZE`는 쿼리를 실제 실행한다.
- 쓰기 SQL의 ANALYZE는 disposable 환경 또는 안전한 transaction에서만 검토한다.
- `BUFFERS` 정보는 I/O 원인을 이해하는 데 도움이 된다.
- estimated rows와 actual rows 차이가 크면 통계와 데이터 분포를 확인한다.

운영에서 고비용 계획을 확인할 때 서비스 영향과 timeout을 먼저 정한다.

## Backfill

- PK 또는 안정적인 unique key range로 batch를 나눈다.
- 한 transaction에서 너무 많은 row version을 만들지 않는다.
- autovacuum, WAL, replica lag, table bloat를 관찰한다.
- `SKIP LOCKED`는 작업 queue에 유용할 수 있지만
  누락, 재시도, starvation 규칙을 명확히 한다.

## PostgreSQL 검증 항목

```text
server_version
transaction_isolation
lock_timeout
statement_timeout
migration transaction mode
index validity
constraint validation state
replication lag
long-running transactions
```

정확한 명령은 대상 버전의 공식 문서와 운영 정책을 확인한 뒤 사용한다.
