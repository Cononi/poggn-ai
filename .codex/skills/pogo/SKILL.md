---
name: pogo
description: 작업 수행을 관장하는 기본 운영 엔진입니다. 사용자 지시, AGENTS, 그리고 세부 skill을 연결해 실행한다.
---

# Pogo 운영 엔진 (필수)

## 우선순위

1. 사용자 현재 지시(문맥 기반 명시적 요청).
2. `AGENTS.md`의 절대 규칙: 승인 전 STOP, 안전성/데이터 손실 방지, Git/Release 규칙.
3. 이 `pogo` skill의 운영 규칙.
4. 작업 영역의 전문 skill(`evidence-driven-sdd`, `pogo-settings`, `safe-git-automation`, `security`, `backend`, `front`, `designer`, `architecture`, `pogo-subagent-auto` 등).

`AGENTS.md`의 승인 전 STOP/안전/Git-Release 규칙은 상위 규칙이므로 `pogo`는 이를 넘을 수 없다.

## 사고 방식 (필수 규칙)

1. 코딩하기 전에 충분히 생각한다.
- 가정은 근거를 붙여 밝히고, 불명확한 의도는 질문한다.
- 충분한 이해 없이 시작하지 않는다.

2. 단순하게 작성한다.
- 요구 범위 밖의 추가 기능, 설정, 호환성 분기, 과도한 추상화는 만들지 않는다.
- 반복 호출/일회성 코드를 위해 구조를 과도하게 분리하지 않는다.
- 처음엔 최소한의 동작으로 시작하고, 불필요한 라인을 즉시 축소한다.

3. 문제를 직접 해결한다.
- 문서를 읽고, 의도를 해석하고, 목표-증거-완료 기준을 맞춘 뒤 작업한다.
- “동작해 보이는 대로 넘어가기”가 아니라 실패 조건/경계조건을 같이 판단한다.

4. 변경은 최소로.
- 고아가 되는 import/변수/함수/파일이 생기면 제거한다.
- 본 작업과 직접 관련 없는 정리만 수행한다.

5. 목표 중심 검증.
- 작업 성공은 “변경했으므로 완료”가 아니라, 목표-검증 포인트가 충족된 것으로 판단한다.

6. 코드 최소화
- 코드가 200줄이라면 50줄로 줄일 수 있다면 무조건 줄여야 한다.

## Subagent 운영 규칙

이 skill은 `subagent.auto` 설정이든 아니든 필요 시 다중 병렬 에이전트를 적극 활용한다.

- `subagent.auto=true`이고 작업이 Subagent가 수행할 성격일 때는,
  **`작업 진행 예정 보고서 승인이 완료된 뒤`**, 즉시(Subagent 최소 1개 이상)를 시작한다.
- Git 상태 확인, commit/push/merge, release note 초안/검증, 탐색/분석/리뷰/QA/보안/아키텍처 판단은 단일 작업자가 아니라 기본적으로 Subagent 라우팅을 우선 고려한다.
- release 실행은 Subagent나 auto가 승인할 수 없고, 현재 사용자 요청의 명시적 release 지시가 있을 때만 메인이 최종 승인 범위를 확인한다.
- 단, 문서 수정 1~2줄 확인, 단순 출력 조회, 사용 의도 불명확, 위험도 낮은 즉시 응답은 직접 수행해도 된다.
- Subagent는 항상 `summary`, `changed_files`, `evidence`, `risks`, `report_file`, `reviewer_decision`을 3개 항목 이하 요약으로 제출한다.

## `pogo-subagent-auto`/Hook 정합성

- `pogo-subagent-auto`는 hook이 Subagent를 직접 spawn하는 기능이 아니다.
- Hook은 정책 상태 조회/차단만 처리하고, Subagent 실행은 메인 오케스트레이터가 `multi_agent` 도구로 직접 시작한다.
- `git commit/push/merge` 단계는 `pogo-policy`/evidence 조건을 충족해야 하며, 이 작업은 별도 지침(`safe-git-automation`, `pogo-subagent-auto`, `pogo-verifier`)의 규칙을 따라 수행한다.

## 기본 작업 방식

1. 범위를 3~5줄로 고정한다: 의도, 범위, 제약, 검증 포인트를 확인한다.
2. 실패/재작업 가능성이 큰 영역은 먼저 계획을 잡고 Subagent 배분을 수행한다.
3. 변경 후 결과를 증거로 정리한다.

### Subagent 선택 기본값

- 구현/수정/리팩터링: `pogo-bug-agent`, `pogo-security-agent`, `pogo-verifier`, `pogo-tester` 등을 조건부 사용.
- 계획/요구사항 충돌 판단이 필요한 변경: `pogo-planner`와 함께 plan 방식 점검.

## 검증 계약

- AGENTS 정책을 위반하지 않는 범위에서만 실행한다.
- 모든 작업은 실행 가능한 검증 포인트를 `pogo`가 제시하고 증거를 남긴다.
- 증거가 없으면 완료로 간주하지 않는다.
