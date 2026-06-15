# Core Skill Rules

모든 skill은 활성화되면 이 기준을 적용합니다.

## Must

- TASK 범위, owner, 변경 파일, 검증 명령을 먼저 확인합니다.
- 구현은 작은 단위로 나누고, public contract 변경은 명시합니다.
- business rule은 controller, UI, script glue에 숨기지 않습니다.
- 입력 검증, 권한, 오류 형태, 테스트 가능성을 경계에서 확인합니다.
- 실패한 test, build, lint, security, sandbox 결과를 숨기지 않습니다.

## Never

- unrelated user change를 revert, overwrite, stage, commit하지 않습니다.
- secret, token, private key, 실제 credential, 대형 생성물을 commit하지 않습니다.
- 검증 없이 done, pass, safe, complete라고 보고하지 않습니다.
- 큰 파일, 중복 로직, 혼합 책임을 task 소유 범위에 남기지 않습니다.

## Done

완료 보고에는 변경 파일, 실행한 검증, 생략/차단 사유, 남은 위험,
TASK/commit 연결을 포함합니다.
