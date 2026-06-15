# 프론트 컴포넌트 지침

React 프론트는 기본적으로 TypeScript와 TSX를 사용합니다.

JSX가 있는 새 UI 파일은 `.tsx`입니다.

JSX가 없는 타입, hook, client, util 파일은 `.ts`입니다.

신규 `.js` 또는 `.jsx`는 legacy 작업을 명시한 경우만 허용합니다.

## 컴포넌트 계층

컴포넌트는 이름이 아니라 성질로 재사용합니다.

primitive는 최소 UI 의미와 접근성을 담당합니다.

compound는 함께 쓰이는 조각을 묶습니다.

feature는 도메인 화면 조각을 조합합니다.

page와 screen은 route composition만 담당합니다.

## 재사용 기준

시각 성향이 같으면 variant와 tone으로 합칩니다.

크기 차이는 size prop으로 흡수합니다.

상태 차이는 state, disabled, loading prop으로 흡수합니다.

구조 차이는 slot, children, render prop으로 흡수합니다.

행동 차이는 onChange, onSubmit 같은 callback으로 흡수합니다.

## 반복 추출 대상

Button, Input, Modal, Table만 대상이 아닙니다.

Card, FormField, Select, Checkbox, Radio도 대상입니다.

Tabs, Accordion, Drawer, Popover, Tooltip도 대상입니다.

Toolbar, FilterBar, SearchBox, Pagination도 대상입니다.

EmptyState, ErrorState, LoadingState도 대상입니다.

DataTable, DetailPanel, StatusBadge도 대상입니다.

동일 JSX 패턴이 3회 이상 반복되면 추출합니다.

## 금지 패턴

page 하나에 API, 상태, 스타일, 검증을 모두 넣지 않습니다.

컴포넌트 안에서 직접 fetch와 axios를 반복하지 않습니다.

비슷한 버튼을 이름만 다르게 여러 개 만들지 않습니다.

any, as any, 넓은 object 타입으로 props를 숨기지 않습니다.

160줄 초과 컴포넌트는 리팩토링 후보입니다.

## 권장 구조

```text
src/
  app/ 또는 pages/
  features/order/
    components/
    hooks/
    api/
    types.ts
  shared/ui/
    Button.tsx
    Modal.tsx
    DataTable.tsx
  shared/lib/
```

품질 검사는 `$codex-quality frontend --for-ai`로 확인합니다.
