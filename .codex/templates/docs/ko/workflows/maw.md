# MAW 멀티 에이전트 파이프라인

$maw는 큰 작업을 여러 feature lane으로 나누는 workflow입니다.
agent 개수를 묻지 않고 추천 agent를 보여준 뒤 선택을 받습니다.

## 핵심 개념

```text
agent = 역할
skill = 작업 절차
lane = 실제 병렬 실행 단위
wave = 한 번에 실행하고 병합할 lane 묶음
pipeline = lane dependency graph
epic = 전체 목표
```

order와 payment는 별도 lane입니다.

```text
T002 Order REST API   L002 backend implement
T003 Payment REST API L003 backend implement
```

둘 다 backend agent를 쓰지만 서로 다른 worktree에서 실행합니다.
Spring Boot, JPA, Swagger는 backend agent가 쓰는 skill입니다.

## 진짜 멀티 에이전트 흐름

MAW는 단순히 backend, qa, security를 순서대로 두지 않습니다.
구현 task가 끝나면 그 task를 downstream agent가 받습니다.

```text
L002 backend order implement
  -> L004 test order
  -> L006 qa order
  -> L008 refactor order
  -> L010 security order

L003 backend payment implement
  -> L005 test payment
  -> L007 qa payment
  -> L009 refactor payment
  -> L011 security payment
```

따라서 처음에는 backend/order와 backend/payment가 동시에 ready입니다.
order가 먼저 끝나면 payment가 아직 실행 중이어도 order QA가 ready가 됩니다.

## ready queue

다음에 실행할 수 있는 lane만 봅니다.

```text
$codex-pipeline ready --for-ai
```

ready lane만 worktree로 준비합니다.

```text
$codex-pipeline prepare
```

ready lane만 CSV로 만듭니다.

```text
$codex-pipeline csv --ready
```

subagent 실행 프롬프트를 만듭니다.

```text
$codex-pipeline prompt
```

Codex에서 CSV row마다 subagent 하나를 spawn합니다.

## 실행 반복

```text
1. $codex-pipeline ready --for-ai
2. $codex-pipeline prepare
3. $codex-pipeline csv --ready
4. Codex가 CSV row마다 subagent spawn
5. 각 lane은 $codex-task commit 으로 완료
6. 완료 lane을 root branch에 merge
7. 다시 $codex-pipeline ready --for-ai
```

## /agent 와 agent 목록

/agent 는 실행 중인 subagent thread를 전환하거나 보는 명령입니다.
등록된 custom agent 목록이 안 보일 수 있습니다.

등록된 agent 파일 목록은 아래로 봅니다.

```text
$codex-agents list
$codex-agents check
```

## budget 기준

MAW budget은 전체 epic 제한이 아닙니다.

80개 파일이나 3000줄 제한은 한 wave 또는 PR/MR의 안전 상한입니다.
전체 신규 구현이 이 값을 넘을 수 있습니다.

이 경우 전체를 막지 않고 wave를 나눕니다.

```text
W001 contract, schema
W002 order, payment backend implement
W003 order, payment test and QA
W004 refactor and security
W005 frontend screens
```
