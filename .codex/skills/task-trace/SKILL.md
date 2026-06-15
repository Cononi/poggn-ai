---
name: task-trace
description: TASK, lane, commit 연결과 변경 추적을 검증할 때 사용합니다.
---

# task-trace

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- state 원본은 JSONL이고 TASKS.md는 출력물로 봅니다.
- TASK id, lane id, commit hash를 함께 확인합니다.
- done 처리 전 commit, files, verification을 확인합니다.

## Procedure

- files list는 commit diff에서 가져옵니다.
- 여러 TASK가 한 commit을 공유하면 각각 link를 남깁니다.
- state update commit과 product commit 관계를 기록합니다.
- trace가 깨지면 script 복구를 우선합니다.

## Expert Rules

- trace source는 사람이 편집한 markdown이 아니라 구조화 state입니다.
- TASK done은 commit, files, verification, owner가 모두 연결될 때만 가능합니다.
- 하나의 commit이 여러 TASK를 닫으면 각 TASK에 같은 hash를 명시합니다.
- rollback 영향은 commit graph가 아니라 TASK dependency로도 확인합니다.
- state 복구는 추측보다 script와 git diff 근거로 수행합니다.
- trace 누락은 완료 보고 전에 blocker로 취급합니다.
- TASK done 전 commit hash, changed files, verification evidence를 확인합니다.
- 한 commit이 여러 TASK를 닫으면 각 TASK에 같은 hash와 파일 근거를 남깁니다.

## Expert Checks

- TASKS.md만 수정하고 JSONL이 누락됐는지 봅니다.
- 여러 TASK 변경을 한 TASK로 숨겼는지 봅니다.
- rollback 영향 TASK를 trace로 확인했는지 봅니다.

## Failure Modes

- TASKS.md만 [x] 처리하고 JSONL/state가 그대로인 상태.
- commit은 있지만 어떤 TASK의 산출물인지 모르는 상태.
- 여러 작업을 하나의 TASK로 숨겨 review와 rollback이 어려운 상태.
- state commit과 product commit 관계가 사라진 상태.
- TASKS.md만 갱신되고 JSONL/state 원본이 빠진 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- TASK done without link.
- TASKS.md-only update.
- 누락된 commit/file 연결.

## Verify

- $codex-task trace --for-ai.
- $codex-task files T001.
- git log --oneline.

## Evidence

- TASK id, lane id, commit hash, file list가 연결됩니다.
- trace command 결과와 git show 결과가 일치합니다.
- done 처리 전 검증 결과가 기록됩니다.
- rollback, follow-up, state-only commit 관계를 trace에 연결합니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
