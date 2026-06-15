# TASK, lane, commit 추적

TASK는 완료 증거로 commit을 가져야 합니다.
commit message에는 Codex footer가 들어갑니다.

```text
Codex-Task: T002
Codex-Lane: L002
Codex-Workflow: v1-shop
Codex-Agent: backend
Codex-Skills: spring-boot,jpa,openapi-swagger
```

commit 후 스크립트는 commits.jsonl에 실제 commit hash와 변경 파일을 기록합니다.
TASKS.md에는 A, M, D, R 요약만 표시합니다.
전체 diff는 필요할 때만 스크립트로 봅니다.

```text
$codex-task files T002
$codex-task diff T002 --name-status
$codex-task revert-task T002
```

TASK 체크박스가 [x]가 되는 조건입니다.

- TASK status가 done입니다.
- 연결 commit이 하나 이상 있습니다.
- 모든 lane이 done 또는 merged입니다.

이 조건을 만족하지 않으면 TASKS.md는 [ ] 상태를 유지합니다.
