---
name: docs
description: README, API 문서, 릴리즈 노트, 운영 문서를 갱신할 때 사용합니다.
---

# docs

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- 문서는 현재 코드와 검증 결과만 말합니다.
- 현재 언어 정책과 100자 줄 제한을 지킵니다.
- 명령, API path, code identifier는 번역하지 않습니다.

## Procedure

- API 문서는 auth, request, response, error를 포함합니다.
- 운영 문서는 rollback, migration, secret 주의사항을 포함합니다.
- 실행 예시는 실제 package manager와 repo script를 사용합니다.
- 미검증 성능 주장과 성공 표현을 쓰지 않습니다.

## Expert Rules

- 문서는 원하는 상태가 아니라 현재 검증된 상태만 기록합니다.
- 운영 문서는 실패했을 때 누가 무엇을 되돌릴지까지 말해야 합니다.
- API 문서는 성공보다 auth, validation, error, pagination을 더 중시합니다.
- 예시는 실제 명령과 실제 package manager를 사용해야 합니다.
- 번역은 기술 의미와 명령어 재현성을 해치지 않아야 합니다.
- 릴리즈 노트는 사용자 영향, migration, 위험을 분리합니다.
- 확인하지 못한 코드, config, script 내용은 쓰지 않거나 미검증으로 표시합니다.
- 운영 문서는 rollback trigger와 복구 확인 지표를 포함합니다.

## Expert Checks

- 코드와 문서가 충돌하는지 봅니다.
- 실제 secret처럼 보이는 예시가 있는지 봅니다.
- TODO성 문장이 follow-up 없이 남았는지 봅니다.

## Failure Modes

- 코드에 없는 기능을 문서가 약속하는 상태.
- TODO가 follow-up 없이 남아 책임이 사라지는 상태.
- 예시 secret이 실제 credential처럼 보이는 상태.
- 운영 절차가 rollback 없이 배포만 설명하는 상태.
- 문서 변경만으로 behavior 변경을 암시하는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- 코드와 반대되는 문서.
- 보안 또는 migration 주의사항 누락.
- 실행하지 않은 테스트를 성공으로 문서화.

## Verify

- language status.
- line length check.
- linked command/path existence.

## Evidence

- 문서의 명령과 path가 repo에 존재합니다.
- 변경된 코드/API와 문서 diff가 일치합니다.
- 언어 정책과 줄 길이 제한을 확인했습니다.
- API 문서는 auth, validation, ownership 실패 응답을 분리합니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
