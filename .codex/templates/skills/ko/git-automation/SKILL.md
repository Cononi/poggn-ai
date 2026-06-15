---
name: git-automation
description: Git 초기화, commit, TASK link, rollback, PR 준비에 사용합니다.
---

# git-automation

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- 작업 전 git status로 unrelated changes를 확인합니다.
- stage는 요청 범위 파일만 선택합니다.
- commit 전 quality gate를 통과합니다.
- commit 제목, body, footer는 현재 언어 정책을 따릅니다.

## Procedure

- TASK commit은 lane id와 message를 정확히 둡니다.
- 제목은 conventional commit 형식 `{type}: {title}`로 작성합니다.
- body에는 목적, 범위, 완료 기준, 검증을 기록합니다.
- footer에는 Codex-Task, Codex-Lane, Codex-Verification을 기록합니다.
- 기존 commit link는 hash와 TASK를 검증합니다.
- diff는 stat, name-only, targeted diff 순서로 확인합니다.
- state commit과 product commit은 필요하면 분리합니다.

## Expert Rules

- git 작업은 변경 생성보다 변경 격리가 더 중요합니다.
- stage 전에는 user change, generated output, state file을 분류합니다.
- commit message는 무엇을 바꿨는지보다 왜 이 범위인지 말해야 합니다.
- rollback 가능한 commit 단위를 만들기 위해 unrelated scope를 분리합니다.
- merge/rebase 전에는 작업 트리와 staged diff를 모두 확인합니다.
- 자동화 script가 실패하면 git 수동 명령으로 바로 우회하지 않습니다.
- stage 전 git diff --name-status와 cached name-status를 분리 확인합니다.
- commit message에는 TASK id, 변경 목적, 검증 결과 추적성을 남깁니다.

## Expert Checks

- unrelated 파일이 staged인지 봅니다.
- reset, checkout 같은 destructive 명령을 피했는지 봅니다.
- commit message가 변경 의도를 설명하는지 봅니다.

## Failure Modes

- untracked 대량 파일을 의도 없이 add -A 하는 상태.
- 사용자 변경이 내 커밋에 섞이는 상태.
- 품질 gate 실패 후 commit만 먼저 만드는 상태.
- destructive checkout/reset으로 작업을 잃는 상태.
- hook 실패 후 승인 없이 --no-verify를 쓰는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- TASK done인데 commit/link 없음.
- failed gate 후 commit.
- unrelated user change 포함.

## Verify

- git status --short.
- git diff --cached --stat.
- $codex-quality gate --for-ai.

## Evidence

- git status, staged name-only, diff stat를 확인했습니다.
- commit hash와 TASK link가 기록됩니다.
- 제외한 unrelated 파일 목록을 설명합니다.
- 생성물, lockfile, snapshot 포함 이유를 확인했습니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
