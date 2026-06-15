# 코드 품질 지침

품질 gate는 완료 commit 전에 실행합니다.

기본 명령은 `$codex-quality gate --for-ai`입니다.

변경분만 보려면 staged 또는 git diff 기준을 사용합니다.

## 강제 기준

소스 파일은 200줄을 넘기지 않습니다.

프론트 컴포넌트 파일은 160줄 이하를 목표로 합니다.

React 신규 UI는 `.tsx`를 사용합니다.

JSX가 없는 로직과 타입은 `.ts`를 사용합니다.

중복 코드와 중복 기능을 만들지 않습니다.

secret, token, password 흔적은 error입니다.

## 프론트 기준

page와 screen은 조합만 담당합니다.

상태는 hook, API는 typed client, 검증은 schema로 분리합니다.

같은 성질의 UI는 primitive, compound, feature로 추출합니다.

variant, size, tone, state, slot, render prop을 우선 검토합니다.

## 리팩토링 기준

테스트 실패 중이면 리팩토링보다 실패 수정이 먼저입니다.

품질 gate error가 있으면 TASK 완료 처리를 하지 않습니다.

warn은 QA가 보고 refactor TASK 생성 여부를 판단합니다.
