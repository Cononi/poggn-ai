---
name: capability-extension
description: 필요한 agent나 skill이 없을 때 중복 검토 후 확장할 때 사용합니다.
---

# capability-extension

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- 새 capability보다 기존 capability 보강을 먼저 검토합니다.
- 새 skill은 trigger, procedure, blocker, verification을 가져야 합니다.
- 새 agent는 좁은 사명과 금지 작업을 가져야 합니다.

## Procedure

- $codex-capabilities inspect 또는 $codex-extend scan을 실행합니다.
- 유사도가 높으면 description이나 reference를 보강합니다.
- 생성이 필요하면 승인 근거와 중복 없음 근거를 남깁니다.
- 생성 후 list/check 명령으로 discovery를 검증합니다.

## Expert Rules

- capability는 반복 가능한 실패를 줄일 때만 추가합니다.
- 새 skill은 trigger가 좁고 body가 실행 판단을 바꿔야 합니다.
- 새 agent는 책임, 금지 작업, 산출물 형식을 가져야 합니다.
- 중복이 보이면 새 항목보다 description과 reference를 보강합니다.
- 확장 후 discovery, recommendation, 실제 사용 경로를 모두 확인합니다.
- 승인 근거는 문제, 기존 대안, 왜 부족했는지를 포함해야 합니다.
- 신규 생성 전 inspect와 extend check로 중복 후보를 기록합니다.
- 기존 capability 보강으로 해결 가능하면 신규 생성을 차단합니다.

## Expert Checks

- 일회성 작업을 skill로 만들고 있지 않은지 봅니다.
- 모든 일을 하는 agent가 생기지 않았는지 봅니다.
- hook이나 edit-mode 정책을 우회하지 않았는지 봅니다.

## Failure Modes

- 한 번의 요청을 영구 skill로 만드는 상태.
- 모든 문제를 처리하는 general agent를 만드는 상태.
- description이 넓어 원하지 않는 상황에서 trigger되는 상태.
- 생성 후 list/check 검증 없이 완료하는 상태.
- 특정 파일 전용 지식이 capability로 승격되는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- 중복 capability 생성.
- 승인 없이 agent/skill 생성.
- blocker와 검증 없는 skill 추가.

## Verify

- $codex-extend scan --for-ai.
- $codex-agents check.
- $codex-skills list.

## Evidence

- extend scan 또는 capability inspect 결과가 있습니다.
- 새 항목의 trigger와 blocker가 테스트되었습니다.
- 기존 capability 보강이 불가능한 이유가 기록됩니다.
- 새 agent는 ownership, 입력, 출력, 종료 기준을 가집니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
