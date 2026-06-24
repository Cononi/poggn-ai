# Operations, Security, and Recovery

## 권한

- 애플리케이션 계정과 migration 계정을 분리한다.
- runtime 계정에 불필요한 DDL 권한을 주지 않는다.
- 읽기 전용 점검은 가능한 읽기 전용 credential을 사용한다.
- 관리자 계정을 애플리케이션 설정에 넣지 않는다.
- 사람과 자동화의 변경 이력을 남긴다.

## Secret

- 연결 문자열, 비밀번호, token을 코드와 migration에 기록하지 않는다.
- 명령 출력과 로그에서 credential을 마스킹한다.
- 예제에는 실제 host, user, database 이름을 복사하지 않는다.
- secret rotation 시 connection pool과 배포 순서를 고려한다.

## 개인정보

- query log와 error log에 원문 개인정보를 남기지 않는다.
- 비운영 환경에는 마스킹 또는 합성 데이터를 사용한다.
- dump 파일의 보관, 암호화, 접근, 삭제 정책을 둔다.
- 삭제 요청은 replica, backup, cache, search index 범위를 함께 검토한다.
- 암호화 키와 암호화된 데이터의 수명주기를 분리한다.

## Backup과 복구

backup 성공 메시지만으로 복구 가능성을 증명하지 않는다.

다음을 확인한다.

- backup 범위와 주기
- 보존 기간
- 암호화와 접근 통제
- point-in-time recovery 가능 여부
- 최근 restore drill 결과
- RPO와 RTO
- schema와 application version의 대응
- migration 중 필요한 복구 기준점

파괴적 작업 전에 복구 방법과 데이터 손실 범위를 명시한다.

## Connection Pool

- pool 크기를 DB connection 한도와 서비스 인스턴스 수로 계산한다.
- timeout 종류를 구분한다.
  - connection acquisition
  - connect
  - statement
  - lock
  - transaction
- 긴 transaction과 connection leak을 관측한다.
- retry 폭주가 pool 고갈을 악화하지 않게 한다.
- read replica 사용 시 replication lag와 read-after-write 요구를 확인한다.

## 관측성

최소한 다음을 관찰할 수 있어야 한다.

- query latency와 error rate
- active, idle, waiting connection
- lock wait와 deadlock
- long-running transaction
- replication lag
- storage와 transaction log 증가
- cache hit와 I/O
- migration 진행률과 처리 행 수

민감한 bind 값을 그대로 수집하지 않는다.

## 운영 변경 중단 조건

실행 전에 수치 또는 명확한 사건으로 중단 조건을 정한다.

예시:

- lock wait가 허용 기준을 초과
- p95 latency가 기준선보다 크게 증가
- error rate 증가
- replica lag 증가
- disk 또는 transaction log 여유 부족
- 예상 대상 행 수와 실제 행 수 불일치
- migration checksum 또는 schema 사전조건 불일치

중단 후 재개 조건과 담당자를 함께 기록한다.

## 장애 대응

- 변경을 멈춘다.
- 현재 transaction과 migration 상태를 확인한다.
- 추가 손상을 막고 증거를 보존한다.
- rollback과 roll-forward 중 데이터 손실이 적은 방법을 선택한다.
- 실패 원인과 실제 실행 명령을 기록한다.
- 검증 없이 같은 명령을 반복 실행하지 않는다.

복구되지 않은 상태를 성공 또는 완료로 보고하지 않는다.
