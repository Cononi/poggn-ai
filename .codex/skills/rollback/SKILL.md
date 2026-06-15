---
name: rollback
description: 단일 TASK revert, 전체 rollback, 안전한 복구 범위 산정에 사용합니다.
---

# rollback

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- rollback 목적이 기능 제거인지 장애 완화인지 구분합니다.
- TASK trace로 관련 commit과 파일을 찾습니다.
- unrelated changes를 되돌리지 않습니다.

## Procedure

- revert commit을 기본으로 하고 reset은 피합니다.
- DB migration이 있으면 forward fix와 data repair를 검토합니다.
- config, secret, deploy rollback은 환경별로 분리합니다.
- rollback 후 테스트와 smoke path를 실행합니다.

## Expert Rules

- rollback은 과거로 돌아가는 작업이 아니라 현재 장애를 줄이는 변경입니다.
- revert 대상은 commit이 아니라 사용자 영향과 dependency 기준으로 고릅니다.
- DB 변경은 schema, data, app compatibility를 따로 되돌립니다.
- partial rollback은 이전/현재 client와 server 조합을 검토해야 합니다.
- config와 secret rollback은 환경별 전파 시간과 cache를 고려합니다.
- rollback 후에는 원인 분석보다 smoke와 사용자 경로 확인이 먼저입니다.
- rollback 대상 commit의 forward dependency와 후속 commit 영향을 매핑합니다.
- DB, queue, cache, external API state는 code revert와 별도 복구 계획을 둡니다.

## Expert Checks

- partial rollback의 compatibility matrix를 확인합니다.
- conflict를 임의 해결하지 않았는지 봅니다.
- 사용자 변경이 함께 되돌아가는지 봅니다.

## Failure Modes

- reset으로 shared history나 사용자 변경을 잃는 상태.
- migration revert가 데이터를 더 망가뜨리는 상태.
- feature flag는 되돌렸지만 background job이 계속 도는 상태.
- rollback commit이 원래 장애와 무관한 파일을 포함하는 상태.
- partial rollback에 API/schema 호환성 표가 없는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- unrelated 변경 rollback.
- DB/data rollback 계획 누락.
- conflict 숨김.

## Verify

- $codex-task trace --for-ai.
- git revert dry review.
- post-rollback tests.

## Evidence

- TASK trace와 대상 commit 목록이 있습니다.
- revert diff가 unrelated 변경을 포함하지 않습니다.
- post-rollback smoke 결과와 남은 위험을 보고합니다.
- revert conflict는 파일별 의도와 테스트 근거를 남깁니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
