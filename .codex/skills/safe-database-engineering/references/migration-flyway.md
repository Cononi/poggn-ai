# Flyway Adapter

## 활성화 조건

Flyway dependency, 설정 또는 migration directory가 확인될 때만 사용한다.
정확한 Flyway edition과 version을 확인한다.

## Migration 소유권

- 적용된 versioned migration은 수정하지 않는다.
- 새 변경은 새 migration으로 추가한다.
- repeatable migration의 재실행 조건과 의도를 기록한다.
- migration 이름, version 순서, location을 저장소 규칙에 맞춘다.
- out-of-order 허용 여부를 임의로 바꾸지 않는다.

## Validate와 Checksum

- 배포 전에 validate를 실행한다.
- checksum 불일치 원인을 먼저 조사한다.
- repair는 실패를 지우는 일반 해결책이 아니다.
- repair가 metadata를 어떻게 바꾸는지 확인하고 명시적 승인 후 수행한다.
- 이미 여러 환경에 적용된 파일을 포맷 정리 목적으로 수정하지 않는다.

## Transaction

migration 전체 또는 statement별 transaction 지원은 DBMS와 문장에 따라 다르다.

- 대상 DBMS에서 DDL transaction 지원을 확인한다.
- transaction 밖에서 실행해야 하는 문장이 있는지 확인한다.
- 일부 성공 후 실패했을 때 남는 객체와 복구 절차를 작성한다.
- 한 migration에 서로 다른 위험 단계의 작업을 과도하게 묶지 않는다.

## Baseline과 Clean

- 기존 DB의 baseline version과 실제 schema 일치를 확인한다.
- baseline은 과거 변경을 검증했다는 의미가 아니다.
- `clean`은 데이터와 객체를 제거할 수 있으므로 공유 또는 운영 환경에서 금지한다.
- clean 설정을 자동으로 활성화하지 않는다.

## 운영 절차

- info와 validate로 현재 상태를 확인한다.
- 대상 environment와 schema를 재확인한다.
- migration 전후 schema와 데이터 검증을 실행한다.
- 실패 시 metadata, 실제 객체, application 상태를 함께 확인한다.
- 성공하지 않은 migrate를 완료로 보고하지 않는다.
