# Migration Safety

## 원칙

migration은 파일 생성이 아니라 배포 중인 여러 버전과 데이터를
안전하게 한 상태에서 다른 상태로 옮기는 절차다.

엔진, 버전, 테이블 크기, 트래픽을 모르면 무중단이라고 말하지 않는다.

## 기본 단계

```text
expand → migrate → switch → contract
```

### Expand

구버전 애플리케이션이 계속 동작할 수 있는 스키마를 추가한다.
기존 컬럼이나 계약을 즉시 제거하거나 의미를 바꾸지 않는다.

### Migrate

기존 데이터를 새 표현으로 옮긴다.
backfill은 작은 batch, checkpoint, throttle, 재시작 가능성을 갖춘다.

### Switch

읽기와 쓰기를 새 경로로 전환한다.
필요하면 dual-read 또는 dual-write 기간을 두되 불일치 처리 규칙을 둔다.

### Contract

구버전이 더 이상 존재하지 않고 데이터 검증이 끝난 후
사용하지 않는 컬럼, 인덱스, 호환 코드를 제거한다.

## 호환성 행렬

각 단계에서 다음 조합을 검토한다.

| Application | Old schema | Expanded schema | Contracted schema |
|---|---:|---:|---:|
| Old version | 지원 여부 | 지원 여부 | 보통 미지원 |
| New version | 지원 여부 | 지원 여부 | 지원 여부 |

실제 배포 전략에 필요 없는 조합은 이유를 기록하고 제외한다.

## 변경 유형별 검토

### 새 컬럼

- 기존 행의 값과 의미를 정한다.
- nullable 상태로 먼저 추가할지 검토한다.
- DB default와 애플리케이션 default의 차이를 확인한다.
- 큰 테이블에서 table rewrite와 lock 가능성을 엔진별로 확인한다.

### NOT NULL

- 기존 NULL 수를 측정한다.
- 새 쓰기에서 NULL을 먼저 차단한다.
- backfill 후 검증한다.
- 엔진이 제공하는 점진적 검증 방법을 확인한다.

### UNIQUE

- 중복을 먼저 탐지하고 해결 규칙을 정한다.
- 동시 쓰기가 새 중복을 만들지 못하게 전환 순서를 설계한다.
- 인덱스 생성 방식과 잠금 영향을 확인한다.

### FOREIGN KEY

- orphan 행을 탐지한다.
- 삭제와 갱신 동작을 결정한다.
- 검증 시 테이블 스캔과 잠금 영향을 확인한다.
- application-level relation만 있던 경우 오류 처리 변화를 검토한다.

### 컬럼 이름 변경

한 번의 rename으로 끝내지 않는다.

1. 새 컬럼 추가
2. 새 쓰기 또는 dual-write
3. 기존 데이터 backfill
4. 읽기 전환
5. 구버전 제거 확인
6. 이전 컬럼 제거

DB view나 compatibility layer가 더 안전한지 검토한다.

### 타입 변경

- 값 범위와 손실 가능성을 측정한다.
- 정렬, 비교, collation, timezone 의미 변화를 확인한다.
- 큰 테이블 재작성 여부를 확인한다.
- 새 컬럼으로 복사 후 전환하는 방식을 우선 검토한다.

### 인덱스

- 생성 방식의 lock과 transaction 제약을 확인한다.
- 실패 후 남는 중간 객체를 확인한다.
- 쓰기 증폭과 디스크 여유를 확인한다.
- 사용 여부를 관측한 후 중복 인덱스를 제거한다.

## Backfill 계약

backfill은 다음 속성을 가져야 한다.

- 대상 범위가 명확하다.
- 같은 batch를 다시 실행해도 안전하다.
- 안정적인 정렬 키와 checkpoint가 있다.
- 한 transaction이 과도하게 크지 않다.
- batch 크기와 sleep을 조정할 수 있다.
- lock, latency, replica lag에 중단 기준이 있다.
- 변경된 행 수와 남은 행 수를 측정한다.
- 애플리케이션의 동시 쓰기와 충돌하지 않는다.

`OFFSET` 기반 batch는 변경 중인 데이터에서 누락과 중복 가능성을 검토한다.
가능하면 안정적인 key range 또는 처리 상태를 사용한다.

## Rollback과 Roll-forward

DDL과 데이터 변환은 항상 완전한 rollback이 가능한 것이 아니다.

각 단계에 다음 중 하나를 명시한다.

- 안전한 rollback
- 애플리케이션 feature flag로 되돌림
- 이전 읽기 경로 유지
- 보정 migration을 통한 roll-forward
- backup 또는 point-in-time recovery

되돌리면 새 데이터가 손실되는 경우 rollback이라고 부르지 않는다.

## Migration 검증

- 현재 운영 기준 schema에서 upgrade한다.
- 빈 schema에서도 전체 이력을 적용한다.
- 반복 적용 또는 재시작 동작을 확인한다.
- 예상 객체, constraint, index를 metadata로 확인한다.
- 데이터 수, NULL, 중복, orphan을 전후 비교한다.
- 잠금과 실행 시간을 운영과 유사한 규모에서 관찰한다.
- 구버전과 신버전 애플리케이션의 호환성을 확인한다.

## 금지되는 지름길

- 적용된 migration 파일 수정
- checksum 오류를 이유 없이 repair
- 운영에서 최초 시험 실행
- 검증 없이 NOT NULL, UNIQUE, FK 즉시 적용
- 대량 DML을 한 transaction으로 실행
- backup 존재만 확인하고 restore 가능성을 추측
- 실패한 migration을 수동 수정 후 성공으로 기록
