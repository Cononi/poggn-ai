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

## 구현 agent 일반화

`backend`만 구현 agent가 아닙니다.

아래 agent도 구현 producer가 될 수 있습니다.

```text
backend, frontend, database, integration, devops, docs, performance
```

feature 단위 구현 agent는 feature별 lane을 만듭니다.

```text
backend/order
frontend/order
integration/payment
```

single 구현 agent는 프로젝트 단위 lane을 만듭니다.

```text
devops/project
docs/project
performance/project
```

완료 이벤트는 `implement` stage 전체에 반응합니다.

```text
구현 TASK [x]
-> 필요한 test_writer, test_runner, qa, refactor, security 생성
```

역할 구분은 아래 파일에서 조정합니다.

```text
.codex/state/agent_roles.json
.codex/state/event_policy.json
```
