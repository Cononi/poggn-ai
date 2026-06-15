# 커스텀 방법

커스텀은 .codex 수정 모드에서만 수행합니다.

```text
$codex-edit-mode on
```

수정 후에는 다시 닫습니다.

```text
$codex-edit-mode off
```

커스텀 가능한 항목입니다.

- agent 추가 또는 설명 수정
- skill 추가 또는 절차 수정
- 품질 기준 threshold 수정
- docs 문서 보강
- hook 동작 수정
- 언어 템플릿 수정

수정 후 검증합니다.

```text
$codex-agents check
$codex-quality gate --all --for-ai
$codex-wiki build
```

- extension-governance: agent와 skill 생성 gate입니다.
