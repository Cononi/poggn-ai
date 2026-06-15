---
name: quality-gate
description: 품질, 중복, 대형 파일, 책임 혼합, 보안 냄새를 검사할 때 사용합니다.
---

# quality-gate

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- large file, duplication, ownership, security smell 기준을 먼저 둡니다.
- $codex-quality gate --for-ai를 실행합니다.
- public/exported 클래스, 메소드, 함수는 목적/계약 doc 주석을 둡니다.
- 품질 실패는 현재 TASK blocker인지 먼저 판단합니다.

## Procedure

- 변경 파일을 기능, 테스트, 문서, 설정으로 분류합니다.
- large file, duplicate, mixed responsibility를 먼저 봅니다.
- backend는 transaction, ownership, N+1을 확인합니다.
- frontend는 TSX, component size, typed client를 확인합니다.
- 주석은 왜/계약/제약을 설명하고 코드 반복 설명은 피합니다.

## Expert Rules

- quality gate는 미관 검사가 아니라 유지보수 위험 차단입니다.
- 큰 파일은 줄 수보다 책임 수와 변경 이유로 판단합니다.
- 중복은 텍스트 반복보다 business rule 반복이 더 위험합니다.
- false positive는 제외해도 되지만 근거와 owner를 남깁니다.
- security smell은 quality에서 끝내지 않고 security gate로 보냅니다.
- 품질 실패가 이번 TASK 밖이면 follow-up과 blocker를 분리합니다.
- public API 변경과 내부 리팩토링이 섞이면 분리 필요성을 판단합니다.
- 신규 helper가 기존 util, framework, domain service와 중복인지 봅니다.
- doc 주석 누락은 strict 품질 검증에서 blocker로 봅니다.

## Expert Checks

- controller/UI에 business rule이 숨었는지 봅니다.
- false positive는 근거를 남기고 제외합니다.
- security smell은 security-gate로 연결합니다.
- public/exported symbol의 doc 주석이 목적과 계약을 설명하는지 봅니다.

## Failure Modes

- controller/UI/script에 business rule이 섞인 상태.
- 테스트를 통과시키려고 assertion을 약화한 상태.
- 거대한 diff가 review 가능한 단위로 쪼개지지 않은 상태.
- quality 실패를 warnings로만 보고하고 commit하는 상태.
- feature flag, dead code, TODO가 배포 경로에 남는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- gate fail 무시.
- 혼합 책임을 task scope 안에 방치.
- 미검증 보안 위험을 pass로 보고.
- public/exported symbol의 목적/계약 doc 주석 누락.

## Verify

- $codex-quality gate --for-ai.
- $codex-refactor analyze --for-ai.
- $codex-security gate.

## Evidence

- quality gate output과 조치/예외 근거가 있습니다.
- large/duplicate/mixed responsibility 결과를 분류했습니다.
- 남은 품질 위험은 TASK 또는 follow-up으로 연결됩니다.
- generated file과 수기 편집 파일의 품질 기준을 분리합니다.
- doc 주석 예외는 private trivial helper 또는 generated file 근거가 있습니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
