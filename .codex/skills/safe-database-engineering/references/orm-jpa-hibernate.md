# JPA and Hibernate Adapter

## 활성화 조건

Jakarta Persistence, Hibernate ORM, JPA provider 설정 또는 entity 소스가
명확히 확인될 때만 이 문서를 읽는다.

Spring Data JPA를 사용하면 이 문서와
`references/orm-spring-data-jpa.md`를 함께 읽는다.

JPA specification, Hibernate version, Spring Boot dependency management를
서로 같은 것으로 취급하지 않는다.

## 스키마 소유권

- 운영 스키마는 Flyway, Liquibase 같은 승인된 migration으로 변경한다.
- ORM schema auto-update를 운영 migration으로 사용하지 않는다.
- 가능하면 운영 시작 시 schema validation을 사용한다.
- annotation의 `nullable`, `length`, `unique`만으로 DB가 이미 보장한다고 믿지 않는다.
- entity mapping과 실제 schema metadata를 비교한다.

## 타입 매핑

- `BigDecimal`의 precision과 scale을 DB와 일치시킨다.
- enum 저장 형식과 값 변경 절차를 명시한다.
- temporal 타입은 DB timezone 의미와 Java 타입을 함께 검토한다.
- UUID 생성 위치와 column 타입을 확인한다.
- converter와 custom type이 정렬, 비교, query 조건에 미치는 영향을 본다.

## 식별자와 Entity 동등성

- generated ID가 할당되기 전후의 `equals`와 `hashCode` 동작을 검토한다.
- mutable 필드를 hash key로 사용하지 않는다.
- detached entity를 새 entity처럼 저장하지 않는다.
- `persist`, `merge`, managed, detached 상태의 차이를 확인한다.

## 연관관계

- fetch 기본값에 의존하지 말고 조회 요구를 명시한다.
- 양방향 관계의 owning side와 동기화 코드를 확인한다.
- `CascadeType.ALL`을 aggregate 경계 없이 사용하지 않는다.
- `REMOVE`와 `orphanRemoval`이 실제 데이터 수명과 맞는지 확인한다.
- many-to-many는 연결 entity가 필요한지 검토한다.
- entity를 API 응답으로 직접 직렬화하지 않는다.

## Fetch와 N+1

- 테스트에서 실제 SQL과 query 수를 확인한다.
- fetch join, entity graph, batch fetch, projection 중 목적에 맞게 선택한다.
- collection fetch join과 pagination 조합의 메모리 및 SQL 동작을 확인한다.
- 여러 bag 또는 큰 collection을 한 번에 fetch하지 않는다.
- Open Session in View에 성능과 transaction 책임을 숨기지 않는다.

## Flush와 Bulk DML

flush는 commit에서만 일어난다고 가정하지 않는다.
query 실행 전 flush될 수 있는 조건을 확인한다.

JPQL, HQL, native bulk UPDATE와 DELETE는 persistence context의 entity 상태와
자동으로 동기화되지 않을 수 있다.

bulk 작업 후에는 다음을 검토한다.

- flush 시점
- persistence context clear 또는 refresh
- version과 audit 필드 처리
- 2차 cache 무효화
- 영향받은 행 수 검증

## Batch

- JDBC batching 설정과 실제 driver 지원을 확인한다.
- ID 생성 전략이 insert batching에 미치는 영향을 측정한다.
- 큰 batch에서는 주기적인 flush와 clear를 검토한다.
- persistence context에 모든 entity를 쌓아두지 않는다.
- ordering 옵션이 deadlock과 batching에 미치는 영향을 검증한다.

## Locking

- 낙관적 잠금에는 `@Version`과 충돌 처리를 사용한다.
- version 충돌 후 무조건 같은 entity를 재저장하지 않는다.
- 비관적 잠금은 transaction 경계와 생성 SQL을 확인한다.
- lock timeout hint가 DB와 dialect에서 어떻게 변환되는지 확인한다.
- ORM lock mode 이름만으로 DB row lock 동작을 단정하지 않는다.

## Cache

- 1차 cache는 transaction 안의 identity map으로 이해한다.
- 2차 cache와 query cache는 일관성, 무효화, hit rate 근거가 있을 때만 사용한다.
- 외부 SQL 또는 다른 서비스가 데이터를 바꾸면 cache 일관성을 검토한다.

## 검증

- 대상 DBMS와 버전에 가까운 통합 테스트를 사용한다.
- 생성 SQL과 bind parameter 타입을 확인한다.
- query 수와 반환 행 수를 확인한다.
- schema validation 결과를 확인한다.
- 낙관적 및 비관적 잠금은 두 transaction으로 검증한다.
- bulk DML 후 persistence context 상태를 검증한다.

ORM 테스트 통과와 DB migration 성공을 서로 대신하지 않는다.
