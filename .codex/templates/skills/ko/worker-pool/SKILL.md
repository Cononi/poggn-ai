---
name: worker-pool
description: MAW worker 재사용, thread 종료, context 오염 방지에 사용합니다.
---

# worker-pool

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- worker는 실제 subagent thread임을 전제로 관리합니다.
- role config 재사용과 thread context 재사용을 구분합니다.
- fresh worker를 기본값으로 두고 재사용은 예외로 둡니다.

## Procedure

- worker label은 사람이 원인 추적 가능해야 합니다.
- 완료 worker는 요약 수집 후 닫습니다.
- thread cap 초과 전 completed thread를 정리합니다.
- pool 상태는 ready queue와 함께 확인합니다.

## Expert Rules

- worker는 추상 role이 아니라 살아 있는 context와 file owner를 가진 thread입니다.
- reuse는 같은 workflow, 같은 owner, 같은 branch 상태일 때만 허용합니다.
- worker는 혼자 작업하지 않으므로 다른 worker 변경을 되돌리면 안 됩니다.
- 완료 worker는 summary 수집, diff 검토, close 순서를 밟습니다.
- pool 상태는 ready queue와 함께 봐야 유휴/병목을 구분할 수 있습니다.
- worker prompt에는 forbidden files와 conflict 대응 원칙을 포함합니다.
- worker 상태 전이는 new, running, needs-review, closed, blocked로 둡니다.
- 같은 role이라도 다른 TASK의 thread context는 재사용하지 않습니다.

## Expert Checks

- 동일 workflow 밖 worker 재사용이 있는지 봅니다.
- worker가 ownership 밖 파일을 건드렸는지 봅니다.
- final report에 열린 worker 상태가 포함됐는지 봅니다.

## Failure Modes

- stale worker가 최신 main diff를 모르고 수정하는 상태.
- 두 worker가 같은 파일을 서로 다른 방향으로 고치는 상태.
- 완료 thread를 닫지 않아 새 worker spawn이 막히는 상태.
- worker final report 없이 main이 임의로 결과를 추정하는 상태.
- abandoned worker 기준 없이 응답 없는 thread가 남는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- old context가 새 TASK 판단 오염.
- completed worker가 thread cap 점유.
- worker ownership 위반.

## Verify

- $codex-pool status.
- $codex-pipeline ready --for-ai.
- /agent thread list.

## Evidence

- worker별 thread id, owner, status가 있습니다.
- 완료 worker의 changed files와 verification을 수집했습니다.
- 남은 open worker와 close 여부를 보고합니다.
- final report에 열린, 닫힌, blocked worker 수를 포함합니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
