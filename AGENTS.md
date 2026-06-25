# CODEX 개발 가이드 지침

이 파일은 매 턴 로드되는 부트스트랩 문서다. 실행 정책의 실질 기준은 본 문서다.

## 절대 규칙

- 항상 `pogo` skill을 먼저 사용한다.
- 사용자 요청, 본 AGENTS, 관련 `SKILL.md`, `.codex/agents`가 충돌하면 더 구체적이고 현재 작업에 가까운 정책을 우선한다.
- 작업과 직접 관련된 skill의 `SKILL.md`만 읽고 적용한다.
- 확인하지 않은 파일/테스트/API/설정/실행 결과를 사실처럼 말하지 않는다.
- 기존 사용자 변경을 되돌리거나 섞지 않는다.
- 모든 문서/보고/샘플은 `pogo-state/pogo-settings.json`의 `lang`을 따른다.

## 작업 시작 전 규칙 (메인 오케스트레이터)

- 모든 실질 작업 시작 전 메인은 `작업 진행 예정 보고서`를 먼저 남긴다.
- 작업 시작 브리프는 `의도`, `범위`, `제약`, `검증 포인트`를 포함한다.
- 메인은 최소 개입을 기본값으로 하고, 사용 승인/재요청/보고서 충돌/보안·데이터 손실 위험/의도 불명확/merge 충돌 위험 시에만 직접 개입한다.

## Subagent 운영

- 코드 수정, 버그 수정, 기능 개발, 리팩터링, 테스트, QA, 보안/아키텍처 판단은 Subagents 사용을 우선한다.
- 독립 가능한 파일/기능 경계는 병렬 분배한다.
- 겹치는 파일은 `integrator` 또는 `worker` 단일 리더가 통합/병합한다.
- 병렬 작업이 어렵거나 충돌 가능성이 높으면 Single Agent로 범위를 한정해 진행한다.

## Subagent Thin Mode

- 반환 필수 항목: `summary`, `changed_files`, `evidence`, `risks`, `report_file`, `reviewer_decision`
- `summary`에는 작업 수행 이유, 수행한 작업, 작업 결과, 검토 에이전트 결과, 재검토 필요성, 완성도를 모두 포함한다.
- `summary`와 결과는 3개 항목 이하로 요약해 보고한다.

## Subagent 보고서

- 경로: `pogo-state/subagent-reports/<YYYY-MM-DD>/<HHMMSS>-<sanitized-branch>/<task-id>/<agent-name>.md`
- `agent-name`은 개별 Subagent 이름, `task-id`는 작업 단위를 의미한다.
- 보고서 본문은 작업 이유/결과/재검토/완성도를 명확히 기재한다.

## Skill 라우팅

- 기본 판단/단순 구현: `pogo`
- 요구사항/AC/고위험/보안/데이터 영향: `evidence-driven-sdd`
- 브랜치·worktree·commit·push·merge·release: `safe-git-automation`
- `$pogo-settings`, git 자동화·lang, hook/script: `pogo-settings`
- `subagent.auto`·차단/승인 정책: `pogo-subagent-auto`

## Git/Release 규칙

- `pogo-settings`의 `gitAutomation`을 확인한다.
- 자동화가 꺼진 상태에서 commit/push/merge은 사용자 명시 없이는 수행하지 않는다.
- 보호 규칙 우회, force push, destructive command는 별도 승인 없이는 수행하지 않는다.
- 기본 PR 생성 없음. branch push 전 동일 SHA의 `pogo-policy` PASS를 확인한다.
- main 반영은 검증된 commit만 허용하고 release는 사용자 명시 후 수행한다.

## 구현 및 검증 원칙

- 필요한 부분만 수정하고 주변 리팩터링/포맷 변경을 섞지 않는다.
- 고아가 된 import/변수/함수/파일은 제거한다.
- 실행하지 않은 테스트를 PASS로 보고하지 않는다.
- 검증 상태는 `PASS`, `FAILED`, `PARTIAL`, `NOT RUN`으로 보고한다.
- 문서 정책 중복은 최소화하고, 실질 변경은 AGENTS로 집중한다.
