# 문제 해결

hook이 실패하면 먼저 .codex/hooks/dispatch.py 경로를 확인합니다.
Git 저장소가 아니면 아래 명령을 실행합니다.

```text
$codex-git doctor
$codex-git ensure
```

docs/index.html이 오래되었으면 다시 생성합니다.

```text
$codex-wiki build
```

TASKS.md 체크박스가 완료되지 않으면 아래를 확인합니다.

- TASK status가 done인지 확인합니다.
- commit이 TASK에 연결되었는지 확인합니다.
- 해당 TASK의 모든 lane이 done 또는 merged인지 확인합니다.

품질 gate가 실패하면 큰 파일, 중복, secret 흔적을 먼저 정리합니다.
프론트 파일이 커졌다면 primitive, feature component, hook, api client로 나눕니다.
