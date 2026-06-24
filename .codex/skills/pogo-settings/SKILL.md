---
name: pogo-settings
description: Pogo settings 상태와 정책을 확인하거나 수정할 때 사용한다. 사용자가 git 자동화 commit/push/merge 허용 상태, 응답 lang 모드, pogo settings, pogo-settings.json, pogo policy hook, $pogo-settings 하위 명령, 또는 .codex/script/pogo_settings.py 동작을 묻거나 바꾸려는 경우 사용한다.
---

# Pogo Settings

## 목적

Pogo settings는 Codex 실행 중 적용되는 프로젝트 로컬 설정 상태를 다룬다.
상태 파일, hook, script가 함께 동작하므로 문서 추측 대신 실제 파일을 확인한다.

## 핵심 파일

- `.codex/state/pogo-settings.json`: 현재 설정 상태.
- `.codex/hooks.json`: 프로젝트 hook 등록 위치.
- `.codex/hooks/pogo_policy_hook.py`: hook dispatch와 차단 정책.
- `.codex/script/pogo_settings.py`: settings 상태 확인, git 자동화 변경, one-shot 허용, 언어 모드 변경의 단일 진입점.
- `.codex/script/_pogo_settings.py`: 상태 파일 read/write/validation helper.

## Hook Shortcut

`$pogo-settings`는 `UserPromptSubmit` hook에서 먼저 처리되어야 한다.
처리 결과는 `codex-edit-mode`처럼 `decision: block`으로 반환해 모델 응답 대신 상태와 사용법만 출력한다.

지원 명령:

```text
$pogo-settings
$pogo-settings status
$pogo-settings git status
$pogo-settings git commit on|off|once
$pogo-settings git push on|off|once
$pogo-settings git merge on|off|once
$pogo-settings git all off|once
$pogo-settings lang status
$pogo-settings lang ko|en|bilingual
```

## Lang 정책

`lang`은 응답, 계획, PR 본문, release note 같은 설명문에 적용한다.
Git 식별자인 branch, tag, version, commit type/scope는 `lang=ko`여도 영어/ASCII 관례를 유지한다.

## 작업 절차

1. 사용자의 의도가 상태 확인, 상태 변경, 정책 변경, 기능 삭제 중 무엇인지 먼저 분류한다.
2. 상태 확인은 `.codex/state/pogo-settings.json`과 관련 script 출력을 함께 확인한다.
3. 상태 변경은 `.codex/script/pogo_settings.py`의 `git` 또는 `lang` 하위 명령으로 처리한다.
4. hook/script 동작 변경은 `.codex/hooks.json`, `.codex/hooks/pogo_policy_hook.py`, `.codex/script/*`를 함께 검토한다.
5. 문서만 바꾸는 작업과 실제 hook/script 동작 변경을 구분해서 보고한다.

## 안전 규칙

- 사용자가 명시하지 않은 commit, push, merge 자동화는 켜지 않는다.
- 명시 요청 1회 처리는 `on`이 아니라 `$pogo-settings git <target> once`를 사용한다.
- 상태 파일을 직접 수정하기 전에 기존 script로 가능한지 먼저 확인한다.
- hook이 신뢰되거나 활성화되어 있다고 단정하지 않는다.
- 실행하지 않은 hook, script, 테스트를 성공했다고 보고하지 않는다.
- `.codex` 정책 변경과 제품 코드 변경을 한 작업에 섞지 않는다.

## 검증

변경 유형에 맞게 최소 하나 이상 확인한다.

```bash
python3 .codex/script/pogo_settings.py status
python3 .codex/script/pogo_settings.py git status
python3 .codex/script/pogo_settings.py git commit once
python3 .codex/script/pogo_settings.py lang status
python3 -m py_compile .codex/hooks/pogo_policy_hook.py .codex/script/pogo_settings.py .codex/script/_pogo_settings.py
```

상태 파일을 바꿨다면 변경 전후 값을 보고한다. hook/script를 바꿨다면 syntax check와 관련 dry run 결과를 보고한다.
