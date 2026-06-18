# Codex Automation Template

이 저장소는 다른 프로젝트에 복사해서 사용하는 Codex 자동화 템플릿입니다.
`.codex` 아래의 agent, skill, hook, script가 TASK 추적, lane 분리, 품질 gate,
검증 gate, 문서 생성을 담당합니다.

## 설치

대상 프로젝트 루트에 이 템플릿의 `.codex`와 `.agents` 구성을 둔 뒤 링크를 준비합니다.

```bash
python3 .codex/script/setup_links.py
```

템플릿 자체 테스트는 외부 패키지 없이 실행할 수 있습니다.
pytest를 선호하는 환경에서는 `requirements-dev.txt`를 사용할 수 있습니다.

```bash
python3 .codex/script/codex_test_runner.py --for-ai
```

## 기본 사용

Codex hook이 활성화된 환경에서 `$codex-*` shortcut을 사용합니다.

```text
$codex-language status
$codex-state summary --for-ai
$codex-task trace --for-ai
$codex-quality gate --for-ai
$codex-verify gate --for-ai
```

큰 작업은 `$maw`, 작은 단일 작업은 `$codex-saw` 흐름으로 시작합니다.
자세한 흐름은 `docs/03-quick-start.md`와 `docs/workflows/`를 참고합니다.

## 초기 설계 계약

`$maw` work item은 구현 lane 전에 `contract` lane을 만듭니다.
이 lane은 product type, platform/runtime, framework/engine, domain capability,
stack decision을 먼저 분류합니다. 사용자가 명시한 stack은 `explicit`,
구현 후 바꾸기 비싼 선택은 `confirm`, 합리적 기본 후보는 `candidate`,
요구가 없으면 보류할 기술은 `defer`로 기록합니다. 게임, 모바일, CLI,
API-only, data pipeline, plugin 같은 요청도 같은 gate를 먼저 통과합니다.

Spring Boot가 명시된 backend lane은 Java 패키지 구조 계약도 함께 받습니다.
기본값은 domain-first 구조이며, 각 도메인은 `api`, `application`,
`domain`, `infrastructure`로 나눕니다. `shared`는 response, exception,
validation, util을 소유하고, `platform`은 config, security, filter, web
infrastructure를 소유합니다. 최상위 `controller`, `service`, `repository`,
`entity` layer 패키지는 기본 생성 구조로 쓰지 않습니다.

React만 명시된 frontend lane은 Vite SPA와 Next.js/SSR 선택을 먼저 확인합니다.
Next.js가 명시되면 `src/app` App Router를 route/layout/loading/error 경계로
쓰고, 실제 기능 코드는 `src/features/<feature>`와 `src/shared`에 둡니다.
`page.tsx`는 route composition과 data boundary만 담당하고, `use client`는
leaf interactive component로 제한합니다. server data는 cache, revalidate,
dynamic 정책을 명시해야 합니다.

## 보안과 검증

`$codex-verify gate`는 budget, quality, security, test 순서로 확인합니다.
기본 검증은 modified 파일과 untracked 신규 파일을 함께 봅니다. `.codex`
내부 Python 변경은 `--include-codex --max-lines 500` 기준으로 검사합니다.

`codex_test_runner.py`는 이 템플릿의 신뢰된 `.codex/tests/test_*.py` 전용
runner입니다. 외부에서 받은 임의 테스트 파일을 실행하는 용도로 쓰지 않습니다.

## 템플릿 자체 검증

프로젝트 코드 검증과 `.codex` 템플릿 자체 검증은 분리합니다.
일반 프로젝트 품질 검사는 기본 명령을 사용합니다.

```bash
python3 .codex/script/codex_quality.py gate --for-ai
```

이 템플릿의 내부 Python 코드까지 검사하려면 `--include-codex`를 추가합니다.
내부 CLI 스크립트에는 템플릿 전용 줄 수 기준을 명시합니다.

```bash
python3 .codex/script/codex_quality.py gate --all --include-codex --max-lines 500 --for-ai
python3 .codex/script/codex_test_runner.py --for-ai
```

## 주요 문서

- `docs/00-overview.md`: 전체 개념
- `docs/03-quick-start.md`: 빠른 시작
- `docs/scripts/index.md`: script와 shortcut 목록
- `docs/workflows/maw.md`: MAW workflow
- `docs/workflows/saw.md`: SAW workflow
- `docs/quality/code-quality.md`: 품질 gate 기준
