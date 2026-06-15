---
name: saw
description: $saw 단일 TASK micro workflow를 실행하고, 모호한 기능 요청을 요구사항/보안 계약으로 고정한 뒤 검증할 때 사용합니다.
---

# saw

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- 작은 단일 변경에만 사용합니다.
- risk가 높거나 cross-stack이면 MAW 전환을 제안합니다.
- 검증은 agent chain이 아니라 verify gate로 수행합니다.
- 모호한 "만들어줘/구현해줘/개선해줘" 요청은 구현 전에 요구사항 계약으로 바꿉니다.
- 보안, 권한, 데이터, public contract 미확정 사항이 있으면 구현을 시작하지 않습니다.

## Clarification Contract

- 명확한 단일 변경은 질문 없이 진행합니다.
- 모호하면 최대 3라운드까지 1회 응답당 질문 1개만 사용해 좁힙니다.
- 질문은 현재 답이 없으면 구현 방향이 갈리는 가장 중요한 결정 1개만 고릅니다.
- 여러 항목을 한 번에 묻지 말고, 사용자 답변을 받은 뒤 다음 질문을 이어갑니다.
- 선택지가 필요하면 2~3개 이하로 제한하고, 한 줄 자유답도 허용합니다.
- 1라운드는 목표나 기대 결과 중 더 불확실한 1개를 확인합니다.
- 2라운드는 포함/제외 범위, 완료 기준, 수정 가능 영역 중 blocker가 될 1개를 확인합니다.
- 3라운드는 검증 방법, public contract, 권한/보안 결정 중 위험이 가장 큰 1개를 확인합니다.
- 사용자가 "알아서 해줘"처럼 위임하면 기본값을 선택하되 가정과 위험을 짧게 명시합니다.
- 질문 라운드 후에는 confirmed requirements, non-goals, acceptance criteria, verification plan을 요약하고 사용자 확인을 받습니다.
- 3라운드 후에도 핵심 결정이 비어 있으면 구현하지 말고 확정 내용, 미확정 내용, 제안 기본값, 구현 가능 여부를 보고합니다.

## Security Contract

- asset, entry point, trust boundary를 먼저 찾고 authentication과 authorization을 분리해 확인합니다.
- auth, owner, role, tenant, API mutation, DB query 영향이 있으면 보안 질문을 포함합니다.
- 외부 입력, 파일/URL/path, secret, 개인정보, CORS/CSRF/cookie, redirect, webhook도 확인합니다.
- 입력 검증은 type, size, format, authorization context를 포함합니다.
- error, response, log, audit trail에 token, password, secret, 개인정보, internal id가 노출되지 않게 합니다.
- owner/role check 없는 mutation, tenant predicate 없는 query는 blocker입니다.
- secret 노출 가능성, CORS wildcard와 credential 조합도 blocker입니다.
- 보안 영향이 SAW 범위를 넘으면 MAW 전환 또는 security lane을 제안합니다.

## Guidance Contract

- 중간에 scope, architecture, data, auth, API, UX, verification 위험을 발견하면 즉시 사용자에게 알립니다.
- 조언은 risk, recommended approach, tradeoff, confirmation need 순서로 짧게 제공합니다.
- 사소한 구현 디테일은 직접 판단하고, 동작이나 계약이 바뀌는 결정만 확인합니다.

## Procedure

- 작업 전 risk classify와 context pack을 실행합니다.
- 요구사항 계약과 보안 계약이 충족됐는지 확인합니다.
- 변경 파일 예산을 넘으면 follow-up으로 나눕니다.
- 코드 변경이면 테스트 명령을 확보합니다.
- TASK commit link 없이는 done 처리하지 않습니다.

## Expert Rules

- SAW는 작은 변경을 빠르게 끝내는 방식이지 검증을 줄이는 방식이 아닙니다.
- 파일 수, risk, stack 수가 커지면 즉시 MAW 전환을 고려합니다.
- 단일 TASK라도 auth, DB, deploy 영향은 strict gate를 적용합니다.
- scope creep는 follow-up으로 분리하고 현재 TASK done을 늦추지 않습니다.
- commit link 없이 상태만 done으로 바꾸면 trace가 깨집니다.
- 검증 불가 사유는 환경, 도구 부재, 승인 필요를 구분해 보고합니다.
- 시작 전 $codex-risk classify 결과가 low/small인지 확인합니다.
- auth, DB, API contract, cross-stack 변경이면 MAW 전환을 제안합니다.
- acceptance criteria 없이 구현을 시작하지 않습니다.
- 보안상 fail-closed 기본값을 선택하고, 공개 동작 변경은 사용자 확인을 받습니다.

## Expert Checks

- 작은 작업이라도 auth, DB, API 변경이면 엄격히 봅니다.
- budget 초과를 무시하고 진행했는지 봅니다.
- staged quality/security가 실행됐는지 봅니다.
- 요구사항을 추측으로 구현했는지, acceptance criteria와 대조했는지 봅니다.
- exploitable path를 한 줄로 설명할 수 없는 보안 검토를 통과시키지 않습니다.

## Failure Modes

- 작은 작업이라며 quality/security gate를 생략하는 상태.
- 한 파일 수정이 cross-stack 계약 변경을 숨기는 상태.
- 테스트 실패를 unrelated로 단정하고 근거가 없는 상태.
- 예산 초과 후에도 TASK를 쪼개지 않는 상태.
- 변경 파일 수, 테스트 범위, token 예산을 넘고도 분할하지 않는 상태.
- "개선/구현/만들어줘"를 acceptance criteria 없이 바로 구현하는 상태.
- authn 성공을 authz 성공으로 착각하거나 owner/tenant 검증을 client 입력에 맡기는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- 코드 변경인데 test command 없음.
- budget 초과 SAW 강행.
- security/API/DB 변경을 quick fix로 축소.
- public contract, authz, tenant isolation, secret handling, 입력 검증 미확정.

## Verify

- $codex-verify gate --staged --mode saw --for-ai.
- $codex-quality gate --for-ai.
- $codex-security gate.
- 보안 영향이 있으면 targeted auth negative test 또는 exploit scenario를 남깁니다.

## Evidence

- risk classify와 context pack 결과가 있습니다.
- confirmed requirements, non-goals, acceptance criteria, verification plan이 있습니다.
- staged diff가 단일 TASK 범위입니다.
- commit hash와 verify/quality/security 결과가 연결됩니다.
- 코드 변경은 최소 한 개 테스트나 명시된 검증 대체가 있습니다.
- 보안 영향이 있으면 asset, entry point, trust boundary와 authz/입력 검증 판단이 있습니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
