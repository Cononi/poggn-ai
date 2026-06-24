# Transactions and Concurrency

## 트랜잭션 경계

트랜잭션은 비즈니스 불변조건을 원자적으로 지켜야 하는 최소 단위로 둔다.

- 너무 짧으면 불변조건이 깨질 수 있다.
- 너무 길면 lock, connection, deadlock 비용이 커진다.
- 사용자 입력이나 느린 외부 호출을 열린 transaction 안에서 기다리지 않는다.
- 외부 시스템과 DB를 하나의 로컬 transaction으로 착각하지 않는다.

외부 메시지와 DB 상태의 일관성이 필요하면 outbox, inbox,
idempotency key, 보상 절차를 검토한다.

## 격리 수준

격리 수준 이름만 보고 안전성을 단정하지 않는다.
DBMS의 실제 구현과 workload에서 다음 현상을 검토한다.

- dirty read
- non-repeatable read
- phantom
- lost update
- write skew
- serialization failure

필요한 불변조건과 허용 가능한 anomaly를 먼저 정의한다.
그다음 isolation, constraint, lock, retry 조합을 선택한다.

## 낙관적 동시성

충돌이 드물고 재시도가 가능한 경우 version 기반 검사를 검토한다.

- 갱신 조건에 예상 version을 포함한다.
- 영향받은 행 수가 0이면 충돌로 처리한다.
- 사용자의 입력을 조용히 덮어쓰지 않는다.
- retry 전에 최신 상태로 비즈니스 연산을 다시 계산한다.
- 동일 요청의 중복 실행이 안전한지 확인한다.

## 비관적 잠금

충돌 가능성이 높고 특정 행의 순서를 보장해야 할 때 검토한다.

- transaction 안에서만 의미가 유지되는지 확인한다.
- lock 범위와 실제 생성 SQL을 확인한다.
- 읽기까지 막는다고 임의로 가정하지 않는다.
- timeout과 실패 처리를 정한다.
- lock을 잡은 뒤 느린 외부 호출을 하지 않는다.

## Deadlock

여러 객체를 잠글 때 모든 코드 경로에서 같은 순서를 사용한다.

- table과 row 접근 순서를 문서화한다.
- 가장 제한적인 필요한 lock을 적절한 시점에 획득한다.
- transaction을 짧게 유지한다.
- deadlock victim은 예측하지 않는다.
- 재시도는 제한 횟수와 jitter를 두고 수행한다.

재시도 대상 오류를 DBMS와 driver별로 확인한다.
모든 SQL 오류를 자동 재시도하지 않는다.

## Idempotency

재시도 가능한 쓰기는 중복 실행을 견뎌야 한다.

- 요청 단위 idempotency key
- UNIQUE 제약조건
- 처리 상태와 결과 저장
- 원자적 claim 또는 compare-and-set
- 완료된 요청의 동일 결과 반환

애플리케이션 메모리의 중복 방지만으로 분산 요청을 막지 않는다.

## 카운터와 재고

read-modify-write는 lost update 가능성을 검토한다.

가능한 패턴은 다음과 같다.

- 조건부 원자 UPDATE
- version을 포함한 낙관적 갱신
- 행 잠금 후 검증과 갱신
- append-only ledger와 계산된 잔액

음수 금지 같은 규칙은 조건부 갱신과 CHECK 제약을 함께 검토한다.

## 동시성 테스트

단일 thread 테스트로 잠금 동작을 증명하지 않는다.

최소 두 연결과 명시적인 barrier를 사용한다.

1. transaction A가 읽기 또는 lock을 수행한다.
2. transaction B가 충돌 작업을 시도한다.
3. block, timeout, conflict 또는 성공을 관찰한다.
4. A를 commit 또는 rollback한다.
5. B의 최종 결과와 데이터 불변조건을 확인한다.

다음을 기록한다.

- DBMS와 버전
- isolation level
- 실행 SQL
- transaction 시작과 종료 순서
- timeout과 error code
- 최종 데이터

테스트가 우연히 순차 실행되지 않도록 동기화 지점을 둔다.
