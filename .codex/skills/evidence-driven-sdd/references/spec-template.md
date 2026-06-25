# Spec Template

```md
---
id: SPEC-0034
title: User registration
status: draft
risk: T1
issue: "#34"
owners:
  - backend
created: YYYY-MM-DD
updated: YYYY-MM-DD
superseded_by: null
---

# SPEC-0034: User registration

## Summary

원하는 결과를 한 문장으로 적는다.

## Problem and Expected Outcome

### Problem

현재 문제와 영향을 받는 대상을 적는다.

### Expected Outcome

완료 후 관찰할 수 있는 결과를 적는다.

## Current Behavior

직접 확인한 근거만 경로와 함께 적는다.

- `path/to/source`: 현재 동작
- `path/to/test`: 현재 검증 범위

확인하지 못한 내용은 `[UNKNOWN]`으로 표시한다.

## Scope

### In Scope

- 이번 변경에 포함되는 동작

### Out of Scope

- 의도적으로 제외하는 동작

## Requirements and Invariants

- REQ-001: 요구사항
- INV-001: 깨지면 안 되는 조건

## Acceptance Criteria

### AC-001: 정상 처리

**Given** 사전 조건
**When** 수행하는 행동
**Then** 관찰 가능한 결과

### AC-002: 실패 처리

**Given** 사전 조건
**When** 실패를 유발하는 행동
**Then** 오류, 상태 변화, 부작용 여부

## Contract and Data

해당하지 않으면 `N/A — 이유`를 적는다.

- API 요청·응답·오류:
- 인증·권한:
- 스키마·마이그레이션:
- 호환성:
- 개인정보·보존 정책:

## Failure, Security, and Operations

해당하지 않으면 `N/A — 이유`를 적는다.

- 예상 실패 모드:
- 재시도·멱등성:
- 로그·민감정보 마스킹:
- 지표·알람·추적:
- 롤백·복구:

## Decisions and Uncertainty

- DEC-001: 결정과 이유
- [ASSUMPTION] 가정과 영향
- [OPEN] 미결 사항과 차단 여부

## Implementation Plan

- [ ] AC-001: 결과 중심 작업
- [ ] AC-002: 결과 중심 작업
- [ ] INV-001: 불변 조건 검증

## Verification Matrix

| ID | Test or Evidence | Command / Method | Result | Notes |
|---|---|---|---|---|
| AC-001 | 테스트 이름 | `command` | NOT RUN | |
| AC-002 | 테스트 이름 | `command` | NOT RUN | |
| INV-001 | 검증 방법 | `command` | NOT RUN | |

## Delivery Links

- Issue:
- Release:
- ADR:
- API Contract:
- Release Note:

## Completion

- [ ] 모든 AC·INV가 증거와 연결됨
- [ ] 최종 변경 상태에서 필수 검증 실행
- [ ] 미실행 검증과 잔여 위험 기록
- [ ] API·데이터·보안·호환성 검토
- [ ] 필요한 롤백·마이그레이션 검증
- [ ] Release note 또는 commit이 Issue와 Spec을 연결
- [ ] 차단되는 `[OPEN]` 없음
```
