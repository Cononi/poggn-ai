---
name: safe-database-engineering
description: 관계형 DB의 스키마, SQL, 트랜잭션, 마이그레이션을 안전하게 설계하고 검증한다. ORM은 확인된 기술의 별도 참조만 읽는다.
metadata:
  version: "1.0"
---

# Safe Database Engineering

## 목적

데이터 무결성, 호환성, 복구 가능성을 지키면서 데이터베이스 변경을 수행한다.

ORM은 데이터베이스를 대신하는 진실의 원천이 아니다.
DB 제약조건과 실제 SQL 동작을 먼저 확인하고 ORM 매핑을 그에 맞춘다.

## 사용 시점

다음 작업에서 이 스킬을 사용한다.

- 테이블, 컬럼, 타입, 키, 제약조건, 인덱스 변경
- SQL 작성, 쿼리 튜닝, 실행 계획 검토
- 트랜잭션, 격리 수준, 잠금, 동시성 문제 해결
- 데이터 마이그레이션, backfill, 정리, 보존 정책 변경
- ORM 매핑이 스키마 또는 실제 SQL에 영향을 주는 변경
- 운영 데이터 점검 또는 변경 계획 수립

단순 애플리케이션 로직 변경으로 DB 계약이 바뀌지 않으면
저장소의 일반 개발 스킬을 우선한다.

## 책임 경계

이 스킬은 다음을 결정한다.

- 데이터 불변조건과 DB 제약조건
- 스키마와 SQL의 실제 의미
- 트랜잭션과 동시성 전략
- 마이그레이션, 검증, 복구 전략
- 운영 위험과 관측 항목

ORM 참조는 다음만 결정한다.

- 객체와 테이블의 매핑
- fetch, cascade, flush, dirty checking 동작
- ORM이 생성하는 SQL과 프레임워크별 함정
- ORM API로 DB 전략을 표현하는 방법

DB와 ORM의 설명이 충돌하면 실제 DB 버전의 동작을 다시 확인한다.
ORM이 생성한 SQL을 보지 않고 성능과 잠금 동작을 단정하지 않는다.

## 파일 로딩 원칙

먼저 이 파일만 읽는다.
작업에 필요한 참조만 한 단계 추가로 읽는다.

### 공통 참조

- 모델과 제약조건: [schema-design](references/schema-design.md)
- 스키마 또는 데이터 변경: [migration-safety](references/migration-safety.md)
- 트랜잭션과 잠금: [transactions-concurrency](references/transactions-concurrency.md)
- SQL과 인덱스: [query-performance](references/query-performance.md)
- 운영, 보안, 복구: [operations-security](references/operations-security.md)

### DB 엔진 참조

- PostgreSQL 증거가 있을 때:
  [engine-postgresql](references/engine-postgresql.md)
- MySQL 또는 MariaDB 증거가 있을 때:
  [engine-mysql](references/engine-mysql.md)

엔진이 확인되지 않으면 엔진별 문법이나 잠금 특성을 추측하지 않는다.

### 마이그레이션 도구 참조

- Flyway가 확인될 때:
  [migration-flyway](references/migration-flyway.md)
- Liquibase가 확인될 때:
  [migration-liquibase](references/migration-liquibase.md)

### 데이터 접근 기술 참조

- JPA 또는 Hibernate가 확인될 때:
  [orm-jpa-hibernate](references/orm-jpa-hibernate.md)
- Spring Data JPA가 확인될 때:
  위 문서와
  [orm-spring-data-jpa](references/orm-spring-data-jpa.md)를 함께 읽는다.
- Prisma ORM이 확인될 때:
  [orm-prisma](references/orm-prisma.md)
- SQLAlchemy ORM이 확인될 때:
  [orm-sqlalchemy](references/orm-sqlalchemy.md)
- Entity Framework Core가 확인될 때:
  [orm-ef-core](references/orm-ef-core.md)
- Django ORM이 확인될 때:
  [orm-django](references/orm-django.md)
- TypeORM이 확인될 때:
  [orm-typeorm](references/orm-typeorm.md)
- MyBatis가 확인될 때:
  [orm-mybatis](references/orm-mybatis.md)
- JDBC 또는 jOOQ가 확인될 때:
  [data-access-jdbc-jooq](references/data-access-jdbc-jooq.md)

모든 ORM 참조를 한꺼번에 읽지 않는다.
의존성, 설정 또는 실제 소스가 확인된 기술만 선택한다.

## 스택 확인

변경 전에 저장소에서 다음 증거를 찾는다.

1. DBMS 종류와 실제 버전
2. 스키마 변경 도구와 적용 이력
3. ORM 또는 SQL 접근 기술과 버전
4. 스키마, migration, entity, mapper의 소유 위치
5. 테스트 DB와 운영 DB의 차이
6. 대상 테이블의 규모, 트래픽, 쓰기 경합
7. 배포 방식과 구버전 애플리케이션의 공존 여부
8. 백업, 복구, 모니터링 방법

