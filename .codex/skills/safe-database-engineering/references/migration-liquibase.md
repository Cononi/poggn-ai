# Liquibase Adapter

## 활성화 조건

Liquibase dependency, 설정 또는 changelog가 확인될 때만 사용한다.
정확한 Liquibase version을 확인한다.

## Changeset 정체성

changeset은 보통 id, author, file path 조합으로 식별된다.
저장소의 include 구조와 경로 변경 영향을 확인한다.

- 적용된 changeset을 임의 수정하지 않는다.
- 새 변경은 새 changeset으로 추가한다.
- logical file path를 사용하는 경우 규칙을 유지한다.
- checksum 오류를 `clearCheckSums`로 자동 숨기지 않는다.

## Preconditions

precondition은 기대한 시작 상태를 확인하는 데 사용한다.

- table, column, index 존재 여부
- DBMS 또는 version 조건
- 데이터 사전조건
- 이미 적용된 수동 변경 여부

실패 동작이 HALT, WARN, MARK_RAN 중 무엇인지 의도적으로 선택한다.
`MARK_RAN`으로 실제 미적용 변경을 성공처럼 보이게 하지 않는다.

## Rollback

자동 rollback 지원 여부를 change type별로 확인한다.

- 데이터 손실이 있는 rollback을 안전하다고 부르지 않는다.
- custom SQL에는 명시적 rollback 또는 roll-forward 계획을 둔다.
- rollback SQL을 실제 테스트 DB에서 검증한다.
- tag와 배포 버전의 대응을 기록한다.

## Context와 Label

- environment별 차이를 context와 label로 숨기지 않는다.
- 어떤 changeset이 어느 환경에 적용되는지 명확히 한다.
- 운영에서 누락된 context가 없는지 update 전 확인한다.
- 같은 schema가 환경마다 다른 이력을 갖지 않게 관리한다.

## 검증과 미리보기

- changelog validation을 실행한다.
- SQL preview를 검토하되 실제 적용 성공으로 간주하지 않는다.
- 대상 DBMS에서 update를 검증한다.
- database changelog lock 상태를 확인한다.
- 실패 후 실제 schema와 changelog table 상태를 함께 확인한다.
