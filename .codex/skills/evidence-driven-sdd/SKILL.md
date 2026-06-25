---
name: evidence-driven-sdd
description: 기능·API·데이터 변경 전에 검증 가능한 요구사항과 완료 증거를 정의한다. 신규 기능, 비즈니스 규칙 변경, 고위험 수정, Spec·테스트·Release 연결이 필요할 때 사용한다.
metadata:
  version: "2.0"
---

# Evidence-Driven SDD

## 목적

사람과 에이전트가 같은 완료 기준으로 기능을 구현하게 한다.
문서의 양보다 확인 가능한 요구사항과 실행 증거를 우선한다.

## 사용 시점

다음 중 하나라도 해당하면 이 스킬을 사용한다.

- 사용자에게 보이는 동작이 바뀐다.
- API, 데이터 모델, 비즈니스 규칙이 바뀐다.
- 인증, 권한, 보안, 결제, 개인정보를 다룬다.
- 여러 모듈 또는 외부 시스템에 영향을 준다.
- 구현 전에 범위와 완료 조건을 합의해야 한다.

오타, 포맷팅, 주석처럼 외부 동작이 변하지 않는 수정은 Issue와 commit만으로 처리할 수 있다.

## 파일 로딩 원칙

이 파일만 먼저 읽는다. 필요한 경우에만 다음 문서를 추가로 읽는다.

- Spec 작성·수정: `references/spec-template.md`
- Release 전달 기록 작성: `references/pr-template.md`

관련 없는 참조 문서를 한꺼번에 읽지 않는다.

## 저장 위치

```text
docs/specs/<tracker-id>-<kebab-case-title>/spec.md
```

예시:

```text
docs/specs/0034-user-registration/spec.md
docs/specs/PAY-421-refund-idempotency/spec.md
```

완료 후 폴더를 이동하거나 삭제하지 않는다. `spec.md`의 `status`만 갱신한다.

```text
draft → approved → implementing → verifying → done
```

예외 상태:

```text
blocked | superseded
```

## 작업 절차

### 1. 현재 상태 확인

코드 작성 전에 관련 소스, 테스트, 계약, 데이터 모델, 빌드 명령을 직접 확인한다.
확인하지 못한 내용은 사실처럼 쓰지 않는다.

### 2. 변경 등급 결정

- `T0`: 외부 동작 변화가 없는 사소한 수정. 별도 Spec 생략 가능.
- `T1`: 기능, API, 데이터, 비즈니스 규칙 변경. Spec 필수.
- `T2`: 보안, 결제, 개인정보, 삭제, 마이그레이션, 동시성, 호환성 파괴. 롤백·관측성·복구 계획 필수.

### 3. Spec 작성

`references/spec-template.md`를 사용한다.
최소한 다음을 명확히 한다.

- 문제와 기대 결과
- 포함 범위와 제외 범위
- 요구사항과 불변 조건
- 검증 가능한 Acceptance Criteria
- 실패 동작과 잔여 위험

Acceptance Criteria에는 고유 ID를 붙인다.

```text
AC-001
AC-002
INV-001
```

### 4. 미결 사항 표시

결정되지 않은 내용을 숨기거나 임의 구현하지 않는다.

```text
[OPEN] 결정이 필요한 사항
[ASSUMPTION] 가정과 영향
[UNKNOWN] 아직 확인하지 못한 사실
```

차단되는 `[OPEN]` 항목이 있으면 구현 완료로 처리하지 않는다.

### 5. 최소 변경 구현

- Spec 범위 밖 리팩터링을 끼워 넣지 않는다.
- 추가 변경이 필요하면 Spec을 먼저 갱신한다.
- 공개 계약이 바뀌면 계약 파일과 테스트도 함께 수정한다.
- 각 작업과 테스트를 AC 또는 INV ID에 연결한다.

### 6. 최종 상태 검증

가능하면 최종 diff 또는 최종 commit에서 검증한다.
허용되는 결과는 다음 네 가지뿐이다.

```text
PASS | FAILED | PARTIAL | NOT RUN
```

`PASS`에는 실행 명령, 대상 commit, 핵심 결과를 기록한다.
실행하지 않은 테스트를 `PASS`라고 쓰지 않는다.

### 7. 전달 기록 연결

- Issue: 문제, 맥락, 우선순위
- Spec: 원하는 동작과 완료 기준
- Test/Contract: 실행 가능한 검증
- Release: 실제 변경, 위험, 검증 증거
- Commit: 세부 변경 이력
- Release Note: 사용자·운영자에게 의미 있는 변화

외부 동작 변화가 없으면 Release Note는 생략할 수 있다.

## 완료 조건

다음을 모두 만족해야 `status: done`으로 변경한다.

1. 승인된 원하는 동작이 명확하다.
2. 모든 AC와 INV가 구현 및 증거에 연결되어 있다.
3. 필수 검증이 최종 변경 상태에서 실행되었다.
4. 미실행 검증과 잔여 위험이 기록되었다.
5. API, 데이터, 보안, 호환성 영향이 처리되었다.
6. 필요한 롤백, 마이그레이션, 관측성이 준비되었다.
7. Release note 또는 commit이 Issue와 Spec을 연결한다.
8. 차단되는 `[OPEN]` 항목이 없다.

코드 작성만으로는 완료가 아니다.

## 정직성 규칙

- 확인하지 않은 파일, API, 테스트, 버전, 실행 결과를 만들지 않는다.
- 요구사항과 코드가 다를 때 코드를 자동으로 정답 처리하지 않는다.
- 실패하거나 생략한 검증을 숨기지 않는다.
- 구현 편의를 위해 Acceptance Criteria를 몰래 약화하지 않는다.
- 같은 내용을 Spec, 별도 tasks 문서, 별도 qa 문서에 중복 저장하지 않는다.

## 최종 보고 형식

```md
## 구현

- AC-001: 구현 내용과 변경 경로
- AC-002: 구현 내용과 변경 경로

## 검증

- Command: `실행 명령`
- Commit: `commit hash 또는 working tree`
- Result: PASS | FAILED | PARTIAL | NOT RUN

## 남은 위험

- 없으면 `None`
- 있으면 영향과 후속 조치
```
