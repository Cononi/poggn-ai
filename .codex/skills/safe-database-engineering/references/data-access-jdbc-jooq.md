# JDBC and jOOQ Adapter

## 활성화 조건

직접 JDBC, Spring JDBC, JdbcClient, jOOQ dependency 또는 generated source가
확인될 때 이 문서를 읽는다.

이 계층은 ORM이 아니다.
SQL과 transaction 의미를 직접 관리한다.

## 공통 JDBC 규칙

- `PreparedStatement` 또는 framework bind parameter를 사용한다.
- identifier와 sort 표현은 allowlist로 검증한다.
- connection, statement, result set을 확실히 닫는다.
- fetch size와 streaming 동작을 driver별로 확인한다.
- batch의 부분 실패와 update count를 처리한다.
- generated key와 timezone 타입 변환을 실제 driver에서 검증한다.
- transaction 경계 밖으로 connection-bound cursor를 반환하지 않는다.

## Spring JDBC

- named parameter가 identifier를 bind하지는 못한다.
- row mapper에서 NULL과 primitive 변환을 확인한다.
- exception translation의 실제 원인과 SQLState를 보존한다.
- transaction template과 annotation 경계를 혼용할 때 propagation을 확인한다.
- batch update의 결과 배열과 실패 위치를 기록한다.

## jOOQ

- code generation schema와 migration 순서를 일치시킨다.
- generated source가 어느 schema version을 표현하는지 기록한다.
- dialect를 실제 DBMS와 버전에 맞춘다.
- plain SQL API는 bind와 identifier 안전성을 직접 책임진다.
- fetch into의 이름 기반 매핑과 타입 변환을 테스트한다.
- transaction API와 Spring transaction 통합 경계를 확인한다.
- query object를 만들었다고 실행된 것으로 착각하지 않는다.

## SQL 검증

- 최종 SQL과 bind 타입을 확인한다.
- 반환 행 수와 update count를 확인한다.
- transaction rollback과 retry 동작을 검증한다.
- 대상 DBMS container에서 integration test를 실행한다.
- query plan은 실제 데이터 분포와 index 상태에서 확인한다.
