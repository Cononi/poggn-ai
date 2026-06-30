# pogo-main

## summary
- 작업 수행 이유: 사용자가 multi-project 저장소에서 worktree를 더 적극적으로 사용해야 한다고 지적했고, 작업 완료 후 worktree 결과를 통합한 뒤 `.worktrees`를 안전하게 정리하는 기준을 명문화할 필요가 있었습니다.
- 수행한 작업: `safe-git-automation`의 작업공간 선택 기준을 worktree 기본으로 바꾸고, `worktree-policy.md`에 통합 절차와 `pogo_worktree_cleanup.py` 기반 정리 절차를 추가했습니다.
- 작업 결과: 새 작업, multi-project release 준비, 병렬 작업은 worktree 우선으로 정리되었고, 현재 대상 미커밋 변경을 그대로 커밋해야 하는 경우만 일반 branch 예외로 남겼습니다.

## changed_files
- `.codex/skills/safe-git-automation/SKILL.md`
- `.codex/skills/safe-git-automation/references/worktree-policy.md`
- `.codex/version.json`
- `pogo-state/subagent-reports/2026-06-30/035007-chore_pogo_worktree_default_cleanup/worktree-policy/pogo-main.md`

## evidence
- 별도 worktree: `/config/workspace/.worktrees/pogo-ai-2/pogo-worktree-default-cleanup`
- 작업 branch: `chore/pogo-worktree-default-cleanup`
- 기준 commit: `d4f78fb46231f436a99c20cb5b029de9035e8a3c`

## risks
- worktree는 process, port, DB, secret을 격리하지 않으므로 병렬 테스트에는 별도 런타임 격리 설정이 필요합니다.
- 현재 작업공간에 이미 대상 미커밋 변경이 있는 경우에는 worktree로 옮기는 과정에서 누락/혼입 위험이 있어 일반 branch 예외를 유지했습니다.
- worktree 제거는 branch 삭제가 아니므로 branch 정리는 별도 승인과 확인이 필요합니다.

## report_file
pogo-state/subagent-reports/2026-06-30/035007-chore_pogo_worktree_default_cleanup/worktree-policy/pogo-main.md

## reviewer_decision
PASS
