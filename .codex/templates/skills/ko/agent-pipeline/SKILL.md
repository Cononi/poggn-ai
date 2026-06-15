---
name: agent-pipeline
description: MAW 구현 결과를 test, QA, refactor, security lane으로 전달할 때 사용합니다.
---

# agent-pipeline

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- upstream TASK가 commit에 연결된 뒤 downstream lane을 만듭니다.
- downstream prompt에는 commit, changed files, risk, expected output을 넣습니다.
- 검증 agent는 구현을 대체하지 않고 판정과 최소 수정 제안에 집중합니다.

## Procedure

- ready queue와 lane dependency를 먼저 확인합니다.
- 중복 downstream lane은 root_lane_id와 commit 기준으로 합칩니다.
- QA, refactor, security 결과는 pass, fail, blocked 중 하나로 정리합니다.
- 실패 결과는 구현 완료 취소가 아니라 follow-up TASK 후보로 남깁니다.

## Expert Rules

- lane 생성은 실행 계획이 아니라 실행 예약으로 취급합니다.
- downstream agent는 upstream diff만 검토하게 제한합니다.
- QA와 security는 구현 agent와 분리된 판단권을 가집니다.
- event idempotency는 root lane, commit, target role 조합으로 봅니다.
- 실패 lane은 원인, 재현, 소유자를 가진 follow-up으로 바꿉니다.
- 결과 통합 시 pass보다 blocker와 unresolved risk를 먼저 읽습니다.
- downstream 입력은 commit SHA, diffstat, owned files, risk를 포함합니다.
- QA, refactor, security 결과가 충돌하면 가장 보수적인 판정을 채택합니다.

## Expert Checks

- 같은 파일을 여러 downstream agent가 동시에 고치지 않는지 봅니다.
- security 실패가 QA pass로 덮이지 않는지 봅니다.
- test_runner 실패가 환경 문제인지 코드 문제인지 분류합니다.

## Failure Modes

- lane 문서만 생기고 실제 thread가 없는 상태.
- 하나의 실패를 여러 downstream lane이 중복 보고하는 상태.
- test 실패가 QA 실패로만 기록되고 재실행 근거가 없는 상태.
- security blocker가 refactor 제안에 묻히는 상태.
- security fail이 QA pass나 test pass로 상쇄되는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- commit 없는 TASK를 downstream으로 넘김.
- 검증 agent가 넓은 제품 구현을 수행함.
- downstream 실패를 무시하고 finalize함.

## Verify

- $codex-pipeline ready --for-ai.
- $codex-pipeline prompt.
- $codex-task trace --for-ai.

## Evidence

- ready queue와 spawned thread id가 일치합니다.
- 각 downstream report가 upstream commit hash를 참조합니다.
- 최종 보고에 pass, fail, blocked 집계가 있습니다.
- 실패 보고에는 재현 명령과 follow-up TASK 후보가 있습니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
