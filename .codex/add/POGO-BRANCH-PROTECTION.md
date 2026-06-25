# Pogo Branch Protection

## 목적

로컬 hook은 실수 방지용이다. GitHub 보호 규칙은 `main`에 들어가는 최종 경로를 막는다.
`pogo-policy` check를 required status check로 연결하고, PR review 1개 이상을 요구한다.

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

## 토큰 소비 정책

- PR 본문에는 `Why`, `What`, `Verification`, `Risk`만 남긴다.
- Subagent 원시 로그는 PR에 붙이지 않는다.
- Subagent handoff는 작업 요약, 변경 파일, 검증 초점만 전달한다.
- `pogo_policy_ci.py`는 agent/skill 문서의 대략 토큰 추정치를 출력해 과도한 prompt 문서를 감지한다.
