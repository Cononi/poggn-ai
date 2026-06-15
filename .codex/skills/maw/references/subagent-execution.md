# MAW Subagent Execution Contract

MAW는 TASK/lane/CSV를 만드는 것으로 끝나지 않습니다.
ready lane마다 실제 Codex subagent thread가 떠야 합니다.

## Must

1. `$codex-risk classify --for-ai`를 먼저 실행합니다.
2. 사용자가 `$maw`를 명시하면 risk가 saw여도 MAW를 유지합니다.
3. `$codex-context pack --for-ai`로 현재 상태를 압축 확인합니다.
4. `$codex-work-items apply`로 implementation lane을 만듭니다.
5. `$codex-pipeline ready --for-ai`와 csv/prompt를 확인합니다.
6. `$codex-agents check/list`로 agent 구성을 확인합니다.
7. 현재 세션의 subagent capability로 ready lane마다 실제 subagent를 spawn합니다.
8. implementation TASK가 commit에 연결되면 downstream lane을 spawn합니다.
9. 완료된 subagent thread는 결과 통합 후 닫습니다.

## Never

- main thread가 ready implementation lane을 대신 구현하지 않습니다.
- TASK를 commit 연결 없이 done 처리하지 않습니다.
- downstream lane을 만들고 실제 실행을 생략하지 않습니다.

## Blocker

`/agent`에 main만 있거나, main이 구현을 대신하면 MAW 실패입니다.
