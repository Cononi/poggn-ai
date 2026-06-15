# 언어 전환

언어는 단일 ZIP 안에서 전환합니다.

```text
$codex-language ko
$codex-language en
```

전환 시 README, AGENTS, agent, skill, docs 파일이 다시 렌더링됩니다.
docs/index.html도 다시 생성됩니다.

언어 템플릿 위치입니다.

```text
.codex/templates/i18n.json
.codex/templates/docs/ko/
.codex/templates/docs/en/
```

새 문서를 추가하면 두 언어 템플릿 모두에 추가하는 것을 권장합니다.
