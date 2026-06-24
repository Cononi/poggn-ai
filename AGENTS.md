# CODEX 개발 가이드 지침

## 필수 규칙

- 항상 `pogo` skill을 먼저 사용한다.
- 사용자 요청, `AGENTS.md`, 관련 skill, `.codex/agents` 설정이 충돌하면 더 구체적이고 현재 작업에 가까운 지침을 우선한다.
- 스킬 문서는 이름만 보고 추측하지 말고, 작업에 해당하는 `SKILL.md`를 직접 읽고 적용한다.
- 확인하지 않은 파일, 테스트, API, 설정, 실행 결과를 사실처럼 말하지 않는다.

## 작업 시작 판단

작업을 시작할 때 메인 에이전트가 다음을 먼저 판단한다.

1. 요청 의도와 성공 기준이 명확한가.
2. `pogo` 계획으로 충분한가, `evidence-driven-sdd` 계획이 필요한가.
3. 코드 수정/버그/개발이면 Multi Agent(Subagents) 우선으로 나눌 수 있는가.
4. 어떤 전문 스킬을 적용해야 하는가.
5. 어떤 검증 명령이나 증거가 완료 기준이 되는가.

판단 결과는 필요한 경우 짧게 제시한다.

```text
에이전트 방식 판단:
- 추천: Multi Agent 우선 | Single Agent 예외
- 이유: 판단 근거
- 비용/위험: 토큰, 충돌, 불확실성
- 진행: 사용할 skill/agent와 검증 방식
```

## 계획 수립 기준

- `pogo`: T0 수정, 단일 파일 또는 좁은 변경, 외부 동작 변화가 없거나 작고 명확한 작업.
- `evidence-driven-sdd`: 기능, API, 데이터 모델, 비즈니스 규칙, 보안, 결제, 개인정보, 마이그레이션, 동시성, 호환성에 영향을 주는 T1/T2 작업.
- 애매하면 `evidence-driven-sdd` 기준으로 변경 등급을 먼저 정하고, 필요한 최소 Spec과 Acceptance Criteria만 작성한다.
- 계획 비교가 필요하면 `pogo-planner` agent를 사용해 `pogo` 방식과 `evidence-driven-sdd` 방식을 비교하고 메인 에이전트가 최종 결정한다.

## 전문 스킬 라우팅

작업 영역에 맞는 스킬을 함께 사용한다.

- `architecture`: 여러 모듈, 경계, 의존성, public contract, 장기 구조 판단.
- `backend`: API, 서버 도메인 로직, 인증/권한, 데이터 저장, job/queue/integration.
- `front`: 컴포넌트, 화면 상태, form, routing, client API 연동, 접근성/반응형 구현.
- `designer`: 사용자 흐름, 정보 구조, 레이아웃, 시각 계층, UX 상태, 디자인 일관성.
- `security`: 인증, 권한, 입력 검증, 민감 데이터, secret, dependency, 네트워크, 파일, abuse case.
- `safe-database-engineering`: 스키마, SQL, 트랜잭션, 인덱스, 마이그레이션, ORM이 실제 DB 계약에 영향을 주는 작업.
- `safe-git-automation`: 브랜치, worktree, commit, push, PR, 병렬 작업공간, 충돌 복구.
- `pogo-settings`: commit/push/merge 자동화 상태와 언어 모드를 `$pogo-settings` 하위 명령으로 확인 또는 변경.

여러 영역이 걸리면 `architecture`로 경계를 먼저 정하고, `backend`, `front`, `designer`, `security`, `safe-database-engineering`을 병렬 또는 순차로 배치한다.

## Git 자동화 정책

`.codex/state/pogo-settings.json`의 `gitAutomation` 값을 따른다.

- `commit: false`: commit을 자동 수행하지 않으며, 필요하면 `$pogo-settings git commit once`로 1회 허용한다.
- `commit: true`: 작업 완료와 검증 후 현재 작업 범위의 변경만 자동 commit할 수 있다.
- `push: false`: push를 자동 수행하지 않으며, 필요하면 `$pogo-settings git push once`로 1회 허용한다.
- `push: true`: commit이 완료되고 remote/branch가 확인되었을 때 자동 push를 허용한다.
- `merge: false`: merge를 자동 수행하지 않으며, 필요하면 `$pogo-settings git merge once`로 1회 허용한다.
- `merge: true`: 대상 branch, 검증 결과, 충돌 없음이 확인된 경우에만 merge를 허용한다.

모든 git 자동화는 `safe-git-automation` 규칙을 우선한다. 기존 사용자 변경을 섞거나 되돌리지 않는다. destructive command, force push, 보호 규칙 우회, 승인 필요한 원격 작업은 토글이 켜져 있어도 별도 승인 없이는 수행하지 않는다.

Git 식별자는 언어 모드와 분리한다. `lang=ko`여도 branch, tag, commit type/scope, version은 ASCII/영어 관례를 유지하고, commit body, PR 본문, release note 같은 설명문만 한국어로 작성할 수 있다.

작업 commit에는 PR 번호를 강제하지 않는다. PR 번호는 PR 생성 후 확정되므로 최종 squash merge commit 끝에 `(#번호)` 형식으로 남긴다.
작은 PR 본문은 `Summary` 4줄만 기본으로 작성한다.
항목은 `Why`, `What`, `Verify`, `Risk/Rollback`이다.
고위험, migration, API/데이터/보안 변경일 때만 세부 섹션을 추가한다.

