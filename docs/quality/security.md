# 보안 지침

보안 검사는 마지막 단계에서 반드시 실행합니다.

```text
$codex-security gate
$codex-quality gate --for-ai
```

금지 사항입니다.

- secret, token, password, private key를 코드에 쓰지 않습니다.
- .env 내용을 읽거나 문서에 붙이지 않습니다.
- 인증과 권한 검사를 프론트에만 의존하지 않습니다.
- 사용자 입력을 검증하지 않고 DB나 shell에 넘기지 않습니다.
- CORS와 redirect 정책을 넓게 열지 않습니다.
- 권한 변경, 결제, 배포 설정은 고위험 변경으로 취급합니다.

보안 이슈가 발견되면 TASK를 완료하지 않습니다.
security agent 또는 refactor agent가 별도 TASK로 수정해야 합니다.
