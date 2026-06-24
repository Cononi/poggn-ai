# MyBatis Adapter

## 활성화 조건

MyBatis dependency, configuration, mapper interface 또는 mapper XML이
명확히 확인될 때만 이 문서를 읽는다.

MyBatis는 SQL을 숨기는 ORM으로 가정하지 않는다.
SQL과 result mapping의 책임이 애플리케이션에 있다.

## Parameter 안전

- 값에는 `#{...}` bind parameter를 사용한다.
- `${...}`는 문자열 치환이므로 외부 입력에 사용하지 않는다.
- table, column, order 방향은 allowlist로 변환한다.
- LIKE escape와 wildcard 정책을 정한다.
- IN 목록은 빈 값과 최대 크기를 처리한다.

## Dynamic SQL

- 조건이 모두 빠져 전체 UPDATE 또는 DELETE가 되지 않게 한다.
- `<where>`, `<set>`, trim 동작을 테스트한다.
- 선택적 필드 업데이트에서 NULL의 의미를 구분한다.
- 재사용 SQL fragment가 문맥에 맞는 alias를 사용하는지 확인한다.
- 복잡한 동적 SQL은 생성된 최종 SQL을 테스트한다.

## Result Mapping

- 명시적인 `resultMap`으로 column과 property 관계를 관리한다.
- 자동 매핑의 underscore와 case 규칙을 확인한다.
- join 결과의 중복 행과 nested collection 조립을 검증한다.
- nullable column과 primitive 타입의 차이를 확인한다.
- constructor mapping과 record 지원을 버전별로 확인한다.

## Transaction

- Spring transaction과 `SqlSession` 수명주기를 확인한다.
- mapper 호출마다 별도 transaction이라고 가정하지 않는다.
- batch executor의 flush와 오류 위치를 확인한다.
- generated key 반환 방식이 DBMS와 driver에서 동작하는지 확인한다.
- cursor 또는 streaming 조회 중 connection 수명을 관리한다.

## Cache

- local cache scope를 확인한다.
- 2차 cache는 명시적으로 일관성 전략을 정한 경우에만 사용한다.
- 외부 SQL과 다른 mapper namespace가 cache를 stale하게 만들 수 있다.
- cache 활성화를 성능 해결책의 기본값으로 사용하지 않는다.

## Pagination과 Batch

- DBMS별 pagination SQL을 확인한다.
- 큰 OFFSET의 비용을 측정한다.
- batch insert와 update의 driver rewrite 지원을 확인한다.
- 한 statement에 지나치게 많은 parameter를 만들지 않는다.
- batch 실패 시 부분 성공과 재시도 단위를 정의한다.

## Migration과 Mapper 동기화

- mapper SQL보다 migration이 먼저 배포되어야 하는지 확인한다.
- expand 단계에서는 구버전 mapper도 동작해야 한다.
- 컬럼 rename은 alias 또는 호환 column 기간을 둔다.
- 제거된 컬럼을 참조하는 mapper를 전체 검색한다.

## 검증

- 실제 DBMS에서 mapper 통합 테스트를 실행한다.
- 생성된 SQL, parameter, 영향 행 수를 확인한다.
- dynamic SQL의 최소, 최대, 빈 조건을 테스트한다.
- concurrency와 lock SQL은 두 transaction으로 검증한다.
- mapper XML parse 성공만으로 SQL 실행 성공을 단정하지 않는다.
