---
name: frontend-typescript
description: React TS/TSX, typed props, DTO, client 경계를 만들 때 사용합니다.
---

# frontend-typescript

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- 신규 UI는 .tsx, 로직과 client는 .ts를 사용합니다.
- props, DTO, API response, error shape를 명시합니다.
- unknown input은 guard나 parser 뒤 사용합니다.

## Procedure

- nullable과 optional 상태를 UI state model에 반영합니다.
- typed client는 status, error, body parsing을 캡슐화합니다.
- domain type을 component props에 그대로 누출하지 않습니다.
- tsconfig strict 완화는 승인 없이 하지 않습니다.

## Expert Rules

- 타입은 컴파일 통과가 아니라 runtime contract를 표현해야 합니다.
- API response는 unknown에서 guard/parser를 거쳐 domain/UI model로 변환합니다.
- DTO, form state, view model은 nullable 의미가 다르면 분리합니다.
- as const, discriminated union, exhaustive check로 UI 상태 전이를 막습니다.
- typed client는 status, retry, error body, cancellation을 캡슐화합니다.
- any 금지는 목적이 아니라 오류를 숨기지 않는 수단입니다.
- API DTO와 ViewModel을 분리하고 날짜, 금액, enum 변환 위치를 고정합니다.
- 외부 입력 경계에서 as assertion을 금지하고 parser 뒤에만 좁힙니다.

## Expert Checks

- any 또는 as any가 타입 오류를 숨기는지 봅니다.
- API 타입과 실제 계약이 맞는지 봅니다.
- event handler와 form value 타입이 명시됐는지 봅니다.

## Failure Modes

- as any로 backend contract drift를 숨기는 상태.
- optional field를 loading 상태와 missing data 상태에 같이 쓰는 상태.
- component props가 API DTO 변경에 직접 흔들리는 상태.
- event target value를 암묵적 any로 처리하는 상태.
- generated type을 직접 수정하는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- 신규 .js/.jsx 추가.
- type assertion으로 오류 은폐.
- API contract와 타입 불일치.

## Verify

- typecheck.
- lint.
- API contract test or schema check.

## Evidence

- typecheck가 strict 설정에서 통과합니다.
- API boundary에 guard/parser 또는 typed client가 있습니다.
- UI state union이 empty/loading/error/success를 표현합니다.
- transport, validation, auth, unknown error type을 구분합니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
