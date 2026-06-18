# script 설명

.codex/script 안의 Python 파일은 토큰 절약을 위한 실행 단위입니다.

AI가 긴 문서를 읽고 쓰는 대신 script가 상태를 계산합니다.

## 핵심 script

```text
codex_state.py       workflow, TASK, VERSION 상태 관리
codex_task_git.py    TASK와 commit 연결, diff, revert
codex_lanes.py       MAW 병렬 lane과 worktree 관리
codex_pipeline.py    ready queue와 downstream agent pipeline 관리
codex_waves.py       MAW lane을 실행 wave로 분할
codex_work_items.py  요구사항을 기능 TASK로 분해
codex_design_gate.py 제품 유형, platform, framework, stack 계약 분류
codex_saw.py         SAW micro workflow 생성
codex_verify.py      SAW/TASK 완료 전 최소 검증
codex_test_runner.py .codex 내부 테스트 전용 no-dependency runner
codex_quality.py     코드 품질, 프론트 TSX, 중복 검사
codex_security.py    secret, token, private key 검사
codex_refactor.py    리팩토링 필요 여부 분석
codex_wiki.py        docs/index.html 생성
codex_language.py    ko/en 문서와 skill 렌더링
codex_shortcuts.py   $codex-* shortcut 실행
```

## codex_pipeline.py

구현, test, QA, refactor, security lane의 ready 상태를 계산합니다.

```text
$codex-pipeline status --for-ai
$codex-pipeline ready --for-ai
$codex-pipeline prepare
$codex-pipeline csv --ready
$codex-pipeline prompt
```

ready lane만 subagent batch로 실행합니다.

## codex_waves.py

대형 MAW 작업을 전체 크기로 막지 않고 wave로 나눕니다.

```text
$codex-waves assign
$codex-waves plan
$codex-waves next
$codex-waves prompt --wave W002
```

한 wave만 준비하고 실행합니다.

```text
$codex-lanes prepare --wave W002
$codex-lanes csv --wave W002
$codex-lanes prompt --wave W002
```

## codex_verify.py

SAW는 검증을 생략하지 않습니다.

검증 범위만 줄입니다.

```text
$codex-verify gate --for-ai
$codex-verify gate --staged --for-ai
```

검사 순서는 아래입니다.

```text
budget gate
quality gate
security gate
changed-code test command
```

문서만 변경되면 test는 생략됩니다.

코드가 변경되면 test command가 필요합니다. 기본 검증은 modified 파일과
untracked 신규 파일을 함께 봅니다. `.codex` 내부 Python 변경은 내부 테스트
runner를 자동으로 실행합니다.

명령은 `.codex/state/verify.json`에 넣을 수 있습니다.

```json
{
  "commands": ["npm run test", "npm run typecheck"]
}
```

명령이 없으면 package.json, pytest, Gradle, Maven을 일부 탐지합니다.

그래도 없으면 gate는 실패합니다.

`codex_test_runner.py`는 신뢰된 `.codex/tests/test_*.py` 전용입니다.
외부에서 받은 임의 테스트 파일 실행 용도로 사용하지 않습니다.

## risk, context, budget

아래 명령은 토큰 절약의 핵심입니다.

```text
$codex-risk classify --text "요청" --for-ai
$codex-context pack --for-ai
$codex-budget status
```

자세한 내용은 scripts/risk-context-budget.md를 참고합니다.

## commit 연결

TASK commit은 verify를 자동으로 다시 실행합니다.

```text
$codex-task commit T001 --message "fix dto"
```

검증을 통과해야 TASK가 done 처리됩니다.

## context와 doctor

```text
$codex-context pack --for-ai
$codex-context pack --staged --for-ai
$codex-doctor --deep --for-ai
```

context는 현재 workflow, 다음 TASK, 변경 파일 요약을 압축합니다.

doctor는 git, hook, docs, script 문법, 문서 길이를 검사합니다.

```text
$codex-extend check agent --name NAME --purpose "PURPOSE"
$codex-extend create skill --name NAME --purpose "PURPOSE" --approve
```
