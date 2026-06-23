# Poggn AI Codex Automation Template

이 저장소는 Codex를 Git 기반 개발 흐름에 안전하게 연결하기 위한 자동화
템플릿입니다. 다른 프로젝트 루트에 `.codex`, `.agents`, `.github` 구성을
복사해 두고, Codex가 agent, skill, TASK, lane, commit, gate를 일관된 방식으로
다루게 하는 것이 목적입니다.

핵심 목표는 AI가 모든 상태를 기억하게 만드는 것이 아닙니다. 반복 가능한 상태
계산, 검증, 추적, 문서 생성을 script가 맡고, Codex는 현재 작업에 필요한
짧은 결과만 읽습니다. 이 구조는 토큰 사용량을 줄이고, TASK와 commit 사이의
추적성을 유지하며, 검증 없이 완료되는 변경을 막습니다.

## 이 템플릿이 해결하는 문제

- 큰 요청을 여러 기능 lane으로 나누어 병렬 작업합니다.
- 작은 요청은 SAW 흐름으로 한 TASK와 한 commit에 묶습니다.
- agent는 역할, skill은 절차, lane은 실행 단위로 분리합니다.
- quality, security, verify gate를 commit 전후 흐름에 둡니다.
- TASK, lane, commit, event를 JSONL 상태로 남겨 rollback 근거를 만듭니다.
- PR template, squash merge, required check로 GitHub 운영 규칙을 고정합니다.

## 빠른 시작

프로젝트 루트에 이 템플릿을 둔 뒤 shortcut link를 준비합니다.

```bash
python3 .codex/script/setup_links.py
```

현재 언어와 상태를 확인합니다.

```text
$codex-language status
$codex-state summary --for-ai
$codex-context pack --for-ai
```

작은 단일 변경은 SAW로 시작합니다.

```text
$codex-saw suggest --text "dto 필드 매핑 오류 수정"
```

큰 기능은 MAW로 분해합니다.

```text
$maw spring boot 쇼핑몰 order payment rest api swagger jpa
```

검증은 아래 gate를 기본으로 사용합니다.

```text
$codex-quality gate --for-ai
$codex-security gate
$codex-verify gate --for-ai
```

템플릿 자체 테스트는 외부 패키지 없이 실행할 수 있습니다.

```bash
python3 .codex/script/codex_test_runner.py --for-ai
```

## 전체 아키텍처

작업은 아래 계층으로 흐릅니다.

```text
사용자 요청
  -> risk/context/budget 확인
  -> agent 추천
  -> skill 선택
  -> TASK 생성
  -> lane 생성
  -> worktree 또는 단일 branch 작업
  -> quality/security/test/verify gate
  -> commit 연결
  -> PR, squash merge, release note
```

주요 개념은 네 가지입니다.

- `agent`: 작업자의 역할입니다.
- `skill`: agent가 읽는 반복 가능한 절차입니다.
- `lane`: 실제 병렬 실행 단위입니다.
- `TASK`: commit과 연결되는 추적 단위입니다.

예를 들어 order API와 payment API는 모두 backend agent를 쓸 수 있습니다. 그러나
두 기능은 서로 다른 lane으로 나뉘고, 각 lane은 별도 worktree와 branch에서
실행될 수 있습니다. Spring Boot, JPA, OpenAPI는 agent가 아니라 backend agent가
사용하는 skill입니다.

## 디렉터리 구조

```text
.codex/
  AGENTS.md              저장소 작업 규칙
  agents/*.toml          agent 역할 정의
  skills/*/SKILL.md      반복 절차와 검증 기준
  script/*.py            상태 계산, gate, 문서, git 자동화
  state/*.json           언어, 예산, 검증, runtime 상태
  tests/test_*.py        템플릿 내부 테스트
.agents/                 Codex agent/skill link 대상
.github/
  PULL_REQUEST_TEMPLATE.md
  workflows/codex-verify.yml
docs/                    상세 문서와 운영 설명
README.md                전체 입문 문서
```

자세한 파일 설명은 [docs/02-file-tree.md](docs/02-file-tree.md)를 봅니다.

## Agent

agent는 기능명이 아니라 책임입니다. 같은 agent type도 여러 lane에 배정될 수
있습니다. 예를 들어 `backend` agent가 order lane과 payment lane에서 각각 다른
worker로 실행될 수 있습니다.

대표 agent는 아래와 같습니다.

