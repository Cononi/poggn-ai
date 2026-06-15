---
name: verify-gate
description: TASK 완료 전 quality, test, security 검증을 강제할 때 사용합니다.
---

# verify-gate

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- 변경 유형에 맞는 test, lint, build, security를 고릅니다.
- $codex-verify를 우선 실행합니다.
- 실패 명령, 오류, 승인 필요성을 보고합니다.

## Procedure

- 테스트 파일이 있으면 도구 부재를 pass로 보지 않습니다.
- staged gate와 full gate의 차이를 구분합니다.
- MAW downstream은 upstream commit 기준으로 검증합니다.
- flaky 의심은 재실행 근거와 패턴을 남깁니다.

## Expert Rules

- verify는 테스트 실행 목록이 아니라 완료 판정의 증거 수집입니다.
- 문서 변경, 코드 변경, 설정 변경은 서로 다른 gate를 요구합니다.
- 도구 부재는 pass가 아니라 skipped with reason입니다.
- staged gate와 full gate가 다르면 어떤 범위를 믿는지 명시합니다.
- flaky 의심은 재실행 횟수보다 실패 패턴 근거가 중요합니다.
- MAW downstream 검증은 upstream commit hash를 기준으로 합니다.
- 변경 파일별 최소 검증 명령을 매핑하고 미실행 사유를 요구합니다.
- DB, API, security 변경은 단위 테스트만으로 pass 처리하지 않습니다.

## Expert Checks

- allow-no-test가 문서/메타 변경 밖에서 쓰였는지 봅니다.
- security/quality gate가 빠졌는지 봅니다.
- 실패 로그가 원인 부분만 요약됐는지 봅니다.

## Failure Modes

- allow-no-test로 코드 변경 검증을 생략하는 상태.
- 실패 로그 전체를 붙이고 원인 요약이 없는 상태.
- quality/security 중 하나만 통과하고 verify complete라고 하는 상태.
- 환경 실패와 제품 실패를 구분하지 않는 상태.
- snapshot 변경이 contract 변화인지 확인하지 않은 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- 코드 변경인데 검증 명령 없음.
- failed test를 환경 문제로만 치부.
- security/quality gate 미실행.

## Verify

- $codex-verify gate --for-ai.
- $codex-quality gate --for-ai.
- $codex-security gate.

## Evidence

- 실행한 명령, exit code, 핵심 실패 라인이 있습니다.
- skipped 항목은 이유와 위험이 기록됩니다.
- 최종 판정은 pass/fail/blocked 중 하나입니다.
- 실패 재현 로그 줄, 명령, 환경 변수를 남깁니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
