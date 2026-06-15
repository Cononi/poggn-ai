# Agent pipeline

Agent pipeline은 MAW의 핵심 실행 모델입니다.

## 왜 필요한가

단순 병렬은 구현 lane만 동시에 돌립니다.
그러면 QA, refactor, security가 마지막에 한 번만 돌 수 있습니다.

Agent pipeline은 각 구현 결과를 downstream agent가 바로 받습니다.

```text
구현/order done -> qa/order ready
구현/payment running -> 계속 진행
```

## stage

```text
foundation
implement
test
qa
refactor
security
```

## dependency

각 lane은 deps에 upstream lane id를 가집니다.

deps가 모두 done 또는 merged이면 ready가 됩니다.

```text
$codex-pipeline ready --for-ai
```

## worktree 준비

ready lane만 worktree를 만듭니다.

downstream lane은 가장 가까운 upstream branch에서 시작합니다.

```text
$codex-pipeline prepare
```

## CSV batch

```text
$codex-pipeline csv --ready
$codex-pipeline prompt
```

CSV row 하나가 subagent worker 하나입니다.

## 완료

각 worker는 lane별 commit을 남깁니다.

```text
$codex-task commit T002 --lane L002 --message "Order REST API"
```

검증 lane이 코드 변경이 없으면 빈 commit으로 증거를 남깁니다.

```text
$codex-task commit T006 --lane L006 --message "QA order" --allow-empty
```

## 추적

TASKS.md에는 stage, agent, wave, deps, commit이 표시됩니다.

전체 diff는 문서에 넣지 않습니다.

```text
$codex-task diff T002 --name-status
$codex-task files T002
```
