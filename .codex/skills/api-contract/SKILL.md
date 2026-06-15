---
name: api-contract
description: API endpoint, DTO, error, auth, ownership 계약을 고정할 때 사용합니다.
---

# api-contract

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- method, path, request, response, error shape를 먼저 고정합니다.
- endpoint별 auth, owner, role 조건을 명시합니다.
- public contract는 persistence entity와 분리합니다.

## Procedure

- request validation과 nullable 정책을 DTO에 반영합니다.
- list API에는 pagination, sorting, filtering 정책을 둡니다.
- mutation에는 idempotency와 conflict 처리 가능성을 검토합니다.
- breaking change는 migration path와 client 영향 범위를 적습니다.

## Expert Rules

- contract는 controller 구현보다 먼저 테스트 가능한 문장으로 고정합니다.
- resource id는 path, principal, owner query에서 같은 의미여야 합니다.
- nullable은 DB nullable이 아니라 client가 받는 의미로 결정합니다.
- error code는 UI 분기와 운영 로그 검색을 견딜 만큼 안정적이어야 합니다.
- pagination은 cursor/offset 선택과 정렬 안정성을 함께 정합니다.
- mutation은 중복 요청, 경쟁 상태, 재시도 결과를 설명해야 합니다.
- 상태 변경 API는 retry와 idempotency key 정책을 고정합니다.
- 401, 403, 404는 owner 은닉 정책과 함께 결정합니다.

## Expert Checks

- stack trace나 internal enum이 response로 노출되는지 봅니다.
- client가 의존하는 필드 변경에 test가 있는지 봅니다.
- OpenAPI가 있으면 구현과 schema drift를 확인합니다.

## Failure Modes

- entity field가 그대로 response contract가 되는 상태.
- 403과 404 정책이 owner 노출 위험을 고려하지 않은 상태.
- validation 실패가 field 단위로 추적되지 않는 상태.
- client가 의존하는 enum/string 변경이 문서 없이 일어나는 상태.
- request DTO의 unknown field 허용 여부가 계약에 없는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- 권한 조건 없는 state-changing endpoint.
- entity를 API response로 직접 반환.
- 계약 변경에 test나 문서 갱신 없음.

## Verify

- API contract test.
- OpenAPI schema check.
- $codex-quality gate --for-ai.

## Evidence

- endpoint별 authz, request, response, error 예가 있습니다.
- OpenAPI 또는 contract test가 구현과 일치합니다.
- breaking change 여부와 migration note가 기록됩니다.
- list 응답의 stable ordering과 cursor/page 경계 테스트가 있습니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
