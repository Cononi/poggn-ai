# TASK 완료 이벤트와 후속 agent

MAW는 모든 agent를 한 번에 고정 실행하지 않습니다.

TASK가 commit과 연결되어 `[x]`가 되면 이벤트가 발생합니다.

그 이벤트가 필요한 후속 agent만 생성합니다.

예:

```text
구현/order 완료
-> test_writer/order
-> test_runner/order
-> qa/order
-> 필요 시 refactor/order
-> 필요 시 security/order
```

payment가 아직 진행 중이어도 order 검증은 시작할 수 있습니다.

구현 agent는 다음 ready 구현 TASK를 계속 진행합니다.

후속 agent는 자신의 역할만 수행합니다.

test_writer는 테스트 코드를 작성하지만 실행하지 않습니다.

test_runner는 테스트를 실행하지만 제품 코드를 구현하지 않습니다.

qa는 사용자 흐름과 회귀 위험을 검토합니다.

refactor는 동작 보존 리팩토링만 수행합니다.

security는 보안 위험만 검토합니다.

ready queue 확인:

```text
$codex-pipeline ready --for-ai
```

후속 worker 확인:

```text
$codex-events workers --for-ai
```