버전 관리는 프로젝트별 버전을 기본 정책으로 한다. 단일 프로젝트도 같은 정책을 사용하며, tag는 `<project>-v<semver>` 형식을 쓴다. 예: `web-v1.2.0`, `api-v2.0.3`, `app-v0.4.1`. Git tag는 repo commit을 가리키지만, 최신 tag, version source, release note, rollback 기준은 project 단위로 해석한다.

merge, release, worktree 정리는 별도 단계로 취급한다. main merge와 push가 확인된 뒤 `.codex/script/pogo_release.py status --project <project> --path <path>`와 `notes`로 GitHub Release 계획과 변경 내용을 확인하고, worktree는 `.codex/script/pogo_worktree_cleanup.py`로 clean 상태와 remote 보존을 확인한 뒤 제거한다.

## Multi Agent 운영

Codex 공식 용어는 Subagents다. 사용자가 Multi Agent라고 말하면 Subagents로 해석한다.

- 코드 수정, 버그 수정, 기능 개발, 리팩터링, 테스트 작성, QA, 보안/아키텍처 판단은 Multi Agent를 기본 경로로 사용한다.
- Single Agent는 문서 한두 줄 수정, 단순 질문 답변, 명령 출력 확인, 명확한 단일 파일 T0 변경처럼 Subagent 비용이 이득보다 큰 경우에만 예외로 둔다.
- 기본 모델은 `.codex/agents/*.toml`에 정의된 `gpt-5.3-codex-spark`를 따른다.
- `.codex/agents`의 `model_reasoning_effort`는 기본 `high`로 둔다.
- 워커, 검증, 보안, 아키텍처, 버그 수정 agent는 `model_reasoning_effort = "xhigh"`로 둔다.
- Subagents는 현재 sandbox와 approval 정책을 상속한다.
- 병렬 작성은 충돌 위험이 있으므로 메인 에이전트가 작업 단위와 파일 경계를 정한다.
- Subagent 결과는 원시 로그가 아니라 결정, 변경 범위, 검증 증거, 남은 위험으로 요약한다.
- 최종 병합, 충돌 판단, 사용자 보고는 메인 에이전트가 책임진다.

재사용 가능한 agent는 `.codex/agents/`에 둔다.

- `pogo-planner`: 계획 비교와 작업 분해.
- `pogo-worker`: 승인된 단일 작업 단위 구현.
- `pogo-bug-agent`: 버그 재현, 원인 축소, 수정, 회귀 검증.
- `pogo-architecture-agent`: 구조, 경계, 의존성, contract 검토.
- `pogo-backend-agent`: API, 도메인, DB 접근, 서버 검증.
- `pogo-front-agent`: 화면, 상태, 접근성, 반응형, 프론트 검증.
- `pogo-designer-agent`: UX, 정보 구조, 레이아웃, 시각 일관성.
- `pogo-security-agent`: 보안 위협 모델링과 취약점 검토.
- `pogo-verifier`: 최종 검증 판단.

버그 수정은 `pogo-bug-agent`를 우선 사용하고, 구현은 `pogo-worker` 또는 영역별 agent로 나눈 뒤 `pogo-verifier`에 넘긴다. 보안 영향이 있는 구현은 `pogo-security-agent` 검토를 먼저 거친 뒤 `pogo-verifier`에 넘긴다.

## 구현 규칙

- 필요한 부분만 수정한다.
- 기존 코드 스타일, 파일 구조, helper API, 테스트 패턴을 따른다.
- 관련 없는 리팩터링, 포맷 변경, 죽은 코드 삭제를 끼워 넣지 않는다.
- 새 추상화는 실제 복잡도나 중복을 줄일 때만 만든다.
- 변경 때문에 고아가 된 import, 변수, 함수, 클래스, 파일은 제거한다.
- 프론트 작업은 기존 디자인 시스템과 `designer`/`front` 기준을 같이 확인한다.
- 백엔드와 DB 작업은 서버 검증, 권한, 트랜잭션, 마이그레이션 안전성을 확인한다.
- 보안 관련 작업은 클라이언트 검증만으로 완료 처리하지 않는다.

## 검증과 보고

- 작업 전 성공 기준과 검증 방법을 정한다.
- 가능한 경우 변경을 재현하거나 보호하는 테스트를 작성/수정한다.
- 실행하지 않은 테스트를 PASS라고 말하지 않는다.
- 검증 결과는 `PASS`, `FAILED`, `PARTIAL`, `NOT RUN` 중 하나로 보고한다.
- 판단 불가한 Subagent 검증은 `UNABLE_TO_JUDGE`로 받고, 메인 에이전트가 추가 증거 또는 재작업을 결정한다.
- 최종 보고에는 변경 파일, 실행한 명령, 결과, 남은 위험을 포함한다.

## Git 안전 규칙

- commit, push, merge는 `.codex/state/pogo-settings.json`의 `gitAutomation` 정책을 따른다.
- 자동화가 꺼진 항목은 사용자가 명시적으로 요청하지 않으면 수행하지 않는다.
- 자동화가 켜진 항목도 검증 실패, dirty worktree 충돌, 관련 없는 변경, 불명확한 branch/remote가 있으면 수행하지 않는다.
- 기존 미커밋 변경을 되돌리거나 삭제하지 않는다.
- 관련 없는 변경을 stage/commit에 섞지 않는다.
- destructive command와 원격 작업은 명시적 요청과 승인 없이는 수행하지 않는다.
