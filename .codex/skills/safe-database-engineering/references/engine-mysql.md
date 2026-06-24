# MySQL and MariaDB Adapter

## 활성화 조건

MySQL 또는 MariaDB driver, JDBC URL, container image, deployment 설정,
운영 정보 중 하나 이상의 명확한 증거가 있을 때만 사용한다.

MySQL과 MariaDB를 같은 제품으로 취급하지 않는다.
제품, major/minor version, storage engine을 각각 확인한다.

## 타입과 스키마

- InnoDB 사용 여부를 확인한다.
- charset과 collation을 database, table, column, connection에서 확인한다.
- case sensitivity가 환경별 filesystem과 collation에 따라 달라질 수 있다.
- `datetime`과 `timestamp`의 범위와 timezone 변환 차이를 확인한다.
- decimal precision과 scale을 명시한다.
- unsigned 타입은 다른 DB로 이동할 가능성과 ORM 매핑을 검토한다.
- zero date 같은 비표준 값의 허용 설정을 확인한다.

## DDL

online DDL 지원은 버전과 변경 형태에 따라 다르다.

- 선택 가능한 algorithm과 lock 수준을 확인한다.
- 요청한 algorithm이 실패 대신 fallback하는지 확인한다.
- table copy, metadata lock, temp storage 영향을 확인한다.
- replica와 binary log에 미치는 영향을 확인한다.
- 큰 DDL은 운영과 유사한 데이터에서 먼저 검증한다.

`ONLINE` 또는 `LOCK=NONE`이라는 이름만으로 무잠금이라고 단정하지 않는다.
metadata lock과 짧은 exclusive 구간을 확인한다.

## Transaction과 Lock

- 실제 transaction isolation을 확인한다.
- InnoDB의 next-key와 gap lock 가능성을 검토한다.
- index를 사용하지 않는 locking query가 넓은 범위를 잠글 수 있다.
- autocommit 상태와 framework transaction 경계를 확인한다.
- deadlock과 lock wait timeout을 구분해 처리한다.
- 여러 행과 테이블을 같은 순서로 접근한다.

## 실행 계획

- `EXPLAIN` 결과의 access type, rows, filtered, key를 함께 본다.
- 지원 버전에서는 실제 실행 정보를 제공하는 기능을 검토한다.
- 실제 실행 기능은 쿼리를 수행하므로 운영에서 주의한다.
- optimizer가 선택한 index와 통계 상태를 확인한다.
- collation 또는 implicit conversion으로 index가 무효화되는지 확인한다.

## Replication

- read replica의 lag와 read-after-write 요구를 확인한다.
- DDL과 대량 DML이 replica 적용을 지연시킬 수 있다.
- binary log format과 row volume 영향을 검토한다.
- failover 후 auto-increment, GTID, connection routing 가정을 확인한다.

## MySQL 검증 항목

```text
product and server version
storage engine
character set and collation
transaction isolation
autocommit
sql mode
DDL algorithm and lock behavior
replication lag
long-running transactions
```

정확한 명령은 대상 제품과 버전의 공식 문서를 확인한 뒤 사용한다.
