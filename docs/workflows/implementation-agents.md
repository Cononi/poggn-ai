# 구현 agent 원칙

MAW에서 `backend`는 예시일 뿐입니다.

구현 agent는 자기 영역의 산출물을 만드는 agent입니다.

기본 구현 agent는 다음과 같습니다.

```text
backend
frontend
database
integration
devops
docs
performance
```

custom agent도 `.codex/state/agent_roles.json`에 등록하면 구현 agent가 됩니다.

구현 TASK가 `[x]` 완료되면 event bus가 후속 agent를 선택합니다.

```text
구현/order 완료
-> 필요한 test_writer
-> 필요한 test_runner
-> 필요한 qa
-> 필요한 refactor
-> 필요한 security
```

그동안 다른 구현 agent는 다음 ready TASK를 계속 진행합니다.

```text
frontend/order 검증 중
backend/payment 구현 진행
integration/webhook 구현 진행
```

후속 agent는 무조건 생성하지 않습니다.

변경 파일, 위험도, feature, policy를 보고 필요한 agent만 생성합니다.
