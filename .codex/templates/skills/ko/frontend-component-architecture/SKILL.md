---
name: frontend-component-architecture
description: 프론트 UI를 재사용 가능한 component, hook, typed client로 나눌 때 사용합니다.
---

# frontend-component-architecture

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- page는 route, data boundary, composition만 담당합니다.
- state는 hook, API는 typed client나 service로 분리합니다.
- loading, error, empty, disabled 상태를 설계합니다.

## Procedure

- primitive, compound, feature component 계층을 정합니다.
- variant, size, tone, slot으로 차이를 흡수합니다.
- form, table, filter, toolbar는 재사용 후보로 봅니다.
- 접근성 label, role, focus, keyboard path를 확인합니다.

## Expert Rules

- component 분리는 미관보다 state, IO, domain 책임 분리로 판단합니다.
- page는 route composition이고 business decision은 hook/service로 내립니다.
- compound component는 keyboard, focus, aria contract까지 포함해야 합니다.
- variant는 className 분기가 아니라 의미 있는 API로 노출합니다.
- table/form/filter는 loading, empty, error, dirty 상태를 동시에 설계합니다.
- 재사용은 세 번째 반복에서 추출하되 domain 의미를 잃지 않습니다.
- modal/drawer는 focus trap, escape, inert, 뒤로가기 동작을 검증합니다.
- table/filter/search는 URL state, pagination, reset 책임을 먼저 정합니다.

## Expert Checks

- component가 160줄을 넘는지 봅니다.
- 동일 JSX 패턴이 세 번 이상 반복되는지 봅니다.
- responsive overflow와 text wrapping을 확인합니다.

## Failure Modes

- page 파일이 data fetch, mutation, rendering, validation을 모두 갖는 상태.
- 공통 컴포넌트가 특정 feature DTO에 묶이는 상태.
- responsive overflow가 긴 텍스트에서만 깨지는 상태.
- icon button에 accessible name이나 tooltip이 없는 상태.
- design token 없이 임의 색상이나 간격을 추가하는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- UI, API, validation, domain mutation이 한 파일에 혼합.
- 접근성 이름 없는 interactive control.
- 반복 JSX 복붙 유지.

## Verify

- component line count.
- TypeScript check.
- responsive/a11y manual check.

## Evidence

- component tree와 state owner가 설명됩니다.
- loading/error/empty/disabled 상태가 구현됩니다.
- typecheck와 responsive 확인 결과가 있습니다.
- shared 승격은 두 개 이상 사용처와 stable props API가 있습니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
