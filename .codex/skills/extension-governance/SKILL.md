---
name: extension-governance
description: agent/skill 확장 승인, 중복 방지, 기존 capability 보강에 사용합니다.
---

# extension-governance

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- capability 요청을 문제, 반복성, domain으로 분해합니다.
- 일회성 작업은 skill로 만들지 않습니다.
- 비슷한 항목이 있으면 새로 만들지 않고 보강합니다.

## Procedure

- $codex-extend scan으로 기존 항목을 비교합니다.
- 새 agent는 사명, ownership, forbidden work를 가져야 합니다.
- 새 skill은 expert constraint와 failure mode를 가져야 합니다.
- 생성 후 discovery와 recommendation을 검증합니다.

## Expert Rules

- 확장은 개인 취향이 아니라 반복 실패를 줄이는 정책 변경입니다.
- 새 항목은 discovery, trigger, permission, maintenance 비용을 증가시킵니다.
- 유사 capability가 있으면 새로 만들기 전 trigger를 좁히거나 body를 보강합니다.
- 승인 없는 create는 도구 생태계의 신뢰를 깨는 변경으로 봅니다.
- 새 skill/agent는 제거 기준과 소유 범위를 함께 가져야 합니다.
- 확장 후 실제 추천 경로가 의도대로 작동하는지 확인합니다.
- 승인 근거는 반복성, 전문성, 기존 skill 부족분으로 나눕니다.
- 기존 skill과 trigger가 겹치면 routing 우선순위를 정합니다.

## Expert Checks

- scope가 너무 넓은 capability인지 봅니다.
- 승인 없이 create 명령이 실행됐는지 봅니다.
- description trigger가 충분히 구체적인지 봅니다.

## Failure Modes

- 모호한 description 때문에 과도하게 trigger되는 상태.
- 새 agent가 QA, 구현, 보안까지 모두 처리하는 상태.
- scan 결과를 보지 않고 중복 capability를 만드는 상태.
- 승인 이유가 사용자 요청 반복 없이 단발성인 상태.
- 승인 로그 없이 --approve 생성이 실행되는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- 중복 skill/agent 생성.
- approval 없이 확장.
- blocker와 verification 없는 capability.

## Verify

- $codex-extend scan --for-ai.
- $codex-agents check.
- $codex-skills list.

## Evidence

- scan/inspect 결과와 중복 판단이 남아 있습니다.
- 신규/수정 capability의 trigger test가 있습니다.
- 승인 범위와 생성 파일 목록이 기록됩니다.
- 생성 후 discovery, recommendation, 중복 scan 결과를 검증합니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
