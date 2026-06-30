# pogo-main

## summary
- 작업 수행 이유: 다른 프로젝트에서 `PreToolUse hook (failed) error: hook exited with code 1`가 표시되어 정책 차단과 hook 내부 실패가 구분되지 않았습니다.
- 수행한 작업: `.codex/hooks/pogo_policy_hook.py`에서 정책 차단 응답을 stderr + exit 1 대신 JSON `decision:block` + exit 0으로 반환하도록 수정했습니다.
- 작업 결과: git commit 차단과 codex-edit 보호 파일 수정 차단이 모두 JSON block + exit 0으로 반환되며, 일반 명령은 계속 통과합니다.

## changed_files
- `.codex/hooks/pogo_policy_hook.py`
- `.codex/version.json`
- `pogo-state/subagent-reports/2026-06-30/pretooluse-block-json/hook-policy/pogo-main.md`

## evidence
- `python3 -m py_compile .codex/hooks/pogo_policy_hook.py .codex/script/pogo_settings.py .codex/script/_pogo_settings.py`: PASS
- `printf ... git commit ... | python3 .codex/hooks/pogo_policy_hook.py pre-tool-use`: JSON `decision:block`, exit 0
- `printf ... touch .codex/tmp-hook-test ... | python3 .codex/hooks/pogo_policy_hook.py pre-tool-use` with codex-edit off: JSON `decision:block`, exit 0
- `PYTHONDONTWRITEBYTECODE=1 python3 .codex/script/pogo_policy_ci.py`: PASS

## risks
- OS sandbox 문제(`bwrap` namespace 생성 실패)는 hook 수정으로 해결되지 않으며 실행환경 설정 문제로 별도 조치가 필요합니다.
- hook 정책 차단은 이제 실패처럼 보이지 않지만, 실제 hook 내부 예외는 여전히 실패로 보고되어야 합니다.
- 다른 프로젝트가 이전 버전 hook을 사용 중이면 이번 pogo-policy 릴리즈를 반영해야 같은 동작을 얻습니다.

## report_file
pogo-state/subagent-reports/2026-06-30/pretooluse-block-json/hook-policy/pogo-main.md

## reviewer_decision
PASS
