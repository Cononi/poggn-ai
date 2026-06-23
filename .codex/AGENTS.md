# AGENTS

모든 작업은 저장소 문서를 먼저 확인합니다.
문서 줄 길이는 100자를 넘기지 않습니다.
소스 파일은 200줄을 넘기지 않습니다.
프론트 컴포넌트 파일은 160줄 이하를 목표로 합니다.
React 프론트는 TypeScript와 TSX를 기본으로 사용합니다.
JS/JSX 신규 생성은 사용자가 명시한 legacy 작업일 때만 허용합니다.
중복 기능과 중복 코드는 만들지 않습니다.
스파게티 코드를 만들지 않습니다.
성질이 같은 UI는 primitive, compound, feature 컴포넌트로 추출합니다.
variant, size, tone, state, slot, render prop으로 재사용성을 만듭니다.
한 파일에 화면, 상태, API, 스타일, 검증을 모두 넣지 않습니다.
스크립트로 처리 가능한 상태 작업은 스크립트로 처리합니다.
$codex-risk classify 로 SAW/MAW 위험도를 먼저 판단합니다.
$codex-context pack --for-ai 로 현재 상태를 먼저 압축 확인합니다.
$codex-budget status 로 shortcut 출력 길이를 확인합니다.
TASKS.md, 전체 git log, 전체 diff는 사용자가 요구할 때만 넓게 읽습니다.
상태 진단은 $codex-doctor --deep --for-ai 로 스크립트가 수행합니다.
$maw는 큰 작업, 기능 분해, 병렬 lane, worktree 작업에 사용합니다.
$saw는 작은 단일 패치, 버그 수정, 작은 리팩토링에만 사용합니다.
$saw는 기본적으로 subagent chain, worktree, lane을 만들지 않습니다.
$saw는 한 TASK와 한 commit으로 끝나는 micro workflow입니다.
$saw에서 기능이 2개 이상이거나 cross-stack이면 $maw 전환을 제안합니다.
$saw는 변경 파일만 읽고, 전체 repo scan은 금지합니다.
$saw도 테스트와 보안 검사는 생략하지 않습니다.
$saw 검증은 agent가 아니라 $codex-verify gate로 수행합니다.
$saw commit은 staged quality, targeted test, security를 통과해야 합니다.
검증 실패 때만 refactor, test, security follow-up TASK를 추가합니다.
TASK 완료는 commit 연결 후에만 인정합니다.
구현 후 test, QA, quality, refactor, security 순서를 지킵니다.
SAW commit 전 $codex-verify gate --staged --mode saw --for-ai 를 통과해야 합니다.
commit 전 $codex-quality gate --staged --for-ai 를 통과해야 합니다.
보안 검사는 마지막에 반드시 수행합니다.
secret, token, private key는 절대 생성하거나 노출하지 않습니다.

## Git/PR 정책

작업 commit에는 PR 번호를 강제하지 않습니다.
PR 번호는 PR 생성 후 확정되므로 작업 commit 수정을 유도하지 않습니다.
PR 제목은 conventional commit 형식을 사용합니다.
PR 본문은 Why, What Changed, Verification, Risk and Rollback을 포함합니다.
리뷰 초점이 필요하면 Review Guide를 추가합니다.
기본 merge 전략은 squash merge입니다.
최종 squash merge commit 제목 끝에는 `(#번호)` 형식으로 PR 번호를 남깁니다.
일반 merge나 rebase merge가 필요하면 PR 번호 추적 방식 변경을 먼저 확인합니다.

## SAW 검증 규칙

SAW는 검증을 생략하지 않습니다.

작은 작업도 완료 전 $codex-verify gate --mode saw 를 통과해야 합니다.

commit 명령은 staged quality, test, security를 다시 실행합니다.

테스트 명령이 없으면 .codex/state/verify.json에 추가합니다.

## 토큰 예산 규칙

SAW가 risk/budget 기준을 넘으면 MAW나 follow-up으로 분리합니다.
AI가 전체 repo를 읽기 전 $codex-context pack --for-ai 를 사용합니다.
전체 diff는 마지막 수단입니다. 먼저 name-status만 확인합니다.

$maw budget은 전체 epic 상한이 아니라 lane/wave/PR 단위 상한입니다.
대형 신규 구현은 실패시키지 말고 wave로 나눠 순차 병합합니다.
한 wave는 $codex-lanes csv --wave W001 처럼 따로 실행합니다.
각 wave 완료 후 verify, merge, TASK commit, state commit을 수행합니다.
전체 구현 규모가 80개 파일이나 3000줄을 넘을 수 있음을 허용합니다.
하지만 한 lane이나 한 wave가 예산을 넘으면 더 작은 TASK로 분리합니다.

## MAW agent pipeline
MAW는 feature별 구현 worker와 downstream 검증 worker로 실행합니다.
$codex-pipeline ready --for-ai
$codex-pipeline prompt
$codex-agents list

## 이벤트 기반 MAW 규칙

MAW는 ready queue 기반으로만 subagent를 spawn합니다.
구현 agent는 각자 맡은 산출물 구현만 수행합니다.
테스트 코드는 test_writer agent가 작성합니다.
테스트 실행은 test_runner agent가 수행합니다.
QA, refactor, security는 policy와 위험도에 따라 필요한 경우만 생성합니다.
TASK 완료 이벤트는 $codex-events process 로 후속 lane을 만듭니다.
$codex-task commit은 MAW lane commit 후 event 처리를 자동 호출합니다.
agent profile은 재사용하지만 live thread는 lane별로 짧게 사용합니다.
완료된 subagent thread는 닫아 context rot과 토큰 누적을 줄입니다.
worker_name은 사람이 알아볼 수 있게 agent-feature-stage-lane 형식으로 기록합니다.
새 $maw는 새 agent_pool_generation을 사용합니다.

## 이벤트 기반 후속 agent

구현 agent는 제품 코드 구현만 수행합니다.

test_writer는 테스트 코드 작성만 수행합니다.

test_runner는 테스트 실행과 실패 분석만 수행합니다.

QA, refactor, security는 필요 조건이 맞을 때만 생성합니다.

전체 마무리는 $codex-finalize apply --for-ai 로 생성합니다.

subagent는 명시적으로 spawn해야 하며, 실행 중이면 /agent에서 확인합니다.

## 확장 규칙

없는 agent나 skill은 먼저 중복 검사를 합니다.

`$codex-extend scan --text "요청" --for-ai`를 사용합니다.

TASK가 완료되면 필요한 후속 agent만 동적으로 실행합니다.

## 구현 agent 일반화

MAW는 backend 전용 workflow가 아닙니다.
stage가 implement인 모든 agent는 다음 ready TASK를 계속 진행합니다.
예: backend, frontend, database, integration, devops, docs, performance.
custom implementer도 agent_roles.json에 등록하면 같은 규칙을 따릅니다.
검증 agent는 TASK 완료 이벤트 이후 필요한 경우에만 실행합니다.
역할 분류는 .codex/state/agent_roles.json에서 관리합니다.
