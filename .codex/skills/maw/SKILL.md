---
name: maw
description: $maw 병렬 workflow를 실행하고, 모호한 대형 기능 요청을 요구사항/보안/lane 계약으로 고정할 때 사용합니다.
---

# maw

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- ready lane은 main 메모가 아니라 실제 subagent 실행 대상으로 봅니다.
- ready queue를 확인하기 전 구현하지 않습니다.
- implementation lane은 실제 subagent thread로 실행합니다.
- 모호한 "만들어줘/구현해줘/개선해줘" 요청은 구현 전에 요구사항, 보안, lane 계약으로 고정합니다.
- 보안, 권한, 데이터, public contract, owner files, forbidden files 미확정 사항이 있으면 spawn하지 않습니다.

## Clarification Contract

- 최대 3라운드, 라운드당 3개 이하 질문으로 목표와 범위를 좁힙니다.
- 1라운드는 사용자 목표, 핵심 시나리오, 기대 결과를 확인합니다.
- 2라운드는 포함/제외 범위, 완료 기준, 변경 가능 영역, 검증 방법을 확인합니다.
- 3라운드는 lane 분리, owner files, forbidden files, public contract, 보안 결정을 확정합니다.
- 3라운드 후에도 핵심 결정이 비어 있으면 구현하지 말고 확정 내용, 미확정 내용, 제안 기본값, 구현 가능 여부를 보고합니다.
- 구현 전 confirmed requirements, non-goals, acceptance criteria를 짧게 고정합니다.
- lane contract와 verification plan도 함께 고정합니다.

## Security Contract

- asset, entry point, trust boundary를 먼저 찾고 authentication과 authorization을 분리해 확인합니다.
- auth, owner, role, tenant, API mutation, DB query 영향은 security 계약에 넣습니다.
- 외부 입력, 파일/URL/path, secret, 개인정보, CORS/CSRF/cookie도 확인합니다.
- redirect, webhook 영향이 있으면 security lane 또는 security gate를 계약에 넣습니다.
- 각 implementation lane은 입력 검증, output encoding, error/log 노출, owner/tenant predicate 책임을 명시합니다.
- owner/role check 없는 mutation, tenant predicate 없는 query는 blocker입니다.
- secret 노출 가능성, CORS wildcard와 credential 조합도 blocker입니다.
- security agent는 exploit path, negative authz test 또는 명시적 검증 대체를 남깁니다.

## Guidance Contract

- 중간에 scope, architecture, data, auth, API, UX, verification 위험을 발견하면 즉시 사용자에게 알립니다.
- 조언은 risk, recommended approach, tradeoff, confirmation need 순서로 짧게 제공합니다.
- 사소한 구현 디테일은 lane owner가 처리하고, 동작이나 계약이 바뀌는 결정만 main이 확인합니다.

## Orchestration Contract

- main은 구현자가 아니라 orchestrator입니다.
- main은 subagent final report, diff, 검증, acceptance, blocker를 평가합니다.
- 문제가 있으면 lane을 done 처리하지 않고 구체적 blocker로 재수행을 지시합니다.
- 재수행은 같은 lane과 owner files 범위에서만 허용하고 scope creep은 follow-up으로 분리합니다.

## Token Contract

- subagent에는 전체 TASKS.md, 전체 대화, 전체 ready JSON을 전달하지 않습니다.
- `$codex-pipeline ready --for-ai`는 샘플과 hidden count 확인에만 씁니다.
- 전체 spawn 대상은 `$codex-pipeline csv --ready`의 CSV로 처리합니다.
- subagent prompt는 lane id, purpose, acceptance, owner files, forbidden files만 포함합니다.
- 큰 로그와 diff는 원인 라인, 관련 파일, 실패 명령만 요약합니다.

## Procedure

- 요구사항 계약과 보안 계약이 충족됐는지 확인합니다.
- $codex-pipeline ready/csv/prompt를 spawn 입력으로 사용합니다.
- 각 subagent에는 task, lane, files, skills, done contract를 줍니다.
- commit link 후 downstream event를 처리합니다.
- 완료 thread는 결과 통합 후 닫습니다.

## Expert Rules

- MAW는 계획 문서가 아니라 실제 subagent thread 실행 계약입니다.
- main은 orchestrator이며 ready implementation lane을 직접 구현하지 않습니다.
- main은 subagent 결과를 diff, test, security, acceptance 기준으로 검토합니다.
- 문제가 있으면 lane을 done 처리하지 않고 같은 lane에 재수행을 지시합니다.
- 기능 구현 agent는 구현만 하고 QA/security/refactor 판정은 하지 않습니다.
- downstream lane은 완료 commit event 이후 필요한 역할만 생성합니다.
- 각 lane은 owner files, forbidden files, done contract, verification을 가집니다.
- 완료는 commit link 후에만 가능하며 TASK state와 thread 상태가 일치해야 합니다.
- MAW 시작 조건은 ready queue에 실제 implementation lane이 있을 때입니다.
- 각 subagent prompt에는 파일 범위, 금지 범위, 완료 계약, 검증 명령을 넣습니다.
- subagent prompt에는 전체 TASKS.md 대신 compact row contract만 넣습니다.
- acceptance criteria와 lane contract 없이 ready lane을 spawn하지 않습니다.
- 보안상 fail-closed 기본값을 선택하고, 공개 동작 변경은 사용자 확인을 받습니다.

## Expert Checks

- /agent에서 main만 보이는지 확인합니다.
- main thread가 구현을 대신했는지 봅니다.
- downstream lane이 생성만 됐는지 봅니다.
- subagent 결과가 main 검토 없이 pass 처리됐는지 봅니다.
- 요구사항을 추측으로 lane에 배분했는지, acceptance criteria와 대조했는지 봅니다.
- exploitable path를 한 줄로 설명할 수 없는 보안 검토를 통과시키지 않습니다.

## Failure Modes

- /agent에 main만 있는데 MAW 완료라고 보고하는 상태.
- ready queue를 보지 않고 main이 바로 구현하는 상태.
- 구현 agent가 자기 변경을 QA pass 처리하는 상태.
- subagent final report를 검토 없이 done 처리하는 상태.
- thread 종료 없이 completed worker가 pool을 점유하는 상태.
- lane 완료 후 commit link 없이 downstream event를 처리하는 상태.
- "개선/구현/만들어줘"를 acceptance criteria 없이 바로 lane으로 쪼개는 상태.
- authn 성공을 authz 성공으로 착각하거나 owner/tenant 검증을 client 입력에 맡기는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- main이 ready implementation lane 구현.
- TASK commit 연결 없이 done 처리.
- subagent spawn 없이 MAW 완료 보고.
- subagent 결과가 main 검토 없이 done 처리됨.
- public contract, authz, tenant isolation, secret handling, 입력 검증, owner files 미확정.

## Verify

- $codex-pipeline ready --for-ai.
- $codex-pipeline prompt.
- /agent thread 확인.
- 보안 영향이 있으면 $codex-security gate와 targeted auth negative test 또는 exploit scenario를 확인합니다.

## Evidence

- ready queue, prompt, spawned agent id를 기록합니다.
- confirmed requirements, non-goals, acceptance criteria, lane contract, verification plan이 있습니다.
- 각 subagent final report와 changed files를 통합합니다.
- main review 결과와 재수행 여부를 lane id와 함께 기록합니다.
- commit link와 downstream event 처리 결과를 보고합니다.
- /agent thread id와 lane id로 spawn 증거를 남깁니다.
- 보안 영향이 있으면 asset, entry point, trust boundary와 authz/입력 검증 판단이 있습니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
