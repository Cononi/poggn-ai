# Query Performance

## 먼저 쿼리 계약을 정의한다

SQL을 튜닝하기 전에 다음을 기록한다.

- 반환해야 하는 데이터
- 허용 가능한 최신성
- 예상 입력 범위와 선택도
- 평균 및 최악의 결과 행 수
- 정렬과 pagination 요구
- latency 목표와 호출 빈도
- 읽기 중 일관성 요구

결과 상한이 없는 목록 API와 batch 조회를 기본값으로 두지 않는다.

## 정확성과 안전

- 모든 외부 값은 bind parameter로 전달한다.
- table, column, sort direction 같은 identifier는 allowlist로 검증한다.
- NULL 비교와 3-valued logic을 확인한다.
- timezone, collation, case sensitivity를 명시한다.
- JOIN으로 행이 증식하는지 확인한다.
- UPDATE와 DELETE는 대상 행 수를 사전에 검증한다.

## 실행 계획

실행 계획은 실제 엔진과 대표 데이터 분포에서 확인한다.

다음을 함께 본다.

- estimated rows와 actual rows의 차이
- scan과 join 방식
- filter에서 제거된 행
- sort, temp, spill
- index condition과 residual filter
- 반복 실행 횟수
- buffer 또는 I/O 정보
- planning과 execution 시간

통계가 오래되었거나 테스트 데이터가 균일하면 계획이 운영과 다를 수 있다.

`EXPLAIN ANALYZE`는 실제 쿼리를 실행할 수 있다.
쓰기 SQL이나 운영 환경에서는 정확한 동작을 확인하고 명시적 승인 없이 실행하지 않는다.

## 인덱스 설계

쿼리에서 시작해 인덱스를 설계한다.

- equality, range, join, order 조건의 조합
- 컬럼 순서와 선택도
- covering 가능성과 row lookup 비용
- partial 또는 filtered index 가능성
- expression index와 collation
- 읽기 이득과 쓰기, vacuum, storage 비용

인덱스가 존재한다는 사실만으로 사용된다고 단정하지 않는다.
계획과 운영 관측으로 확인한다.

## Pagination

작은 데이터와 임의 페이지 이동은 OFFSET이 단순할 수 있다.
큰 offset과 실시간 변경이 있는 목록은 keyset pagination을 검토한다.

keyset에는 다음이 필요하다.

- 안정적이고 유일한 정렬 순서
- 마지막 행의 cursor
- 정렬 방향에 맞는 비교 조건
- 동일 값 tie-breaker
- cursor 직렬화와 검증

전체 count는 별도 고비용 쿼리가 될 수 있다.
정확한 count가 정말 필요한지 확인한다.

## 큰 조회와 Batch

- 필요한 컬럼만 선택한다.
- 한 번에 전체 결과를 메모리에 올리지 않는다.
- streaming 또는 chunking의 transaction과 connection 수명을 확인한다.
- IN 목록의 크기와 plan 변화를 관찰한다.
- batch 쓰기는 driver와 ORM의 실제 batching을 확인한다.
- 한 transaction에 과도한 row를 넣지 않는다.

## Query 변경 증거

```md
## Query

- Purpose: 쿼리 목적
- SQL path: 실제 SQL 또는 생성 위치
- Parameters: 입력 범위와 분포
- Result bound: 최대 또는 예상 행 수
- Before plan: 핵심 비용과 실제 행
- After plan: 핵심 비용과 실제 행
- Index change: 추가, 유지, 제거 근거
- Engine/version: 실행한 DBMS
- Data scale: 테스트 데이터 규모와 한계
- Remaining risk: 운영에서 확인할 항목
```

microbenchmark 하나만으로 운영 성능을 보장하지 않는다.
latency뿐 아니라 CPU, I/O, lock, connection, replica 영향도 본다.
