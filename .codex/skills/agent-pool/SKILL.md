---
name: agent-pool
description: MAW worker 이름, thread 재사용, 종료 기준, context 오염 방지에 사용합니다.
---

# agent-pool

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- 역할 정의 재사용과 live thread 재사용을 구분합니다.
- 기본값은 lane별 fresh worker로 둡니다.
- worker label에는 role, feature, stage, lane을 포함합니다.

## Procedure

- pool status와 thread cap을 먼저 확인합니다.
- 완료 thread는 결과 요약을 회수한 뒤 닫습니다.
- 같은 workflow와 같은 ownership일 때만 thread 재사용을 허용합니다.
- main 검토에서 실패한 lane만 같은 계약으로 재수행합니다.
- 새 MAW workflow는 이전 worker context를 승계하지 않습니다.

## Expert Rules

- thread 재사용은 비용 절감이 아니라 context 위험으로 평가합니다.
- worker 이름은 사람이 사고 원인을 역추적할 수 있어야 합니다.
- pool cap에 도달하면 새 작업보다 완료 thread 정리가 먼저입니다.
- 동일 role이라도 TASK, branch, file owner가 다르면 fresh worker를 씁니다.
- worker summary는 변경 파일, 검증, 남은 위험을 포함해야 합니다.
- 오래 열린 worker는 최신 git 상태를 다시 확인하기 전 수정하지 못합니다.
- thread 재사용은 same TASK, same lane, same file ownership일 때만 허용합니다.
- 재수행은 같은 TASK/lane/ownership일 때만 기존 worker에 맡깁니다.
- main 재검토 blocker는 짧은 실패 근거와 기대 수정만 worker에 전달합니다.
- worker label은 role/task/lane/stage/files-scope 형식으로 둡니다.

## Expert Checks

- old context가 최신 파일보다 우선하지 않는지 봅니다.
- worker가 ownership 밖 파일을 수정했는지 봅니다.
- 완료 thread가 max_threads를 계속 점유하는지 봅니다.

## Failure Modes

- 이전 workflow 기억으로 새 파일을 덮어쓰는 상태.
- completed thread가 닫히지 않아 max_threads를 잡아먹는 상태.
- worker label만 같고 실제 owner가 다른 상태.
- subagent 결과가 main diff와 충돌하는데 통합 검토가 없는 상태.
- live worker가 같은 파일을 동시에 다루는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- 서로 다른 TASK가 같은 live context를 공유함.
- 완료 thread를 닫지 않아 spawn이 막힘.
- worker가 다른 lane 파일을 무단 수정함.
- main review 실패 lane을 새 근거 없이 반복 재사용함.

## Verify

- $codex-pool status.
- $codex-pipeline ready --for-ai.
- /agent 상태 확인.

## Evidence

- pool status에 running, completed, closed 상태가 분리됩니다.
- worker별 owner 파일 목록이 남아 있습니다.
- 완료 후 열린 thread 수를 보고합니다.
- 종료 전 summary, changed files, tests, blockers를 회수합니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
