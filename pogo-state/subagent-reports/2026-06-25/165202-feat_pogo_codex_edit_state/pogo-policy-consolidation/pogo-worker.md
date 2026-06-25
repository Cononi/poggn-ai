# AGENTS/SKILL 정책 통합 재작업 보고서

## summary
- 작업 수행 이유: 이전 결과가 사용자 의도와 반대로 AGENTS와 SKILL의 중심 규칙 위치가 역전되어, 실질 정책 문서(`AGENTS.md`) 중심 구조를 복원해야 했습니다.
- 수행한 작업: `AGENTS.md`를 61줄의 실질 정책 문서로 재작성(작업 시작 규칙, 메인 최소 개입, Subagent 병렬 분배/통합/Thin Mode, 보고서 형식/경로, skill routing, Git/Release 규칙, 구현·검증 원칙 포함). `.codex/skills/pogo/SKILL.md`는 AGENTS 참조 shim으로 최소화. `__pycache__` 삭제 후 검증 수행.
- 작업 결과: 정책 단일 출처가 다시 `AGENTS.md`로 확정되었고 SKILL은 보조 shim만 유지.
- 검토 에이전트 결과: `pogo_policy_ci.py` PASS, `AGENTS.md` 61줄(100줄 미만), `__pycache__` 삭제 확인.
- 재검토 필요성: 없음.
- 완성도: 100%(요청 항목 전부 반영).

## changed_files
- AGENTS.md
- .codex/skills/pogo/SKILL.md
- `pogo-state/subagent-reports/2026-06-25/165202-feat_pogo_codex_edit_state/pogo-policy-consolidation/pogo-worker.md`

## evidence
1. `wc -l AGENTS.md` → `61 AGENTS.md`
2. `python3 .codex/script/pogo_policy_ci.py` → `pogo-policy: PASS`
3. `find . -path '*__pycache__*' -print` → 출력 없음(삭제 완료)

## risks
- 문서 변경만으로 즉시 기능 회귀 가능성은 낮고, 운영 정책만 중앙화로 인해 향후 정책 변경 시 AGENTS/문서 동기화가 필요.
- `.codex/skills/pogo/SKILL.md`가 매우 축약되어 있어 정책 변경은 항상 AGENTS.md를 통해 적용해야 함.
- 현재 변경은 문서 레벨이므로 런타임 동작 리스크는 없음.

## report_file
- pogo-state/subagent-reports/2026-06-25/165202-feat_pogo_codex_edit_state/pogo-policy-consolidation/pogo-worker.md

## reviewer_decision
PASS
