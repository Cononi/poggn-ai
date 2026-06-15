# 이벤트 기반 MAW

MAW는 TASK 완료 이벤트를 기준으로 후속 agent를 선택합니다.

구현 agent는 구현만 담당합니다.

테스트 코드는 test_writer가 작성합니다.

테스트 실행은 test_runner가 담당합니다.

QA, refactor, security는 변경 내용과 위험도에 따라 실행됩니다.

모든 후속 agent가 항상 도는 것은 아닙니다.

```text
code changed -> test_writer, test_runner
public API or large change -> qa
large maintainability risk -> refactor
payment, auth, token, secret -> security
```

TASK가 `[x]` 완료되면 event bus가 후속 lane을 만듭니다.

후속 agent가 도는 동안 구현 agent는 다음 ready TASK를 계속 진행합니다.

```text
구현/order 완료
-> test_writer/order, qa/order 준비

구현/payment 진행 중
-> 계속 구현 가능
```

ready queue 확인:

```text
$codex-pipeline ready --for-ai
```

worker 확인:

```text
$codex-events workers --for-ai
```
