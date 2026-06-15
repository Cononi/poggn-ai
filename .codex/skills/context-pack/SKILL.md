---
name: context-pack
description: TASK, lane, 변경 파일 context를 compact하게 확인할 때 사용합니다.
---

# context-pack

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- 작업 시작, 재개, subagent spawn 전 실행합니다.
- pack 결과의 workflow, phase, changes를 해석합니다.
- pack과 git status가 다르면 git status를 우선 재확인합니다.

## Procedure

- SAW에서는 changed files 중심으로 읽습니다.
- MAW에서는 lane worktree 기준으로 다시 실행합니다.
- pack이 넓으면 task trace로 한 번 더 좁힙니다.
- subagent prompt에는 pack 요약을 짧게 포함합니다.

## Expert Rules

- pack은 현재 workflow와 변경 표면을 잡는 시작점이지 최종 증거가 아닙니다.
- pack 이후 파일을 바꾸면 다음 판단 전 갱신합니다.
- MAW에서는 main worktree와 lane worktree의 pack을 구분합니다.
- pack이 넓으면 task trace, git diff, rg로 다시 좁힙니다.
- pack의 change_count가 0이어도 untracked와 staged 상태를 확인합니다.
- subagent에게 pack 전체가 아니라 필요한 요약만 전달합니다.
- pack 출력의 TASK, lane, phase, changed files를 작업 전 요약합니다.
- pack에 없는 파일을 수정하려면 TASK 범위 적합성을 먼저 설명합니다.

## Expert Checks

- pack 이후 변경이 생겼는데 갱신하지 않았는지 봅니다.
- pack에 없는 파일을 이유 없이 읽었는지 봅니다.
- 전체 repo scan으로 pack을 대체했는지 봅니다.

## Failure Modes

- pack에 없는 파일을 무근거로 수정하는 상태.
- pack 결과와 git status 충돌을 무시하는 상태.
- 오래된 pack으로 commit 직전 판단을 하는 상태.
- large TASKS를 읽고 pack을 생략하는 상태.
- MAW lane에서 root pack만 믿고 lane worktree pack을 생략하는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- 오래된 pack 결과 사용.
- lane worktree가 아닌 root context 사용.
- pack/git status mismatch 무시.

## Verify

- $codex-context pack --for-ai.
- $codex-task trace --for-ai.
- git status --short.

## Evidence

- pack timestamp와 workflow path를 보고합니다.
- pack과 git status 차이를 해소했습니다.
- subagent prompt에 pack 요약이 포함됩니다.
- pack/git status 불일치 해소 과정을 남깁니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
