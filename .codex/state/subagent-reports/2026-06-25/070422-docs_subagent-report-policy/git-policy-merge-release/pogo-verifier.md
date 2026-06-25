# pogo-verifier

## summary
- `merge-notes` 명령 추가와 Git 정책 문서 보강(merge 템플릿, worktree, release 운용)으로 사용자 요청의 핵심 항목(스크립트 중심 의사결정, merge 본문/푸터 보강, 수동 release 전환, 범용 Single/Multi 동등 정책)을 반영한 후 변경사항을 점검했습니다.
- 확인 결과, `safe-git-automation`/`pogo-git-agent` 문서와 `.codex/script/pogo_release.py`의 동작이 서로 정합적이며, `merge-notes`는 기존 `create`의 version/tag 유효성 제약은 유지한 채 초안 출력 가능, 버전 미확인 시 `unknown` 처리 및 merge title/body/footer 요약을 출력합니다.
- 재검토는 `merge-notes`의 default 기준(`HEAD~`/latest tag) 범위 정책이 실제 운영 정책과 일치하는지, 그리고 `--verify` 강제 조건이 팀 운영 정책 요구와 충돌하지 않는지(운영 가이드가 증거 요구를 명시)만 필요합니다.

## changed_files
- `.codex/skills/safe-git-automation/SKILL.md`
- `.codex/skills/safe-git-automation/references/pr-template.md`
- `.codex/skills/safe-git-automation/references/worktree-policy.md`
- `.codex/agents/pogo-git-agent.toml`
- `.codex/script/pogo_release.py`

## evidence
- `.codex/skills/safe-git-automation/SKILL.md`에 Single/Multi 동일 규칙, script-first 원칙, deterministic 처리(메인/merge/worktree 단계의 명확 규칙), release는 사용자 명시 시에만 실행하는 문구 및 no-PR fast-forward 정책이 기록됨.
- `.codex/skills/safe-git-automation/references/pr-template.md`에 Merge 기록 제목/Body/Footer 템플릿(`Refs`, `Validation`, `Scope`, `Rollback`)과 `자동 릴리즈는 수행하지 않는다` 가이드가 명시됨.
- `.codex/skills/safe-git-automation/references/worktree-policy.md`에 병렬/병행 작업에서 worktree 사용 가이드와 `deterministic script(고정명령)` 기록 원칙이 명시됨.
- `.codex/agents/pogo-git-agent.toml`의 `developer_instructions`에 `Apply 동일 규칙 for single-agent and multi-agent` 및 `script-first`가 명시됨.
- `.codex/script/pogo_release.py`:
  - `merge-notes` 서브커맨드가 추가되어 merge commit 수집(`collect_merge_commits`), 제목/Body/Footer 표시(`split_body_footer`), 변경 파일/검증/롤백 섹션 출력.
  - 버전이 비어도 실패하지 않고 `현재 버전: unknown` + 상태 메시지로 초안 출력.
  - `create`는 `validate_tag`를 통해 semver/tag 형식을 요구.
- 실행 증거:
  - `python3 -m py_compile .codex/script/pogo_release.py` 종료 0.
  - `python3 .codex/script/pogo_release.py merge-notes --help` 도움말 출력됨.
  - `python3 .codex/script/pogo_release.py merge-notes --from HEAD~5 --to HEAD --verify "pytest: NOT RUN"` 실행 시 `## 릴리즈 판단`, `## Merge 상세`, `## 변경 파일`, `## 검증`, `## 롤백` 출력 및 버전 unknown 처리 확인.
- 변경 파일은 대상 5개에 한정되어 있어 `git diff --name-only`가 위 목록만 반환.

## risks
- `merge-notes`는 `--verify`가 없으면 즉시 종료되므로, 자동 호출 시 필수 증거 입력 절차가 필요합니다(운영 가이드 일치 여부는 별도 확인 필요).
- 기본 `--from`이 `latest_project_tag(project)`이므로 태그 형식/정확도가 깨진 프로젝트에서는 기준 범위가 기대와 달라질 수 있어 merge 집계 범위 판단의 선행 점검이 필요합니다.
- 변경 파일/병합 본문 수집은 project scope에 따라 경로 필터링되므로, multi-project 리포지토리에서 범위를 명확히 지정해야 누락을 피할 수 있습니다.

## reviewer_decision
PASS
