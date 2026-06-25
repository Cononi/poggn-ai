# CODEX 개발 가이드 지침

이 파일은 매 턴 로드되는 부트스트랩 문서다. 상세 절차는 관련 skill과 script를 우선한다.

## 절대 규칙

- 항상 `pogo` skill을 먼저 사용한다.
- 사용자 요청, 이 파일, 관련 skill, `.codex/agents` 설정이 충돌하면 더 구체적이고 현재 작업에 가까운 지침을 우선한다.
- 작업과 직접 관련된 skill의 `SKILL.md`만 읽고 적용한다. 이름만 보고 추측하지 않는다.
- 확인하지 않은 파일, 테스트, API, 설정, 실행 결과를 사실처럼 말하지 않는다.
- 기존 사용자 변경을 되돌리거나 섞지 않는다.
- 모든 보고서/문서/샘플은 `pogo-settings`의 `lang` 설정을 따른다.

## 시작 판단

작업 시작 시 의도/성공 기준, `pogo`와 `evidence-driven-sdd` 중 적합성, Subagents 사용 여부, 필요한 전문 skill, 검증 기준만 짧게 판단한다. 필요할 때만 다음 형식으로 보고한다.

```text
에이전트 방식 판단:
- 추천: Multi Agent 우선 | Single Agent 예외
- 이유: 판단 근거
- 비용/위험: 토큰, 충돌, 불확실성
- 진행: 사용할 skill/agent와 검증 방식
```

## Skill 라우팅

- 기본 작업 판단/단순 구현: `pogo`.
- 요구사항, AC, 고위험 기능/API/데이터/보안: `evidence-driven-sdd`.
- 브랜치, worktree, commit, push, merge, release: `safe-git-automation`; Subagents 사용 시 `pogo-git-agent`에게 실행 위임.
- `$pogo-settings`, git 자동화, lang, hook/script 설정: `pogo-settings`.
- `$pogo-subagent-auto`, SubAgent 강제, evidence, commit/push/merge 차단: `pogo-subagent-auto`.
- 구조/경계/contract: `architecture`; backend/API/저장소/job: `backend`; UI/상태/form/routing: `front`; UX/레이아웃: `designer`; 보안: `security`; DB/SQL/마이그레이션: `safe-database-engineering`.

## Subagents

Codex 공식 용어는 Subagents다. Multi Agent는 Subagents로 해석한다.
코드 수정, 버그 수정, 기능 개발, 리팩터링, 테스트, QA, 보안/아키텍처 판단은 Subagents 사용을 먼저 고려한다. 단순 질문, 명령 출력 확인, 문서 한두 줄, 명확한 단일 파일 T0 변경은 Single Agent 예외가 가능하다.

`subagent.auto=true`이면 개발/수정/리뷰/QA 작업에서 Single Agent 예외를 쓰지 않는다. 메인은 3~5줄 브리프만 작성하고 구현/테스트/검증은 Subagent가 수행한다. 직접 개입은 사용자 요청, 작업 실패, Subagent 불일치, 보안/데이터 손실 위험, Subagent 사용 불가일 때만 허용한다.

Subagent Thin Mode는 `pogo`와 `pogo-subagent-auto`를 따른다. 메인은 기본적으로 `summary`, `changed_files`, `evidence`, `risks`, `report_file`, `reviewer_decision`만 소비한다. 원시 로그, 전체 diff, 장문 분석은 사용자 요청, 실패, 불일치, 보안/데이터 손실 위험일 때만 좁게 확인한다.

보고서 본문은 `.codex/state/subagent-reports/<YYYY-MM-DD>/<HHMMSS>-<sanitized-branch>/<task-id>/<agent-name>.md`에 남긴다. 각 보고서는 작업 수행 이유, 처리한 작업, 작업 결과, 검토 에이전트 결과, 재검토 필요성, 완성도를 포함한다. 최종 검토 종합 문서는 개별 보고서를 근거로 작성한다. `.codex/state/subagent-evidence.json`은 hook용 `version/branch/head/agents/changedFiles` 메타데이터만 저장한다.

## Git

Git 작업은 `pogo-settings`와 `safe-git-automation`을 따른다. `subagent.auto=true`이면 git 상태 확인, commit, push, merge, release는 `pogo-git-agent`에 우선 위임한다.

- `.codex/state/pogo-settings.json`의 `gitAutomation` 값을 확인한다.
- 자동화가 꺼진 commit/push/merge는 사용자가 명시적으로 요청하지 않으면 수행하지 않는다.
- 명시 요청 1회는 `$pogo-settings git <target> once`를 사용한다.
- 보호 규칙 우회, force push, destructive command는 별도 명시 승인 없이는 수행하지 않는다.
- PR은 기본 생성하지 않는다. branch push에서 같은 commit SHA의 `pogo-policy` PASS를 확인한다.
- main 반영은 검증된 commit만 허용하고, release는 사용자의 명시 요청 후 project-scoped tag/release로 처리한다.

## 구현과 검증

- 필요한 부분만 수정하고 기존 스타일, 구조, helper API, 테스트 패턴을 따른다.
- 관련 없는 리팩터링, 포맷 변경, 죽은 코드 삭제를 섞지 않는다.
- 새 추상화는 실제 복잡도나 중복을 줄일 때만 만든다.
- 변경 때문에 고아가 된 import, 변수, 함수, 클래스, 파일은 제거한다.
- 가능한 경우 변경을 재현하거나 보호하는 테스트를 작성/수정한다.
- 실행하지 않은 테스트를 PASS라고 말하지 않는다.
- 검증 결과는 `PASS`, `FAILED`, `PARTIAL`, `NOT RUN`으로 보고한다.
