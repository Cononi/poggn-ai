# Agent 선택 원리

Codex는 요청 텍스트를 보고 agent를 추천합니다.
사용자는 추천 목록에서 고르거나 agent를 추가할 수 있습니다.

예시입니다.

```text
$codex-agents recommend --text "쇼핑몰 order payment rest api"
```

추천 예시는 architecture, backend, database, test, qa, security입니다.
frontend가 필요한 화면 작업이면 frontend도 추가합니다.

agent 수를 먼저 묻지 않는 이유는 사용자가 병렬 개수를 알기 어렵기 때문입니다.
대신 목적에 맞는 agent를 고르면 work_items가 기능 lane을 만듭니다.

새 agent는 기본적으로 자동 생성하지 않습니다.
필요하면 $codex-edit-mode on 후 .codex/agents에 명시적으로 추가합니다.
