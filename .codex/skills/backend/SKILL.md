---
name: backend
description: Backend engineering guidance for APIs, domain logic, validation, persistence, transactions, authorization, error handling, observability, and server-side tests. Use when work touches routes, controllers, services, database access, jobs, queues, integrations, or business rules.
---

# Backend Skill

## 목적

서버 변경을 데이터 무결성, 보안, 계약 안정성, 운영 가능성 기준으로 구현한다. API와 도메인 로직은 확인 가능한 요구사항과 테스트로 닫는다.

## 기본 원칙

- route/controller는 얇게 유지하고 핵심 규칙은 domain/service 계층에 둔다.
- 입력 검증, 권한 확인, 비즈니스 규칙, 저장 동작을 분리해서 확인한다.
- 데이터 변경은 idempotency, transaction, rollback 가능성을 검토한다.
- 외부 API, queue, job, webhook은 재시도와 중복 처리 기준을 명시한다.
- 에러는 호출자가 행동할 수 있는 형태로 반환하고 내부 세부정보를 노출하지 않는다.
- 로그와 metric은 디버깅에 필요한 정보만 남기고 개인정보를 기록하지 않는다.

## 사용 절차

1. 요청의 외부 계약을 확인한다: endpoint, method, payload, response, status code, auth.
2. 도메인 규칙을 확인한다: 허용 상태, 금지 상태, edge case, 실패 동작.
3. 데이터 접근을 확인한다: schema, index, transaction, migration, concurrency.
4. 구현 위치를 정한다: route, service, repository, job, integration boundary.
5. 테스트를 먼저 정한다: unit, integration, contract, migration, authorization.
6. 구현 후 실제 명령으로 검증하고 실패한 검증을 숨기지 않는다.

## API 기준

- 새 API는 입력/출력 타입과 실패 응답을 명확히 정의한다.
- 기존 API 변경은 backward compatibility를 먼저 판단한다.
- pagination, filtering, sorting은 기존 패턴을 따른다.
- validation error와 domain error를 구분한다.
- status code는 의미에 맞게 쓴다: 400 입력 오류, 401 인증, 403 권한, 404 리소스 없음, 409 상태 충돌.

## 데이터 기준

- 쓰기 작업은 transaction 경계를 명시한다.
- unique constraint와 application-level 중복 방지를 같이 검토한다.
- migration은 forward/backward compatibility와 배포 순서를 고려한다.
- 삭제는 soft delete, cascade, audit 필요 여부를 확인한다.
- 대량 작업은 timeout, batch, lock, retry 영향을 확인한다.

## 보안 기준

- 인증된 사용자와 권한 있는 사용자를 구분한다.
- 서버에서 다시 검증한다. 프론트 검증만 믿지 않는다.
- 민감 정보는 response, log, error message에 노출하지 않는다.
- 파일 업로드, URL fetch, webhook, callback은 SSRF/path traversal/replay 위험을 확인한다.

## 테스트 기준

- 비즈니스 규칙은 unit test로 빠르게 고정한다.
- API 계약은 integration 또는 request test로 확인한다.
- 권한, 실패 상태, 경계값을 happy path와 함께 테스트한다.
- DB 변경은 migration 검증과 rollback/compatibility 검토를 남긴다.

## Multi Agent 연결

- API/도메인/데이터 영향 분석이 독립적이면 `pogo-backend-agent`를 사용한다.
- backend agent는 구현 결과를 `pogo-verifier`에 넘길 수 있도록 변경 파일, 실행 명령, 실패/미실행 테스트를 요약한다.
- 프론트 계약이 함께 바뀌면 front agent와 API contract를 먼저 맞춘 뒤 구현한다.

## 완료 체크리스트

- 입력 검증과 권한 검증이 서버에 있는가.
- 성공/실패 응답이 기존 API 스타일과 맞는가.
- 데이터 쓰기 경계와 동시성 위험을 확인했는가.
- 필요한 테스트가 실행되었고 결과가 기록되었는가.
- 로그/에러가 운영에 유용하고 민감 정보를 새지 않는가.
