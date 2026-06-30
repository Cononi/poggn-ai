# pogo-main

## summary
- 작업 수행 이유: 사용자가 worktree 생성 시점마다 release하는 것이 아니라, 같은 내용이 여러 번 수정되면 최종안만 release해야 한다고 지적했습니다.
- 수행한 작업: `safe-git-automation` release 관리, worktree policy, no-PR release flow에 worktree 생성/중간 수정/중간 commit/branch push는 release 조건이 아니며 최종 `main` 반영 후 한 번만 release한다는 기준을 반영했습니다.
- 작업 결과: worktree는 반복 수정과 검증 공간, release는 최종안 공표 단계라는 경계가 문서화되었고, 최종안 이전 상태를 release하려는 경우 차단 기준에 포함했습니다.

## changed_files
- `.codex/skills/safe-git-automation/SKILL.md`
- `.codex/skills/safe-git-automation/references/worktree-policy.md`
- `.codex/skills/safe-git-automation/references/pr-template.md`
- `.codex/version.json`
- `pogo-state/subagent-reports/2026-06-30/040000-chore_pogo_final_release_gate/release-gate/pogo-main.md`

## evidence
- 별도 worktree: `/config/workspace/.worktrees/pogo-ai-2/pogo-final-release-gate`
- 작업 branch: `chore/pogo-final-release-gate`
- 기준 commit: `64a01ce8187a086c29d083e7539de51993559684`

## risks
- 중간 commit을 보존할 수는 있지만, release note는 최종 main 기준으로 작성해야 하므로 운영자가 release 시점을 혼동하지 않아야 합니다.
- 최종안 여부가 불명확한 요청은 release가 아니라 검증 결과와 남은 결정을 먼저 보고해야 합니다.
- worktree cleanup은 release 조건이 아니므로 cleanup 완료 자체를 release trigger로 해석하면 안 됩니다.

## report_file
pogo-state/subagent-reports/2026-06-30/040000-chore_pogo_final_release_gate/release-gate/pogo-main.md

## reviewer_decision
PASS
