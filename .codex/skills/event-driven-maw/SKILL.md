---
name: event-driven-maw
description: TASK 완료 이벤트로 필요한 downstream agent를 동적으로 고를 때 사용합니다.
---

# event-driven-maw

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- 이벤트 원천은 commit에 연결된 TASK 완료입니다.
- changed files와 risk로 downstream agent를 고릅니다.
- auth, permission, secret 변경은 security를 생략하지 않습니다.

## Procedure

- schema/query 변경은 database 또는 JPA 검증을 붙입니다.
- frontend UI 변경은 component/TS 검증을 붙입니다.
- 중복 이벤트는 root lane과 commit 기준으로 제거합니다.
- ready lane은 실제 subagent로 실행합니다.

## Expert Rules

- event는 TASK done이 아니라 commit-linked completion일 때만 신뢰합니다.
- changed files, risk, domain tag로 downstream lane을 결정합니다.
- auth, secret, permission, deploy 변경은 security event를 강제합니다.
- schema/query 변경은 DB/JPA 검증 event를 붙입니다.
- frontend 변경은 type, accessibility, visual state 검증을 붙입니다.
- event 처리 결과는 lane 생성과 subagent spawn을 분리해 기록합니다.
- event idempotency key는 TASK id, commit SHA, changed file hash로 둡니다.
- 파일 패턴별 downstream mapping은 auth, DB, API, UI, CI, docs로 나눕니다.

## Expert Checks

- downstream lane이 생성만 되고 spawn되지 않았는지 봅니다.
- high-risk 변경에 QA/security가 빠졌는지 봅니다.
- finalize 조건이 충족됐는지 봅니다.

## Failure Modes

- commit 없는 TASK 완료 이벤트로 downstream을 만드는 상태.
- 이벤트 중복으로 같은 검증이 여러 번 실행되는 상태.
- ready lane이 spawn되지 않고 대시보드에만 남는 상태.
- downstream 실패가 upstream done 상태를 무비판적으로 유지하는 상태.
- 삭제, rename, migration 변경을 일반 파일 변경 risk로 처리하는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- commit 연결 전 downstream 생성.
- 보안 영향 변경의 security 생략.
- 이벤트 중복으로 같은 검증 반복.

## Verify

- $codex-pipeline ready --for-ai.
- $codex-pipeline prompt.
- $codex-task trace --for-ai.

## Evidence

- event id, root lane, commit hash가 기록됩니다.
- 선택된 downstream role과 제외 이유가 있습니다.
- spawn 결과와 최종 report가 연결됩니다.
- event 결과는 spawned, deduped, blocked, skipped 중 하나입니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
