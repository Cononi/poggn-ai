# Agent와 skill 추가

agent는 .codex/agents/{name}.toml에 추가합니다.

필수 필드입니다.

- name
- description
- model
- model_reasoning_effort
- developer_instructions

skill은 .codex/skills/{name}/SKILL.md에 추가합니다.
SKILL.md에는 front matter의 name과 description이 있어야 합니다.

추가 후 codex_skills.py 또는 codex_agents.py 추천 규칙을 갱신합니다.
언어 전환에도 반영하려면 .codex/templates/i18n.json도 갱신합니다.

검증 명령입니다.

```text
$codex-agents check
$codex-skills list
```

## 구현 agent로 확장하기

새 agent가 실제 산출물을 만드는 역할이면 구현 agent입니다.

예를 들어 `mobile`, `crawler`, `ml` agent를 추가할 수 있습니다.

```text
$codex-extend check agent --name mobile --purpose "mobile UI 구현"
```

중복이 없으면 agent를 만든 뒤 role 설정에 추가합니다.

```text
.codex/state/agent_roles.json
```

feature별로 여러 lane을 만들 agent는 여기에 넣습니다.

```json
"feature_implementation_agents": ["backend", "frontend", "mobile"]
```

프로젝트 단위로 한 번만 도는 agent는 여기에 넣습니다.

```json
"single_implementation_agents": ["devops", "docs"]
```
