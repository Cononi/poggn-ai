# 보안 지침

보안 검사는 마지막 단계에서만 보는 검사가 아닙니다.
`$codex-verify gate`가 budget, quality, security, test를 함께 실행합니다.

```text
$codex-verify gate --for-ai
$codex-security gate
$codex-quality gate --for-ai
```

금지 사항입니다.

- secret, token, password, private key를 코드에 쓰지 않습니다.
- `.env` 내용을 읽거나 문서에 붙이지 않습니다.
- 인증과 권한 검사를 프론트에만 의존하지 않습니다.
- 사용자 입력을 검증하지 않고 DB나 shell에 넘기지 않습니다.
- CORS와 redirect 정책을 넓게 열지 않습니다.
- 권한 변경, 결제, 배포 설정은 고위험 변경으로 취급합니다.

## 신뢰 경계

- `$codex-*` shortcut은 `.codex/script`의 allow-list script만 실행합니다.
- `.codex` 수정은 `$codex-edit-mode on` 상태에서만 수행합니다.
- `codex_test_runner.py`는 신뢰된 `.codex/tests/test_*.py` 전용입니다.
- 외부에서 받은 테스트 파일, fixture, generated artifact는 먼저 검토합니다.
- 언어 전환은 `docs/`를 template에서 다시 렌더링하므로 template도 갱신합니다.

## 완료 기준

보안 이슈가 발견되면 TASK를 완료하지 않습니다.
security agent 또는 refactor agent가 별도 TASK로 수정해야 합니다.
보안 검증 결과와 남은 위험은 완료 보고에 포함합니다.
