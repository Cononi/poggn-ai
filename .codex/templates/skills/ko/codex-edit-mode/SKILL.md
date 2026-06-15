---
name: codex-edit-mode
description: Codex 수정 모드와 .codex/프로젝트 수정 경계를 관리할 때 사용합니다.
---

# codex-edit-mode

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- .codex 기능 변경인지 프로젝트 코드 변경인지 먼저 분류합니다.
- 두 범위는 가능하면 다른 commit으로 분리합니다.
- edit mode 결과와 hook 정책을 확인합니다.

## Procedure

- 권한이 막히면 우회하지 말고 mode나 요청 범위를 조정합니다.
- skill, agent, hook, script 변경은 모두 검증 대상입니다.
- 작업 후 실제 언어와 렌더 결과를 확인합니다.
- mode가 열린 상태로 unrelated 파일을 stage하지 않습니다.

## Expert Rules

- .codex 변경은 제품 변경보다 도구 동작과 정책 영향이 먼저입니다.
- mode 변경은 범위 확장이므로 이유와 되돌림 경로가 있어야 합니다.
- hook, script, skill 변경은 문서가 아니라 실행 시스템 변경입니다.
- 언어 렌더는 source template과 generated output을 동시에 봅니다.
- 프로젝트 파일과 .codex 파일을 섞으면 commit 의도를 분리합니다.
- 권한 문제를 chmod나 우회 write로 해결하기 전 정책을 확인합니다.
- 시작 전 .codex, 프로젝트 코드, generated output 변경을 분류합니다.
- .codex script/hook 변경은 syntax check와 dry-run 없이는 완료하지 않습니다.

## Expert Checks

- .codex 변경과 제품 코드 변경이 섞였는지 봅니다.
- edit mode 중 hooks를 무시했는지 봅니다.
- 스크립트 문법 검증 없이 commit하는지 봅니다.

## Failure Modes

- edit mode를 열어둔 채 unrelated 파일을 stage하는 상태.
- template만 고치고 실제 rendered skill을 갱신하지 않은 상태.
- script 문법 검증 없이 hook 동작을 바꾸는 상태.
- 제품 코드 변경을 .codex 작업 커밋에 섞는 상태.
- edit mode가 필요한 변경을 일반 파일 수정으로 우회하는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- 권한 없이 .codex 수정.
- 제품 코드와 .codex 기능을 한 commit에 혼합.
- 검증 없이 hook/script 변경.

## Verify

- $codex-edit-mode on/off 결과.
- python3 -m py_compile.
- $codex-quality gate --for-ai.

## Evidence

- edit 범위와 제외한 파일 목록이 기록됩니다.
- 언어 렌더 또는 script syntax 검증을 실행했습니다.
- staged diff가 승인 범위 안에 있습니다.
- source template과 rendered output 중 수정 대상을 기록합니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
