---
name: react
description: React component, hook, state, typed client UI 구현에 사용합니다.
---

# react

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- component 책임을 한 문장으로 제한합니다.
- state는 hook, API는 typed client로 분리합니다.
- a11y label, focus, keyboard path를 확인합니다.

## Procedure

- props는 variant, size, tone, state를 명확히 표현합니다.
- form은 validation, dirty, error, submit state를 모델링합니다.
- list는 key, empty, loading, error state를 갖습니다.
- layout은 mobile/desktop overflow를 검증합니다.

## Expert Rules

- React component는 rendering, state, side effect, IO 경계를 분리합니다.
- hook은 browser lifecycle과 domain transition을 명시해야 합니다.
- controlled form은 validation, dirty, touched, pending 상태를 분리합니다.
- list rendering은 key 안정성, virtualization 필요성, empty/error 상태를 봅니다.
- accessible name은 보이는 label이 없어도 모든 interactive control에 필요합니다.
- animation과 optimistic UI는 rollback과 reduced motion을 고려합니다.
- useEffect는 외부 시스템 동기화에만 쓰고 파생 상태 계산에는 쓰지 않습니다.
- async state update는 unmount, abort, stale response 처리를 가집니다.

## Expert Checks

- copy-pasted JSX가 남았는지 봅니다.
- button과 icon control에 accessible name이 있는지 봅니다.
- animation이 사용자의 행동을 막는지 봅니다.

## Failure Modes

- useEffect가 data dependency와 mutation을 동시에 처리하는 상태.
- component가 API DTO와 domain rule을 직접 해석하는 상태.
- loading skeleton이 layout shift를 만드는 상태.
- 모바일에서 버튼 텍스트나 toolbar가 overflow되는 상태.
- controlled/uncontrolled input 전환 경고가 가능한 초기값 모델.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- untyped props 또는 response.
- responsive overlap 또는 text overflow.
- API 호출이 component body에 흩어짐.

## Verify

- typecheck.
- visual smoke across breakpoints.
- a11y keyboard check.

## Evidence

- component/hook/client 분리가 diff에서 보입니다.
- a11y label, focus, keyboard path를 확인했습니다.
- typecheck와 주요 UI state 검증이 통과합니다.
- reorder, filter, pagination 후 focus 유지 여부를 확인합니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