| Agent | 책임 |
|---|---|
| `architecture` | 요구사항, API 계약, 도메인 경계 설계 |
| `backend` | 서버 API, 서비스, 도메인 로직 구현 |
| `frontend` | 화면, 컴포넌트, 클라이언트 상태 구현 |
| `database` | schema, migration, index, query 검토 |
| `test` | unit, integration, regression test 작성 |
| `qa` | 수용 기준, 사용자 흐름, 품질 판단 |
| `security` | 인증, 권한, secret, 취약점 검토 |
| `refactor` | 동작 보존 리팩토링과 중복 제거 |
| `devops` | CI/CD, Docker, GitHub Actions, GitLab CI |
| `docs` | README, wiki, API 문서, release note |
| `git` | branch, commit, diff, rollback, PR 준비 |

agent 정의는 `.codex/agents/*.toml`에 있습니다. 전체 설명은
[docs/agents/index.md](docs/agents/index.md)를 봅니다.

## Skill

skill은 agent가 작업할 때 읽는 절차입니다. 병렬 실행 단위가 아니며, 특정
프레임워크나 품질 기준을 다룰 때 선택됩니다.

대표 skill은 아래와 같습니다.

| Skill | 목적 |
|---|---|
| `spring-boot` | Spring Boot 서버 구현 절차 |
| `jpa` | entity, repository, transaction, query 절차 |
| `api-contract` | request, response, error 계약 정리 |
| `openapi-swagger` | Swagger 또는 OpenAPI 문서화 |
| `frontend-typescript` | TypeScript 기반 frontend 구현 기준 |
| `frontend-component-architecture` | primitive, compound, feature 구조 설계 |
| `quality-gate` | 대형 파일, 중복, 복잡도, 보안 흔적 검사 |
| `security-gate` | secret, token, 권한, 입력 검증 점검 |
| `refactor-clean-code` | 동작 보존 리팩토링 절차 |
| `task-trace` | TASK, lane, commit 추적 |
| `docs` | README, 운영 문서, release note 작성 |
| `ci-cd` | GitHub Actions, GitLab CI, 배포 파이프라인 |

skill 파일은 `.codex/skills/{name}/SKILL.md`에 있습니다. 더 자세한 목록은
[docs/skills/index.md](docs/skills/index.md)를 봅니다.

## Workflow

### SAW

SAW는 작은 단일 변경을 위한 micro workflow입니다.

```text
primary agent 하나
TASK 하나
필요 skill만 선택
quality, test, security는 script gate
commit 하나로 완료 추적
```

문서만 바꾸면 quality와 security를 확인합니다. 코드가 바뀌면 test command가
필요합니다. test command를 찾지 못하면 `.codex/state/verify.json`에 명령을
추가해야 합니다.

자세한 내용은 [docs/workflows/saw.md](docs/workflows/saw.md)를 봅니다.

### MAW

MAW는 큰 작업을 feature lane으로 나누는 workflow입니다.

```text
agent = 역할
skill = 절차
lane = 병렬 실행 단위
wave = 한 번에 실행하고 병합할 lane 묶음
pipeline = lane dependency graph
epic = 전체 목표
```

구현 lane이 끝나면 downstream lane이 준비됩니다.

```text
implement -> test -> qa -> refactor -> security
```

ready lane만 실행하고, 완료된 lane은 다시 pipeline에 반영합니다. 전체 작업이
커도 한 wave와 한 PR의 크기를 제한해 검토 가능한 단위로 나눕니다.

자세한 내용은 [docs/workflows/maw.md](docs/workflows/maw.md)를 봅니다.

## 주요 Script

`.codex/script` 아래 Python 파일은 Codex 대신 상태를 계산하는 실행 단위입니다.
AI가 긴 문서를 반복해서 읽지 않도록 script가 짧은 JSON 또는 요약을 출력합니다.

| Script | 기능 |
|---|---|
| `codex_state.py` | workflow, TASK, VERSION 상태 관리 |
| `codex_task_git.py` | TASK와 commit 연결, diff, revert |
| `codex_lanes.py` | MAW lane과 worktree 관리 |
| `codex_pipeline.py` | ready queue와 downstream pipeline 관리 |
| `codex_waves.py` | MAW lane을 실행 wave로 분할 |
| `codex_work_items.py` | 요구사항을 기능 TASK로 분해 |
| `codex_design_gate.py` | 제품 유형, runtime, framework, stack 계약 분류 |
| `codex_saw.py` | SAW micro workflow 생성 |
| `codex_verify.py` | TASK 완료 전 최소 검증 |
| `codex_quality.py` | 코드 품질, TSX, 중복 검사 |
| `codex_security.py` | secret, token, private key 검사 |
| `codex_test_runner.py` | 신뢰된 `.codex/tests/test_*.py` 전용 runner |
| `codex_context.py` | 현재 상태와 변경 파일 요약 압축 |
| `codex_budget.py` | SAW/MAW 파일 수와 줄 수 예산 검사 |
| `codex_wiki.py` | docs HTML index 생성 |
| `codex_shortcuts.py` | `$codex-*` shortcut 실행 |

