---
name: ci-cd
description: GitHub Actions, GitLab CI, Docker, 배포 파이프라인 변경에 사용합니다.
---

# ci-cd

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- trigger, branch guard, environment guard를 먼저 확인합니다.
- secret은 masked env나 protected secret store로만 전달합니다.
- test 실패를 숨기지 않고 pipeline을 실패시킵니다.

## Procedure

- cache key에 lockfile과 runtime version을 포함합니다.
- Docker build context와 layer에 secret이 남지 않게 합니다.
- deploy job에는 승인, rollback, environment 분리를 둡니다.
- migration job은 app deploy 순서와 분리합니다.

## Expert Rules

- pipeline은 실패를 빨리 드러내고 배포는 천천히 열리게 설계합니다.
- cache는 속도보다 재현성과 오염 방지를 먼저 만족해야 합니다.
- secret은 env, log, artifact, image layer 전체에서 추적합니다.
- deploy job은 branch, tag, environment, approval gate를 모두 봅니다.
- migration과 app rollout은 실패 시 되돌릴 순서까지 포함합니다.
- matrix build는 지원 runtime과 실제 배포 runtime을 분리해 적습니다.
- PR, push, tag, manual trigger별 권한과 deploy 경로를 분리 검증합니다.
- pull_request_target은 checkout ref와 secret 노출 경로를 blocker로 봅니다.

## Expert Checks

- || true, continue-on-error가 실패를 숨기는지 봅니다.
- production deploy가 tag/branch guard 없이 동작하는지 봅니다.
- artifact retention에 민감 파일이 포함되는지 봅니다.

## Failure Modes

- continue-on-error가 필수 테스트 실패를 숨기는 상태.
- pull_request에서 write token이나 production secret을 쓰는 상태.
- Docker layer에 .env나 build arg secret이 남는 상태.
- rollback job이 deploy와 같은 실패 조건에 묶인 상태.
- deploy concurrency나 environment lock 없이 중복 배포가 가능한 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- secret echo 또는 plain text 저장.
- 테스트 실패를 성공 처리.
- rollback 없는 production deploy 변경.

## Verify

- CI lint 또는 workflow syntax check.
- docker build dry run 가능 여부.
- $codex-security gate.

## Evidence

- workflow trigger와 permission diff를 검토했습니다.
- 실패 시 pipeline이 멈추는 경로를 확인했습니다.
- artifact와 cache에 민감 파일이 없음을 확인했습니다.
- lockfile frozen install과 cache key 근거를 확인했습니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
