# Spring Data JPA Adapter

## 전제

이 문서는 Spring Data JPA가 실제로 확인된 경우에만 읽는다.
먼저 `references/orm-jpa-hibernate.md`도 읽는다.

정확한 Spring Data JPA와 Spring Framework 버전을 확인한다.
repository 추상화가 JPA와 DB의 transaction 의미를 바꾸지는 않는다.

## Transaction 경계

- 여러 repository를 묶는 unit of work는 service 계층에서 정의한다.
- repository method의 기본 transaction 속성을 버전별 문서에서 확인한다.
- 선언한 query method에 transaction이 자동 적용된다고 가정하지 않는다.
- `readOnly=true`를 쓰기 금지 보안 장치로 취급하지 않는다.
- self-invocation과 proxy 경계를 확인한다.
- checked exception의 rollback 규칙을 확인한다.

## `save` 의미

`save`가 항상 INSERT라고 가정하지 않는다.
entity의 신규 판정과 provider의 `persist` 또는 `merge` 선택을 확인한다.

- managed entity는 dirty checking 대상이다.
- 수동 ID와 version 값이 신규 판정에 미치는 영향을 확인한다.
- detached graph의 merge가 의도하지 않은 갱신을 만들 수 있다.
- batch insert에서 불필요한 `saveAndFlush`를 반복하지 않는다.

## Query Method

- derived query 이름이 길고 불명확하면 명시적 query를 사용한다.
- property 경로 변경이 런타임 query 생성에 미치는 영향을 테스트한다.
- nullable parameter와 빈 collection의 의미를 명시한다.
- native query는 DBMS 종속성과 count query를 함께 관리한다.
- pagination의 count query 비용을 별도로 확인한다.

## Projection과 Fetch

- 읽기 전용 화면은 필요한 컬럼만 반환하는 projection을 검토한다.
- interface, class, record projection의 생성 SQL을 확인한다.
- `@EntityGraph`가 필요한 association만 가져오는지 확인한다.
- projection이 lazy load를 완전히 제거했다고 추측하지 않는다.
- collection fetch와 pageable 조합을 실제 SQL로 검증한다.

## Modifying Query

`@Modifying` query는 다음을 검토한다.

- 명시적 transaction
- flush 시점
- persistence context clear 여부
- version과 audit 필드
- 영향받은 행 수
- cache 무효화

이미 load된 entity가 stale 상태로 남을 수 있다.

## Lock

- `@Lock`은 transaction 안에서 사용한다.
- 실제 dialect가 생성하는 SQL을 확인한다.
- timeout hint와 exception 변환을 버전별로 확인한다.
- lock이 필요 없는 조회에 습관적으로 적용하지 않는다.

## Repository 테스트

- slice test만으로 운영 DB 차이를 숨기지 않는다.
- 대상 DB container를 사용한 통합 테스트를 둔다.
- query count, SQL shape, pagination, locking을 검증한다.
- schema migration을 적용한 DB에서 repository 테스트를 실행한다.
- H2 compatibility mode를 운영 DB의 증거로 사용하지 않는다.
