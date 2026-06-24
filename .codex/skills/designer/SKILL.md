---
name: designer
description: Product design and UX guidance for user-facing interfaces, information architecture, layout, visual hierarchy, interaction states, accessibility, responsive behavior, and design-system consistency. Use when planning or reviewing screens, flows, dashboards, forms, navigation, visual polish, or frontend UX decisions.
---

# Designer Skill

## 목적

사용자가 빠르게 이해하고 실수 없이 사용할 수 있는 화면과 흐름을 설계한다. 장식보다 업무 성공, 정보 우선순위, 상호작용 명확성, 접근성, 반응형 안정성을 우선한다.

## 기본 원칙

- 화면의 주요 사용자를 먼저 정의한다.
- 첫 화면은 실제 작업 또는 핵심 정보로 시작한다.
- 설명 문구로 UI 문제를 덮지 않는다. 구조와 컨트롤 자체가 이해되게 만든다.
- 기존 디자인 시스템, 색상, spacing, typography, icon 사용 규칙을 따른다.
- 카드, 섹션, 패널을 남용하지 않는다. 정보 구조가 먼저다.
- 텍스트와 컨트롤은 모바일/데스크톱에서 겹치거나 넘치지 않게 한다.
- 장식 요소는 작업 이해를 돕지 않으면 추가하지 않는다.

## 사용 절차

1. 사용자 목표를 정한다: 사용자가 이 화면에서 끝내야 하는 일.
2. 정보 우선순위를 정한다: 가장 먼저 보여야 할 데이터, 보조 정보, 숨겨도 되는 정보.
3. 흐름을 설계한다: 진입, 탐색, 선택, 입력, 확인, 오류, 완료.
4. 레이아웃을 잡는다: grid, density, spacing, responsive breakpoints.
5. 컨트롤을 선택한다: button, icon button, tabs, segmented control, menu, dialog, form field.
6. 상태를 설계한다: default, hover, focus, active, disabled, loading, empty, error, success.
7. 접근성과 반응형을 확인한다.
8. front 구현자가 바로 구현할 수 있게 구체적인 UI 결정을 남긴다.

## UX 기준

- 사용자가 다음 행동을 추측하지 않게 한다.
- 자주 쓰는 액션은 가까이 두고, 위험한 액션은 분리한다.
- destructive action은 확인, 되돌리기, 권한 제한 중 필요한 보호를 둔다.
- 빈 상태는 다음 행동을 제공한다.
- 오류 상태는 원인과 복구 방법을 제공한다.
- 복잡한 폼은 그룹화, progressive disclosure, inline validation을 사용한다.

## 레이아웃 기준

- 운영/관리 도구는 조용하고 밀도 있게 구성한다.
- 마케팅 hero가 필요한 화면이 아니면 과장된 hero, 장식 카드, 큰 여백을 피한다.
- dashboard는 scan, compare, drill-down이 쉬워야 한다.
- table/list/detail 구조에서는 선택 상태와 현재 위치가 명확해야 한다.
- modal은 짧은 집중 작업에만 사용하고, 복잡한 편집은 page/drawer를 고려한다.
- 같은 화면 안에서 heading scale과 spacing rhythm을 일관되게 유지한다.

## 시각 기준

- 색은 의미를 가져야 한다: primary action, status, warning, danger, neutral.
- 한 가지 색 계열만으로 전체 화면을 지배하지 않는다.
- 아이콘은 텍스트를 대체할 때 accessible name이 있어야 한다.
- 버튼 안 텍스트는 줄바꿈/overflow를 고려한다.
- card radius는 기존 시스템을 따르고, 새로 정해야 하면 8px 이하를 기본으로 한다.
- 실제 제품/장소/콘텐츠가 중요한 화면은 실제 이미지나 명확한 visual asset을 사용한다.

## 접근성 기준

- 색만으로 상태를 전달하지 않는다.
- focus indicator를 숨기지 않는다.
- contrast가 낮은 보조 텍스트를 남용하지 않는다.
- form label, helper text, error text의 관계가 명확해야 한다.
- keyboard 순서가 시각 순서와 크게 어긋나지 않아야 한다.

## Front 연계 기준

Designer는 구현 세부 코드보다 의사결정을 남긴다.

```md
Design Direction:
- User goal: 사용자 목표
- Layout: 화면 구조와 responsive 기준
- Components: 사용할 주요 컨트롤
- States: 필요한 상태
- Accessibility: 필수 접근성 요구
- Visual constraints: 색, 밀도, 이미지, spacing 기준
- Handoff: front 구현자가 확인할 항목
```

## Multi Agent 연결

- UX 방향, 정보 구조, 시각 검토가 독립적으로 가능하면 `pogo-designer-agent`를 사용한다.
- 실제 UI 구현은 `pogo-front-agent`가 맡고, designer agent는 구현 전 방향과 구현 후 리뷰를 제공한다.
- 디자인 판단이 불명확하면 메인 에이전트가 사용자 목표를 다시 확인한다.

## 완료 체크리스트

- 화면의 주요 사용자 목표가 분명한가.
- 정보 우선순위와 주요 액션이 즉시 보이는가.
- 모든 핵심 상태가 설계되었는가.
- 모바일/데스크톱 레이아웃 제약이 명시되었는가.
- 접근성 요구가 구현자가 실행할 수 있을 만큼 구체적인가.
