# CODEX 개발 가이드 지침

이 파일은 매 턴 로드되는 부트스트랩 문서다. 상세 절차는 관련 skill과 script에 둔다.
토큰 절감을 위해 여기에는 라우팅과 절대 규칙만 남긴다.

## 필수 규칙

- 항상 `pogo` skill을 먼저 사용한다.
- 사용자 요청, `AGENTS.md`, 관련 skill, `.codex/agents` 설정이 충돌하면 더 구체적이고 현재 작업에 가까운 지침을 우선한다.
- 작업과 직접 관련된 skill의 `SKILL.md`만 읽고 적용한다. 이름만 보고 추측하지 않는다.
- 확인하지 않은 파일, 테스트, API, 설정, 실행 결과를 사실처럼 말하지 않는다.
- 기존 사용자 변경을 되돌리거나 섞지 않는다.
- 모든 보고서/문서/샘플은 `pogo-settings`의 `lang` 설정을 따른다. `lang=ko`면 한국어, `lang=en`이면 영어, `lang=bilingual`이면 양언어 요약을 포함한다.

## 시작 판단

작업 시작 시 다음만 짧게 판단한다.

- 의도와 성공 기준이 명확한가.
- `pogo`로 충분한가, `evidence-driven-sdd`가 필요한가.
- Subagents가 이득인가, Single Agent 예외인가.
- 어떤 전문 skill이 필요한가.
- 어떤 검증이 완료 기준인가.

필요할 때만 다음 형식으로 짧게 보고한다.

```text
에이전트 방식 판단:
- 추천: Multi Agent 우선 | Single Agent 예외
- 이유: 판단 근거
- 비용/위험: 토큰, 충돌, 불확실성
- 진행: 사용할 skill/agent와 검증 방식
```

## Skill 라우팅

- 기본 작업 판단과 단순 구현: `pogo`.
- 요구사항, acceptance criteria, 고위험 기능/API/데이터/보안 변경: `evidence-driven-sdd`.
- 브랜치, worktree, commit, push, merge, release: `safe-git-automation`; Subagents 사용 시 `pogo-git-agent`에게 실행 위임.
- `$pogo-settings`, git 자동화 상태, lang, hook/script 설정: `pogo-settings`.
- `$pogo-subagent-auto`, SubAgent 강제, evidence, commit/push/merge 차단: `pogo-subagent-auto`.
- 구조/경계/contract: `architecture`.
- API, 서버 로직, 인증/권한, 저장소, job/integration: `backend`.
- UI, 컴포넌트, 상태, form, routing, 접근성/반응형: `front`.
- UX, 정보 구조, 레이아웃, 시각 계층: `designer`.
- 인증, 권한, 입력 검증, secret, 네트워크, 파일, abuse case: `security`.
- 스키마, SQL, 트랜잭션, 인덱스, 마이그레이션: `safe-database-engineering`.

여러 영역이 걸리면 필요한 skill만 최소로 읽는다. 상세 규칙을 `AGENTS.md`에 중복 작성하지 않는다.

## Subagents

Codex 공식 용어는 Subagents다. 사용자가 Multi Agent라고 말하면 Subagents로 해석한다.
코드 수정, 버그 수정, 기능 개발, 리팩터링, 테스트, QA, 보안/아키텍처 판단은 Subagents 사용을 먼저 고려한다.
단순 질문, 명령 출력 확인, 문서 한두 줄, 명확한 단일 파일 T0 변경은 Single Agent 예외가 가능하다.

