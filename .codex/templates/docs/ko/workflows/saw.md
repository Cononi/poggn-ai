# SAW 초저토큰 단일 워크플로우

$saw는 작은 변경을 최소 컨텍스트로 끝내기 위한 모드입니다.

v16부터 SAW는 검증을 생략하지 않습니다.

차이는 검증을 agent chain으로 하지 않고 script gate로 한다는 점입니다.

## 핵심 목적

```text
primary agent 하나
TASK 하나
필요 skill만 자동 선택
quality, test, security는 script gate
commit 하나로 완료 추적
```

## 검증 원칙

SAW는 테스트와 보안 검사를 건너뛰지 않습니다.

다만 아래처럼 범위를 줄입니다.

```text
문서만 변경: quality + security
코드 변경: quality + test + security
```

코드가 바뀌었는데 test command가 없으면 gate는 실패합니다.

이 경우 `.codex/state/verify.json`에 명령을 추가합니다.

```json
{
  "commands": ["npm run test", "npm run typecheck"]
}
```

## MAW와 차이

MAW는 큰 작업을 기능 lane으로 분해합니다.

```text
order backend lane
payment backend lane
frontend checkout lane
test lane
security lane
```

SAW는 그렇게 하지 않습니다.

```text
T001 dto mapping fix
primary agent: backend
skills: spring-boot, api-contract, verify-gate
```

## 언제 SAW를 쓰나요?

- 단일 버그 수정
- DTO 필드 매핑 수정
- 작은 API 응답 수정
- 작은 컴포넌트 props 정리
- 테스트 하나 보완
- 문서 한 부분 수정
- 파일 몇 개 안의 좁은 리팩토링

기능이 둘 이상이면 MAW를 사용합니다.

## 사용법

계획만 봅니다.

```text
$codex-saw suggest --text "주문 응답 DTO totalPrice 매핑 오류 수정"
```

workflow와 TASK 하나를 만듭니다.

```text
$codex-saw init --title dto-fix --branch hotfix/dto-fix --text "dto 수정"
```

다음 작업만 짧게 봅니다.

```text
$codex-saw prompt
```

작업 후 검증을 실행합니다.

```text
$codex-verify gate --for-ai
```

통과하면 commit으로 완료합니다.

```text
$codex-task commit T001 --message "fix dto mapping"
```

commit 명령은 staged verify gate를 다시 실행합니다.

## 후속 TASK

gate가 실패하면 필요한 경우에만 후속 TASK를 만듭니다.

```text
$codex-saw followup --kind refactor --title "duplicate cleanup"
$codex-saw followup --kind test --title "missing regression test"
$codex-saw followup --kind security --title "auth rule check"
```

## 토큰 절약 원리

SAW는 아래를 하지 않습니다.

```text
여러 agent chain 기본 생성 안 함
여러 TASK 기본 생성 안 함
lane, worktree, CSV 생성 안 함
긴 TASKS.md 직접 판독 안 함
QA agent에게 장문 판단을 맡기지 않음
```

대신 script 결과만 짧게 봅니다.

```text
$codex-state summary --for-ai
$codex-saw prompt
$codex-verify gate --for-ai
$codex-task trace --for-ai
```
