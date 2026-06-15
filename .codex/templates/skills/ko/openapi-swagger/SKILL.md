---
name: openapi-swagger
description: OpenAPI/Swagger 문서와 REST API 계약 검증에 사용합니다.
---

# openapi-swagger

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- spec은 구현과 동기화되어야 합니다.
- operationId는 안정적이고 중복 없이 둡니다.
- auth scheme과 security requirement를 endpoint마다 명시합니다.

## Procedure

- required, nullable, default, example을 validation과 맞춥니다.
- error response는 공통 shape와 status를 포함합니다.
- pagination, sorting, filtering parameter를 문서화합니다.
- breaking change는 version note나 migration note를 남깁니다.

## Expert Rules

- OpenAPI는 홍보 문서가 아니라 client generation contract입니다.
- operationId는 SDK 메서드명이 되므로 안정성과 중복을 검증합니다.
- security requirement는 global default보다 endpoint override를 우선 확인합니다.
- oneOf/anyOf는 client 언어의 type 표현 가능성까지 고려합니다.
- example은 validation과 실제 error shape를 통과해야 합니다.
- deprecated field는 제거일과 대체 field를 함께 문서화합니다.
- oneOf, allOf, enum, date-time의 client 생성 결과를 확인합니다.
- path, query, header parameter의 required/default drift를 차단합니다.

## Expert Checks

- 문서에만 있고 구현 없는 endpoint가 있는지 봅니다.
- 구현됐지만 spec에 없는 endpoint가 있는지 봅니다.
- generated client compatibility를 확인합니다.

## Failure Modes

- spec에는 있지만 controller가 없는 endpoint가 있는 상태.
- required/nullable이 Bean Validation이나 TS type과 어긋나는 상태.
- error response가 실제 exception handler와 다른 상태.
- generated client가 breaking change를 감지하지 못하는 상태.
- binary upload/download나 streaming content type이 명시되지 않은 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- auth requirement 누락.
- internal entity schema 노출.
- implementation/spec drift.

## Verify

- OpenAPI validation.
- contract test.
- generated client compile if available.

## Evidence

- spec validation과 implementation diff를 확인했습니다.
- protected endpoint의 security requirement가 명시됩니다.
- generated client 또는 contract test 결과가 있습니다.
- error schema를 실제 handler의 code, message, fieldErrors와 대조합니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
