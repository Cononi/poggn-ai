# Agent 설명

agent는 역할입니다. skill이나 기능명이 아닙니다.

- architecture: 요구사항, API 계약, 도메인 경계 설계
- backend: 서버 API, 서비스, 도메인 로직 구현
- frontend: 화면, 컴포넌트, 클라이언트 상태 구현
- database: 스키마, migration, index, 쿼리 검토
- test: 단위 테스트, 통합 테스트, 회귀 테스트 생성
- qa: 수용 기준, 사용자 흐름, 품질 gate 판단
- security: 인증, 권한, secret, 취약점 검토
- refactor: 동작 보존 리팩토링과 중복 제거
- devops: CI/CD, Docker, GitHub Actions, GitLab CI
- git: branch, commit, diff, rollback, PR/MR 준비
- docs: README, wiki, API 문서, 릴리즈 노트
- integration: 외부 API, 이벤트, 메시징 연동
- performance: 느린 쿼리, 캐시, latency 검토

agent 파일은 .codex/agents/*.toml입니다.
모든 agent에는 name, description, model, model_reasoning_effort가 있어야 합니다.

## /agent 와 $codex-agents

/agent 는 실행 중인 subagent thread를 전환하거나 확인하는 용도입니다.
아직 spawn된 subagent가 없으면 목록이 비어 보일 수 있습니다.

프로젝트에 등록된 custom agent는 아래 명령으로 확인합니다.

```text
$codex-agents list
$codex-agents check
```

## MAW에서 같은 agent 여러 개 실행

같은 agent type을 여러 lane에 배정할 수 있습니다.

```text
L002 backend Order REST API
L003 backend Payment REST API
```

이 경우 backend agent가 두 worker로 동시에 실행됩니다.

각 worker는 다른 worktree와 branch를 사용합니다.

## downstream agent

구현이 끝난 lane은 downstream agent로 전달됩니다.

```text
implement -> test -> qa -> refactor -> security
```

QA, refactor, security는 upstream lane의 commit과 diff를 우선 확인합니다.
전체 repo를 다시 읽지 않습니다.
