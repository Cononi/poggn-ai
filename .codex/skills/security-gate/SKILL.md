---
name: security-gate
description: 인증, 인가, secret, 입력 검증, 배포 유출 보안을 검사합니다.
---

# security-gate

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- asset, entry point, trust boundary를 먼저 찾습니다.
- authentication과 authorization을 분리해 검토합니다.
- secret은 source, log, config, docs, fixture에서 모두 찾습니다.

## Procedure

- user, tenant, role ownership을 data query에서 확인합니다.
- input validation과 output encoding을 확인합니다.
- session, CSRF, CORS, cookie flag를 endpoint 성격에 맞춥니다.
- error message와 audit log의 민감정보를 확인합니다.

## Expert Rules

- 보안 검토는 exploit path를 설명할 수 있어야 통과입니다.
- authentication 성공은 authorization 성공을 의미하지 않습니다.
- owner/tenant predicate는 service check와 data query 양쪽에서 확인합니다.
- secret은 source뿐 아니라 logs, docs, artifacts, cache, images에서 봅니다.
- 입력 검증은 type, size, format, authorization context를 포함합니다.
- error와 audit log는 조사 가능성과 정보 노출을 동시에 만족해야 합니다.
- tenant isolation은 controller 조건이 아니라 query predicate로 검증합니다.
- JWT/session 만료, refresh, revocation 경로를 endpoint별로 확인합니다.

## Expert Checks

- exploit scenario를 한 줄로 설명할 수 있는지 봅니다.
- dependency나 build artifact에 secret exposure가 있는지 봅니다.
- auth only를 authz로 착각했는지 봅니다.

## Failure Modes

- IDOR 가능 endpoint가 principal만 확인하는 상태.
- CORS/CSRF/cookie flag가 endpoint 성격과 맞지 않는 상태.
- token, password, internal id가 response나 log에 남는 상태.
- dependency나 generated artifact에 secret이 포함되는 상태.
- CORS wildcard와 credential 조합이 허용되는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- owner/role check 없는 mutation.
- secret scan 실패 무시.
- 민감정보 log/response 노출.

## Verify

- $codex-security gate.
- $codex-quality gate --for-ai.
- targeted auth negative tests.

## Evidence

- asset, entry point, trust boundary가 정리됩니다.
- negative authz test 또는 exploit scenario가 있습니다.
- secret scan과 staged security gate가 통과합니다.
- SSRF, path traversal, mass assignment 입력 가능성을 검토했습니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
