# 파일 트리

대표 구조입니다.

```text
.codex/
  AGENTS.md
  config.toml
  hooks.json
  agents/
  hooks/
  rules/
  script/
  skills/
  state/
  templates/
  tests/
.agents/
  README.md
docs/
  index.html
  *.md
.codex-state/
  {날짜}/vN-{제목}/
    TASKS.md
    state.json
    tasks.jsonl
    lanes.jsonl
    commits.jsonl
    events.jsonl
.worktrees/
  {workflow}/l001/
```

.codex는 Codex 동작에 필요한 템플릿 원본입니다.
.agents는 Codex skill 탐색 경로를 맞추기 위한 연결 지점입니다.
docs는 사용자를 위한 wiki 문서입니다.
.codex-state는 실행 중인 workflow의 원본 상태입니다.
.worktrees는 병렬 lane별 작업 공간입니다.

일반 프로젝트 작업 중에는 .codex 수정을 피합니다.
.codex를 수정해야 할 때만 $codex-edit-mode on을 사용합니다.
