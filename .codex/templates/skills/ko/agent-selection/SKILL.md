---
name: agent-selection
description: 요청에 맞는 MAW/SAW agent와 skill을 선택하고 중복 생성을 막을 때 사용합니다.
---

# agent-selection

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- 요청을 feature, layer, risk, artifact 기준으로 나눕니다.
- agent는 역할, skill은 절차로 분리합니다.
- 기존 agent와 skill을 먼저 재사용합니다.

## Procedure

- backend, frontend, database, devops, docs 경계를 먼저 정합니다.
- cross-stack 작업은 contract/schema lane을 앞에 둡니다.
- security 영향이 있으면 security-gate를 강제로 포함합니다.
- test 작성과 test 실행은 필요한 경우 분리합니다.

## Expert Rules

- agent는 책임 주체이고 skill은 실행 절차라는 경계를 유지합니다.
- 구현, 테스트 작성, 테스트 실행, QA 판정은 같은 agent에 몰지 않습니다.
- 권한, 결제, 데이터 삭제, 배포 영향은 security나 ops lane을 붙입니다.
- contract 변경은 backend/frontend 구현보다 먼저 독립 lane으로 둡니다.
- 작업 분리는 파일 수보다 merge 충돌 가능성을 우선합니다.
- 없는 agent를 만들기 전 기존 agent description 누락을 의심합니다.
- $codex-risk classify 결과를 agent 수와 검증 lane 결정에 반영합니다.
- 새 agent 전 $codex-capabilities inspect와 $codex-extend check를 실행합니다.

## Expert Checks

- backend에게 QA/security 판정을 맡기지 않았는지 봅니다.
- test_runner가 제품 구현을 맡지 않았는지 봅니다.
- refactor가 동작 변경을 포함하지 않는지 봅니다.

## Failure Modes

- 한 agent가 구현과 최종 승인을 동시에 맡는 상태.
- 병렬화를 위해 같은 파일을 여러 lane에 나눈 상태.
- test_runner에게 제품 구현을 맡기는 상태.
- capability 중복을 확인하지 않고 새 agent를 만드는 상태.
- docs-only, test-only 작업을 불필요하게 MAW로 키우는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- 역할이 겹치는 새 agent 생성.
- 사용자에게 agent 수를 불필요하게 질문.
- 검증 role 없이 high-risk 변경 진행.

## Verify

- $codex-capabilities inspect.
- $codex-agents check.
- $codex-skills list.

## Evidence

- 선택된 agent마다 owner, input, output, forbidden work가 있습니다.
- security 영향 여부가 yes/no로 기록됩니다.
- 중복 capability 확인 결과가 남아 있습니다.
- 제외한 agent 후보와 제외 사유를 짧게 남깁니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