선택적으로 다음 읽기 전용 도구를 실행할 수 있다.

```bash
python3 scripts/detect_db_stack.py .
```

탐지 결과는 후보일 뿐이다.
lockfile, 빌드 설정, 런타임 설정 또는 실제 연결 정보로 확인한다.

확인하지 못한 항목은 다음처럼 표시한다.

```text
[UNKNOWN] 운영 PostgreSQL 정확한 minor version
[ASSUMPTION] 배포 중 구버전과 신버전이 10분간 공존
[OPEN] backfill 허용 처리량
```

## 실행 권한 단계

### DESIGN

저장소와 제공된 자료만 분석한다.
DB에 연결하거나 데이터를 변경하지 않는다.
명시되지 않은 경우 기본 단계다.

### LOCAL

사용자가 구현 또는 검증을 요청한 경우 로컬 또는 일회성 테스트 DB만 사용한다.
대상과 연결 문자열이 로컬인지 확인한다.

### SHARED

공용 개발 또는 staging DB 작업이다.
정확한 환경과 변경 범위를 사용자가 요청했을 때만 수행한다.
다른 사용자의 데이터와 실행 중인 테스트를 고려한다.

### PRODUCTION

운영 DB의 조회 또는 변경이다.
정확한 대상, 명령, 영향, 중단 조건, 복구 방법이 확인되어야 한다.
운영 쓰기와 파괴적 작업은 사용자의 명시적 요청 없이 수행하지 않는다.

연결 대상이 불명확하면 쓰기 작업을 실행하지 않는다.

## 위험 등급

### D0: 분석

- 스키마와 SQL 읽기
- 정적 검토
- 안전한 테스트 환경에서의 실행 계획 확인

### D1: 추가형 변경

- 새 테이블 또는 호환 가능한 컬럼 추가
- 기존 동작을 깨뜨리지 않는 제약조건 준비
- 위험이 확인된 인덱스 추가

추가형 변경도 큰 테이블에서는 잠금과 I/O 위험이 있을 수 있다.
규모와 엔진 동작을 모르면 D2 이상으로 올린다.

### D2: 단계형 변경

- backfill
- NOT NULL, UNIQUE, FK, CHECK 강화
- 컬럼 이름 또는 타입 전환
- 읽기 또는 쓰기 경로 변경
- 배포 버전 간 호환성 관리

`expand → migrate → switch → contract` 단계를 기본으로 한다.

### D3: 고위험 변경

- DROP, TRUNCATE, 대량 DELETE 또는 UPDATE
- 대규모 테이블 재작성 또는 장시간 잠금 가능 작업
- 결제, 인증, 권한, 개인정보, 회계 데이터 변경
- 샤딩, 파티셔닝, 소유권 또는 격리 수준 변경
- 운영 데이터 직접 수정

D3는 별도 실행 계획, 중단 조건, 복구 증거가 없으면 실행하지 않는다.

## 작업 절차

### 1. 현재 상태 확인

다음을 직접 읽고 근거 경로를 기록한다.

- migration과 현재 스키마 정의
- 관련 SQL, repository, mapper, entity
- 데이터베이스 설정과 버전 고정 파일
- 테스트와 배포 파이프라인
- 최근 관련 변경 이력

문서와 코드가 다르면 어느 것이 실제 배포 경로인지 확인한다.

### 2. 불변조건과 접근 패턴 정의

코드 작성 전에 다음을 명시한다.

- 데이터 소유자와 생명주기
- 기본키, 자연키, 중복 허용 여부
- NULL, 기본값, 범위, 상태 전이
- 참조 무결성과 삭제 규칙
- 주요 읽기 및 쓰기 쿼리
- 예상 cardinality와 결과 상한
- 동시 쓰기와 충돌 가능성
- 보존 기간, 개인정보, 감사 요구사항

가능한 불변조건은 애플리케이션 검증만 두지 말고
DB 제약조건으로도 표현한다.

### 3. 변경 계약 작성

D1 이상의 변경은 다음 템플릿을 사용한다.

- [database-change-spec-template](assets/database-change-spec-template.md)

최소한 다음을 포함한다.

- 현재 상태와 목표 상태
- 스키마 및 SQL 변경
- 구버전과 신버전 호환성
- migration과 backfill 단계
- 트랜잭션과 잠금 영향
- ORM 또는 data-access 영향
- 검증, 관측, 복구 방법

### 4. 마이그레이션 설계

- 이미 적용된 migration은 수정하지 않는다.
- rolling deployment에서 양쪽 앱 버전이 동작하도록 설계한다.
- 파괴적 변경은 별도 contract 단계로 미룬다.
- backfill은 작게 나누고 재시작 가능하며 멱등적으로 만든다.
- 각 단계에 사전조건, 완료조건, 중단조건을 둔다.
- rollback이 실제로 안전하지 않으면 roll-forward 계획을 작성한다.
- DDL의 transaction과 lock 특성은 엔진과 버전별로 확인한다.

