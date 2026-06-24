---
name: front
description: Frontend engineering guidance for user-facing UI implementation, state management, component structure, accessibility, responsive behavior, API integration, client-side validation, and browser-facing tests. Use when work touches React/Vue/Svelte/components, pages, forms, routing, client state, styling, or frontend build behavior.
---

# Front Skill

## 목적

사용자가 실제로 조작하는 화면을 안정적이고 예측 가능하게 구현한다. UI는 기존 디자인 시스템과 상태 흐름을 따르고, 접근성/반응형/검증 가능한 동작을 함께 확인한다.

## 기본 원칙

- 기존 컴포넌트, 스타일 토큰, 라우팅, 상태 관리 패턴을 먼저 확인한다.
- 새 컴포넌트는 화면 책임이 분명할 때만 만든다.
- 서버 상태와 클라이언트 UI 상태를 섞지 않는다.
- loading, empty, error, disabled, optimistic, permission 상태를 필요한 만큼 구현한다.
- 텍스트, 버튼, 입력, 모달은 모바일과 데스크톱에서 겹치지 않게 한다.
- 시각 구현은 designer 기준과 충돌하지 않게 한다.

## 사용 절차

1. 사용자 흐름을 확인한다: 진입, 주요 액션, 성공, 실패, 되돌리기.
2. 기존 UI 패턴을 확인한다: component library, icons, spacing, colors, form handling.
3. 상태 모델을 정한다: server data, local state, derived state, URL state.
4. API 계약을 확인한다: request, response, error, retry, cache invalidation.
5. UI 상태를 구현한다: loading, empty, error, success, disabled.
6. 접근성과 반응형을 확인한다: keyboard, focus, labels, viewport constraints.
7. 테스트와 빌드로 검증한다.

## 컴포넌트 기준

- 한 컴포넌트가 데이터 fetch, 복잡한 변환, 프레젠테이션을 모두 책임지지 않게 한다.
- props는 필요한 값만 받고 모호한 boolean 조합을 늘리지 않는다.
- 반복 UI는 기존 list/table/card 패턴을 따른다.
- form은 validation message, submit state, disabled state를 명확히 처리한다.
- icon button에는 accessible name 또는 tooltip을 제공한다.

## 상태 관리 기준

- 서버 데이터는 query/cache 계층이 있으면 그 패턴을 따른다.
- URL에 남아야 하는 상태와 local-only 상태를 구분한다.
- derived state는 가능한 계산으로 유지하고 중복 저장하지 않는다.
- 비동기 작업은 race, stale response, double submit을 고려한다.
- optimistic update는 실패 시 rollback 동작을 둔다.

## 접근성/반응형 기준

- 클릭 가능한 요소는 keyboard로도 접근 가능하게 한다.
- input, select, textarea에는 label 또는 aria-label을 둔다.
- focus 이동이 필요한 modal, drawer, menu는 focus trap/restore를 확인한다.
- 모바일에서 텍스트가 버튼/카드 밖으로 넘치지 않게 한다.
- hover에만 의존하지 않고 touch 환경에서도 동작하게 한다.

## 테스트 기준

- 핵심 사용자 흐름은 component/integration/e2e 중 적절한 수준으로 검증한다.
- form validation, API error, loading/empty state를 포함한다.
- visual risk가 크면 screenshot 또는 수동 viewport 확인 결과를 남긴다.
- build/lint/typecheck 중 프로젝트가 제공하는 검증을 실행한다.

## Multi Agent 연결

- 화면 구현, 상태 흐름, API 연결이 독립 작업으로 나뉘면 `pogo-front-agent`를 사용한다.
- UX/시각 판단이 중요한 작업은 `pogo-designer-agent`와 먼저 방향을 맞춘다.
- backend contract가 바뀌면 backend agent와 payload/error shape를 맞춘 뒤 구현한다.

## 완료 체크리스트

- 모든 주요 UI 상태가 처리되었는가.
- 모바일/데스크톱에서 레이아웃이 깨지지 않는가.
- 접근성 이름, focus, keyboard 동작이 필요한 곳에 있는가.
- API 실패와 재시도/복구 흐름이 명확한가.
- 프로젝트의 lint/test/build 검증을 실행했는가.
