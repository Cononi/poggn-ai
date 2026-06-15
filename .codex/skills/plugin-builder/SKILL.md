---
name: plugin-builder
description: Codex plugin scaffold, manifest, skill bundle 작업에 사용합니다.
---

# plugin-builder

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- plugin 요청인지 일반 기능 요청인지 먼저 구분합니다.
- manifest는 실제 skill, command, asset 경로와 일치해야 합니다.
- plugin scope는 설치 가능한 독립 단위여야 합니다.

## Procedure

- skill bundle에는 trigger, blocker, verification을 포함합니다.
- cache busting이나 reinstall 절차를 확인합니다.
- marketplace entry는 ordering과 availability를 명시합니다.
- plugin 코드와 host project code를 섞지 않습니다.

## Expert Rules

- plugin은 host project와 독립 설치 가능한 배포 단위여야 합니다.
- manifest는 선언 파일이 아니라 실제 discovery contract입니다.
- skill bundle은 trigger, forbidden work, verification을 포함해야 합니다.
- plugin asset은 output 재료인지 instruction인지 구분해 배치합니다.
- cache busting은 개발 편의가 아니라 설치 검증의 일부입니다.
- private plugin은 path, secret, organization 정보 노출을 검토합니다.
- .codex-plugin/plugin.json schema와 상대 경로 정합성을 설치 전 검증합니다.
- command 제공 시 idempotency, cwd, sandbox 권한을 문서화합니다.

## Expert Checks

- manifest 필수 필드가 빠졌는지 봅니다.
- private plugin에 민감 경로나 secret이 포함됐는지 봅니다.
- install/cache refresh 검증이 있는지 봅니다.

## Failure Modes

- manifest가 없는 파일이나 stale path를 가리키는 상태.
- host app 코드와 plugin 코드가 한 커밋에 섞이는 상태.
- 설치 후 discovery가 안 되는데 파일 생성만 완료한 상태.
- marketplace metadata가 실제 사용 가능 상태와 다른 상태.
- plugin과 프로젝트 코드가 양방향 의존하는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- 일반 앱 기능을 plugin으로 오분류.
- manifest와 실제 파일 불일치.
- 설치 검증 실패.

## Verify

- plugin manifest validation.
- install or refresh command.
- skill discovery check.

## Evidence

- manifest validation과 discovery 결과가 있습니다.
- install/reinstall 또는 cache refresh를 검증했습니다.
- plugin scope와 포함 파일 목록을 보고합니다.
- marketplace entry의 id, 순서, visibility, compatibility를 확인했습니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
