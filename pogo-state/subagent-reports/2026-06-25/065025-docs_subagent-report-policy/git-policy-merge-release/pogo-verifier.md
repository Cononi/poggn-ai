## summary
- 작업 수행 이유: `pogo`/`safe-git-automation` 정책, `pogo-git-agent` 지침, `pogo_release.py` 변경이 사용자가 요구한 단일/멀티 에이전트 동일 정책, worktree 활용, merge/release 토큰 절감형 운영에 부합하는지 검증했습니다.
- 수행한 작업: 지정된 6개 파일의 좁은 범위를 점검해 single/multi 동일 규칙, merge 시 title/body/footer 템플릿, worktree 정책, release 자동화 제한, merge-notes dry-run 동작을 확인했습니다.
- 작업 결과: `merge-notes` 커맨드는 등록·도움말·`py_compile` 기준은 충족되었으나, 현재 저장소에서 `.codex/version.json` 삭제 및 version source 부재로 `merge-notes --from HEAD~5 --to HEAD --verify ...`가 semver 유효성 오류로 종료돼 초안 생성이 실패합니다.
- 검토 에이전트 결과: 요구사항의 핵심은 반영되었으나, `merge-notes`가 판단/초안용 커맨드임에도 버전 소스 존재를 hard-fail 하는 점에서 재작업이 필요합니다.
- 재검토 필요성: `merge-notes`에 `--draft-only` 또는 `--allow-missing-version`(또는 동일한 대체 플래그)을 추가해 dry-run에서 버전 소스 미존재 시에도 출력되게 최소 수정 필요.
- 완성도: 정책 정합은 높으나 작업자 경험/요구 시나리오 충족은 부분 미완.

## changed_files
- `.codex/skills/safe-git-automation/SKILL.md`
- `.codex/skills/safe-git-automation/references/pr-template.md`
- `.codex/skills/safe-git-automation/references/worktree-policy.md`
- `.codex/agents/pogo-git-agent.toml`
- `.codex/script/pogo_release.py`
- `보고서: pogo-state/subagent-reports/2026-06-25/064854-docs_subagent-report-policy/git-policy-merge-release/pogo-worker.md`

## evidence
1. `.codex/skills/safe-git-automation/SKILL.md`에 `Single Agent와 Multi Agent 모두 동일 규칙` 및 `release 자동 생성은 기본 수행하지 않음` 문구가 존재.
2. `.codex/skills/safe-git-automation/references/pr-template.md`에 merge 메시지 `feat(scope):` 제목 + 변경 목적/핵심/영향, `Refs/Validation/Scope/Rollback` 푸터 형식이 명시됨.
3. `.codex/script/pogo_release.py`에서 `merge-notes`가 `current_version()` 검증을 통과해야 진입하고, 미통과 시 `release version source must contain a valid semver version`로 `return 2`가 반환됨(`merge-notes` 본문에서 확인).
4. 재현 명령 결과: `python3 .codex/script/pogo_release.py merge-notes --help`(옵션 출력) 및 `python3 .codex/script/pogo_release.py merge-notes --from HEAD~5 --to HEAD --verify "pytest: NOT RUN"`(종료 코드 2, 동일 에러 메세지)로 dry-run 차단 확인.

## risks
- 버전 소스가 삭제되어 있는 저장소에서 merge-notes가 초안 용도로도 실행되지 않아 요청된 판단 흐름을 끊음.
- merge-notes는 현재 `--verify` 누락 시 실패하도록 설계되어 있으며, 초안 단계에서도 최소한의 안내/경고 기반 출력이 가능한지 정책 합의가 필요.
- `current_version` 검증은 project-map/versionSource 정책에 따라 동작하나, release-notes/merge-notes 경로 간 요구사항 차이가 있을 경우 오해 여지가 있음.

## report_file
pogo-state/subagent-reports/2026-06-25/065025-docs_subagent-report-policy/git-policy-merge-release/pogo-verifier.md

## reviewer_decision
REWORK_REQUIRED
