# pogo-main

## summary
- 작업 수행 이유: 사용자가 간단한 작업에는 worktree를 만들지 않는 것이 낫고, `작업 진행 예정 보고서` 후 승인 없이 진행한 점이 문제라고 지적했습니다.
- 수행한 작업: `pogo` 기본 작업 방식에 보고서 후 같은 턴 진행 금지와 승인 전 작업 금지를 명시하고, `safe-git-automation` worktree 기준을 간단한 작업/소규모 수정은 worktree 없이 처리하도록 조정했습니다.
- 작업 결과: worktree는 모든 작업의 기본값이 아니며, 여러 파일/프로젝트, release 준비, 병렬 작업, 기존 미커밋 변경 충돌 위험이 있을 때 사용하는 기준으로 정리했습니다.

## changed_files
- `.codex/skills/pogo/SKILL.md`
- `.codex/skills/safe-git-automation/SKILL.md`
- `.codex/skills/safe-git-automation/references/worktree-policy.md`
- `.codex/version.json`
- `pogo-state/subagent-reports/2026-06-30/worktree-stop-policy/policy-update/pogo-main.md`

## evidence
- `git diff --check`: PASS
- `PYTHONDONTWRITEBYTECODE=1 python3 .codex/script/pogo_policy_ci.py`: PASS
- `rg` 핵심 문구 확인: 보고서 후 같은 턴 진행 금지, 승인 전 작업 금지, worktree는 모든 작업의 기본값이 아님.

## risks
- 문서 정책 변경이며 hook이 보고서 후 STOP을 자동 강제하지는 않습니다.
- 간단한 작업 여부는 메인 오케스트레이터 판단이 필요하므로 모호하면 보고서에서 worktree 사용 여부를 명시해야 합니다.
- commit/push/merge/release는 여전히 사용자 명시와 settings 정책을 따라야 합니다.

## report_file
pogo-state/subagent-reports/2026-06-30/worktree-stop-policy/policy-update/pogo-main.md

## reviewer_decision
PASS
