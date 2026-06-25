# Pogo Branch Protection

## 목적

로컬 hook은 실수 방지용이다. GitHub 보호 규칙은 `main`에 들어가는 최종 경로를 막는다.
`pogo-policy` check를 required status check로 연결하되, PR review 요구는 사용하지 않는다.
PR 없는 운영에서는 작업 branch에 push된 commit SHA의 `pogo-policy` PASS를 확인한 뒤 같은 SHA를 `main`으로 fast-forward push하고, 최종 기록은 GitHub Release에 남긴다.

## 적용 명령

```bash
python3 .codex/script/pogo_branch_protection.py --remote origin --branch main --apply
```

Dry run:

```bash
python3 .codex/script/pogo_branch_protection.py --remote origin --branch main
```

## Required Check

- Workflow: `.github/workflows/pogo-policy.yml`
- Job/status name: `pogo-policy`

## 운영 정책

- PR은 기본 생성하지 않는다.
- 작업 branch push 후 같은 commit SHA의 `pogo-policy` PASS를 확인한다.
- `main` 반영은 검증된 commit SHA를 fast-forward로만 수행한다.
- 반영 후 `.codex/script/pogo_release.py impacted/status/notes/create` 순서로 project-scoped GitHub Release를 남긴다.
- Subagent handoff는 작업 요약, 변경 파일, 검증 초점만 전달한다.
- `pogo_policy_ci.py`는 agent/skill 문서의 대략 토큰 추정치를 출력해 과도한 prompt 문서를 감지한다.