전체 script 설명은 [docs/scripts/index.md](docs/scripts/index.md)를 봅니다.

## 상태와 추적성

TASK는 완료 증거로 commit을 가져야 합니다. commit message는 conventional
commit 제목, 변경 이유, 범위, 검증 결과를 포함합니다.

상태 원본은 JSON/JSONL로 관리됩니다.

```text
.codex/state/state.json
.codex/state/tasks.jsonl
.codex/state/lanes.jsonl
.codex/state/commits.jsonl
.codex/state/events.jsonl
```

TASK가 완료되려면 status가 done이고, lane이 done 또는 merged이며, 연결 commit이
있어야 합니다. 이 기준을 만족하지 않으면 사람이 보는 요약이 완료로 보이지
않습니다.

자세한 내용은
[docs/workflows/task-commit-trace.md](docs/workflows/task-commit-trace.md)를 봅니다.

## 품질과 보안 기준

품질 gate는 완료 commit 전에 실행합니다.

- 소스 파일은 200줄을 넘지 않도록 관리합니다.
- 프론트 컴포넌트 파일은 160줄 이하를 목표로 합니다.
- React 신규 UI는 `.tsx`를 사용합니다.
- 중복 코드와 중복 기능을 만들지 않습니다.
- secret, token, password 흔적은 error로 취급합니다.

보안 gate는 secret, token, private key, 권한, 입력 검증, 위험한 redirect나
CORS 설정을 확인합니다. `.env` 내용이나 실제 credential은 문서에 적지 않습니다.

```text
$codex-quality gate --for-ai
$codex-security gate
$codex-verify gate --for-ai
```

자세한 기준은 [docs/quality/code-quality.md](docs/quality/code-quality.md)와
[docs/quality/security.md](docs/quality/security.md)를 봅니다.

## GitHub 운영 정책

이 저장소는 PR 중심 운영을 전제로 합니다.

- 작업 commit에는 PR 번호를 강제하지 않습니다.
- PR 본문은 Why, What Changed, Verification, Risk and Rollback을 포함합니다.
- 리뷰 초점이 필요하면 Review Guide를 추가합니다.
- 기본 merge 전략은 squash merge입니다.
- 최종 squash merge commit 제목 끝에는 `(#번호)` 형식으로 PR 번호를 남깁니다.
- `main`에는 `codex-verify` required status check를 둡니다.

PR template은 [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)에
있고, workflow는 [.github/workflows/codex-verify.yml](.github/workflows/codex-verify.yml)에
있습니다.

## 문서와 확장

상세 문서는 `docs/`에 있습니다.

- [docs/00-overview.md](docs/00-overview.md): 전체 개념
- [docs/01-architecture.md](docs/01-architecture.md): 구조 원리
- [docs/03-quick-start.md](docs/03-quick-start.md): 빠른 시작
- [docs/agents/index.md](docs/agents/index.md): agent 설명
- [docs/skills/index.md](docs/skills/index.md): skill 설명
- [docs/scripts/index.md](docs/scripts/index.md): script 설명
- [docs/workflows/maw.md](docs/workflows/maw.md): MAW workflow
- [docs/workflows/saw.md](docs/workflows/saw.md): SAW workflow
- [docs/quality/code-quality.md](docs/quality/code-quality.md): 품질 기준
- [docs/quality/security.md](docs/quality/security.md): 보안 기준

새 agent나 skill을 만들기 전에는 중복을 먼저 검사합니다.

```text
$codex-extend scan --text "요청" --for-ai
```

확장 절차는 [docs/customization/add-agent-skill.md](docs/customization/add-agent-skill.md)를
봅니다.

## 운영과 rollback

운영 문서는 성공 경로만 말하지 않습니다. 실패했을 때 어느 commit 또는 TASK를
되돌릴지도 남겨야 합니다.

- TASK 단위 diff는 `$codex-task diff`로 확인합니다.
- TASK 단위 되돌리기는 `$codex-task revert-task`를 사용합니다.
- PR merge 후에는 squash commit 또는 PR 번호를 rollback 기준으로 삼습니다.
- security gate가 실패하면 TASK를 완료하지 않습니다.
- 검증하지 않은 테스트나 동작은 PASS로 기록하지 않습니다.

문제가 생기면 [docs/troubleshooting.md](docs/troubleshooting.md)를 먼저 확인합니다.
