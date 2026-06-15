---
name: language-policy
description: 문서 언어, ko/en 렌더링, 100자 줄 제한을 검증할 때 사용합니다.
---

# language-policy

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- 현재 언어 상태를 먼저 조회합니다.
- 문서와 skill body는 현재 언어를 따릅니다.
- command, API path, code identifier는 번역하지 않습니다.

## Procedure

- ko/en 전환은 templates 원천과 실제 출력을 함께 맞춥니다.
- 렌더 후 SKILL.md line count와 frontmatter를 검증합니다.
- 100자 제한은 실제 문자 수 기준으로 확인합니다.
- 스크립트 검증은 격리 복사본에서 먼저 수행합니다.

## Expert Rules

- 언어 전환은 단순 번역이 아니라 source와 rendered output 동기화입니다.
- 기술 식별자는 번역하지 않고 설명 문장만 언어 정책을 따릅니다.
- ko/en 템플릿은 같은 의미, 같은 제약, 같은 검증력을 가져야 합니다.
- render script는 실제 workspace보다 격리 복사본에서 먼저 시험합니다.
- 줄 길이는 markdown source 기준으로 검사하고 table 폭도 고려합니다.
- 혼합 언어는 사용자 입력, 고유명사, code identifier일 때만 허용합니다.
- 줄 길이는 렌더된 최종 파일 기준 100자 이하로 검증합니다.
- command, path, API, env var, class name은 번역하지 않습니다.

## Expert Checks

- 번역으로 기술 의미가 약해졌는지 봅니다.
- 혼합 언어가 필요한 이유가 있는지 봅니다.
- 제품 코드 변경과 언어 렌더 변경이 섞였는지 봅니다.

## Failure Modes

- ko 문서는 강한데 en 템플릿은 일반론으로 약해지는 상태.
- render 후 실제 SKILL.md가 template과 다른 상태.
- 명령어 옵션이나 path를 번역해 실행성을 깨는 상태.
- 언어 전환이 unrelated docs를 덮어쓰는 상태.
- ko/en 의미 차이나 강도 차이가 생긴 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- 렌더 후 skill 구조 깨짐.
- 명령/API 의미가 번역으로 변경.
- 언어 전환이 프로젝트 코드를 오염.

## Verify

- python3 .codex/script/codex_language.py status.
- isolated ko/en render test.
- line length check.

## Evidence

- 현재 language status와 render 대상이 기록됩니다.
- ko/en 격리 render 테스트가 통과합니다.
- line count와 long line 검사가 통과합니다.
- 번역 후 blocker, must, verify 강도가 유지됩니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