`subagent.auto=true`이면 개발/수정/리뷰/QA 작업에서 Single Agent 예외를 사용하지 않는다. 예외는 상태 조회와 shortcut만 허용한다. 예: `git status`, `$pogo-settings`, `$pogo-subagent-auto` 조회.
- `subagent.auto=true` 상태에서는 개발/수정/리뷰/QA 시작 시 광범위 리포지토리 탐색, 전체 `git diff`/`git log` 리뷰, 전체 검증/테스트를 먼저 수행하지 않는다.
- 대신 메인 오케스트레이터는 우선 3~5줄 브리프(목표/범위/위임 대상/검증 포인트)로 Subagent를 기동한다.
- 직접 개입은 다음 조건만 허용: 사용자 요청, 작업 실패, Subagent 불일치, 보안/데이터 손실 위험, Subagent 사용 불가.
`subagent.auto=true` 멀티에이전트 토큰 절감 플로우:
- 메인은 초안 브리프만 작성하고 구현/테스트/검증은 Subagent가 수행한다.
- 각 Subagent는 완료 즉시 근거형 보고서 문서를 작성한다. 보고서의 핵심 필드는 `summary`, `changed_files`, `evidence`, `risks`, `report_file`, `reviewer_decision`이며 역할별 세부 내용은 `evidence` 안에 3개 이하 항목으로 요약한다.
- 보고서는 별도 markdown 파일로 산출하고, 각 Subagent는 해당 파일 경로만으로 handoff한다.
- 보고서 검토 전담은 `pogo-verifier`가 맡아 보고서만(원시 로그, 전체 diff, 장문 분석 제외)으로 최종 판단을 만든다.
- 모든 작업 완료 후 메인은 `pogo-verifier` 최종 보고만 확인해 `pogo-git-agent`에 git/release 위임 여부를 결정한다.
- 메인은 원시 로그/전체 diff/장문 분석을 기본 소비하지 않으며, 사용자 요청·실패·불일치·보안/데이터 손실 위험 시에만 재확인한다.
`subagent.auto=true`이면 git 상태 확인, commit, push, merge, release 작업은 `pogo-git-agent`에 우선 위임하고, 메인 에이전트는 결정과 최종 보고만 담당한다.
`subagent.auto=true`이면 `pogo`와 `pogo-subagent-auto` 기준을 따른다.
`subagent.auto=true`이면 Subagent Thin Mode를 기본으로 사용한다. 메인 에이전트는 Subagent의 `summary`, `changed_files`, `evidence`, `risks`, `report_file`만 소비하고, 원시 로그와 전체 diff는 사용자 요청, 실패, 불일치, 보안/데이터 손실 위험이 있을 때만 좁게 재확인한다.
Subagent 결과는 `summary` 3줄 이하, `changed_files`, `evidence`, `risks` 3개 이하로 요약한다. 여러 Subagent 결과를 병합할 때도 메인은 결론, 충돌 여부, 다음 조치만 정리한다.
- 보고서 본문은 검토를 위해 별도 문서(예: `.codex/state/subagent-reports/<YYYY-MM-DD>/<HHMMSS>-<sanitized-branch>/<task-id>/<agent-name>.md`)로 남기며, `report_file`은 Hook 증거(`.codex/state/subagent-evidence.json`)가 아닌 작업별 보고서 본문이다.
- `<YYYY-MM-DD>`와 `<HHMMSS>`는 UTC 또는 명시된 timezone 기준으로 기록한다.
- `<sanitized-branch>`는 파일시스템 안전 문자로 정규화한 브랜치명을 사용한다.
- 각 보고서는 다음 항목을 반드시 남긴다: 작업 수행 이유, 처리한 작업, 작업 결과, 검토 에이전트 결과, 재검토 필요성, 완성도.
- 최종 검토 종합 문서는 각 개별 보고서의 위 항목을 근거로 통합해 작성한다.
- `.codex/state/subagent-evidence.json`에는 hook 규칙이 요구하는 `version/branch/head/agents/changedFiles`만 유지한다.

## Git

Git 작업은 `pogo-settings`와 `safe-git-automation`을 따른다. `subagent.auto=true`이면 git 실행과 상태 확인은 `pogo-git-agent`에게 우선 위임한다.

- `.codex/state/pogo-settings.json`의 `gitAutomation` 값을 확인한다.
- 자동화가 꺼진 commit/push/merge는 사용자가 명시적으로 요청하지 않으면 수행하지 않는다.
- 명시 요청 1회는 `$pogo-settings git <target> once`를 사용한다.
- 보호 규칙 우회, force push, destructive command는 별도 명시 승인 없이는 수행하지 않는다.
- PR은 기본 생성하지 않는다. branch push에서 같은 commit SHA의 `pogo-policy` PASS를 확인한다.
- main 반영은 검증된 commit의 fast-forward만 허용하고, 최종 추적은 project-scoped Release/tag로 한다.

## 구현과 검증

- 필요한 부분만 수정한다.
- 기존 코드 스타일, 파일 구조, helper API, 테스트 패턴을 따른다.
- 관련 없는 리팩터링, 포맷 변경, 죽은 코드 삭제를 끼워 넣지 않는다.
- 새 추상화는 실제 복잡도나 중복을 줄일 때만 만든다.
- 변경 때문에 고아가 된 import, 변수, 함수, 클래스, 파일은 제거한다.
- 가능한 경우 변경을 재현하거나 보호하는 테스트를 작성/수정한다.
- 실행하지 않은 테스트를 PASS라고 말하지 않는다.
- 검증 결과는 `PASS`, `FAILED`, `PARTIAL`, `NOT RUN`으로 보고한다.
