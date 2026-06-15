# 품질 기준 커스텀

품질 기준은 `.codex/script/codex_quality.py`의 인자로 조정합니다.

기본 파일 줄 수는 200줄입니다.

기본 프론트 컴포넌트 줄 수는 160줄입니다.

기본 page 줄 수는 120줄입니다.

## 예시

```text
$codex-quality gate --front-lines 140 --page-lines 100 --for-ai
```

```text
$codex-quality gate --strict --for-ai
```

strict 모드는 warning도 실패로 처리합니다.

팀 기준이 강하면 hook에서 strict를 쓰도록 바꿀 수 있습니다.

## 추천 기준

소규모 프로젝트는 front-lines 140을 권장합니다.

대형 프로젝트는 shared/ui와 features 분리를 먼저 적용합니다.

legacy JS 프로젝트는 전환 TASK를 별도로 만든 뒤 TS로 이동합니다.
