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
$codex-quality gate --all --include-codex --max-lines 500 --for-ai
$codex-verify gate --for-ai
$codex-wiki build
```

- extension-governance: agent와 skill 생성 gate입니다.


문서를 추가하거나 수정하면 `docs/` 원본과 `.codex/templates/docs/ko,en`을
같이 갱신합니다. 언어 전환은 template에서 `docs/`를 다시 렌더링합니다.