운영 실행에는 다음 템플릿을 사용한다.

- [migration-runbook-template](assets/migration-runbook-template.md)

### 5. 구현

스키마의 원본은 승인된 migration으로 관리한다.
ORM auto-DDL을 운영 migration으로 사용하지 않는다.

구현 순서는 보통 다음과 같다.

1. 호환 가능한 스키마 확장
2. 애플리케이션의 호환 읽기와 쓰기
3. 점진적 backfill
4. 새 경로로 전환
5. 제약조건 강화
6. 사용하지 않는 스키마 제거

실제 상황에 맞지 않으면 순서를 바꾸고 이유를 기록한다.

### 6. 검증

가능한 범위에서 다음을 검증한다.

- 빈 스키마에서 전체 migration 적용
- 실제 기준 버전에서 최신 버전으로 upgrade
- 대상 DB 엔진과 호환되는 통합 테스트
- 제약조건의 성공 및 실패 사례
- 대표 데이터 분포에서 실행 계획과 결과 상한
- 두 개 이상의 연결을 사용한 동시성 시나리오
- backfill 재실행, 중단, 재개
- 구버전과 신버전 앱의 스키마 호환성
- D2와 D3의 복구 또는 roll-forward 절차

H2 통과만으로 PostgreSQL 또는 MySQL 동작을 증명하지 않는다.

검증 결과는 다음 네 상태만 사용한다.

```text
PASS | FAILED | PARTIAL | NOT RUN
```

`PASS`에는 명령, 대상 환경, DB 버전, 핵심 결과를 기록한다.
실행하지 않은 검증을 통과했다고 쓰지 않는다.

### 7. 운영 준비

D2와 D3에서는 최소한 다음을 준비한다.

- 예상 영향과 관찰할 지표
- lock, latency, error, replication lag 관측
- batch 크기와 throttle 방법
- 중단 기준과 담당자
- 백업 또는 복구 가능한 기준점
- 적용 후 데이터 검증 쿼리
- 다음 배포 단계와 contract 시점

## 절대 안전 규칙

- 대상을 확인하지 않은 DB에 쓰지 않는다.
- 운영 credential, secret, 개인키를 출력하거나 저장하지 않는다.
- 사용자 요청 없이 운영 데이터를 조회하거나 변경하지 않는다.
- `DROP`, `TRUNCATE`, `CASCADE`, 전체 테이블 DML을 자동 실행하지 않는다.
- `UPDATE` 또는 `DELETE`의 범위가 불명확하면 실행하지 않는다.
- FK나 제약조건을 끄는 방식으로 실패를 숨기지 않는다.
- 적용된 migration의 checksum을 맞추려고 내용을 몰래 바꾸지 않는다.
- migration 실패를 도구의 repair 기능으로 자동 은폐하지 않는다.
- SQL 문자열에 외부 입력을 연결하지 않는다.
- 실데이터나 개인정보를 테스트 fixture와 로그에 복사하지 않는다.
- DB 버전과 데이터 규모를 모른 채 무중단이라고 단정하지 않는다.
- 실행하지 않은 backup, restore, migration, test를 성공으로 보고하지 않는다.

## 완료 조건

다음을 모두 만족해야 완료로 판정한다.

1. DBMS, 버전, migration 도구, 접근 기술의 증거가 기록되었다.
2. 불변조건과 주요 접근 패턴이 명확하다.
3. 스키마와 애플리케이션 호환성이 설명된다.
4. migration, backfill, contract 단계가 필요한 만큼 분리되었다.
5. 트랜잭션, 잠금, 재시도, 멱등성이 검토되었다.
6. 실제 엔진에서 필요한 검증을 실행했거나 `NOT RUN`으로 기록했다.
7. 데이터 손실과 운영 위험에 대한 복구 또는 roll-forward가 있다.
8. ORM을 사용한다면 해당 참조와 생성 SQL을 검토했다.
9. 차단되는 `[OPEN]` 항목이 없다.

## 최종 보고 형식

```md
## 데이터베이스 변경

- Mode: DESIGN | LOCAL | SHARED | PRODUCTION
- Risk: D0 | D1 | D2 | D3
- DBMS: `<name and version> | UNKNOWN`
- Migration: `<tool and version> | none | UNKNOWN`
- Data access: `<technology and version> | UNKNOWN`
- Change: 변경 요약

## 무결성과 호환성

- Invariants: 추가 또는 변경된 불변조건
- Compatibility: 구버전과 신버전의 공존 여부
- Recovery: rollback 또는 roll-forward 방법

## 검증

- `<command or check>`: PASS | FAILED | PARTIAL | NOT RUN

## 남은 위험

- 미실행 검증, 운영 조건, 열린 결정
```
