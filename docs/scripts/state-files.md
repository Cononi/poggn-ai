# 상태 파일 구현

.codex-state 아래 파일은 스크립트가 읽는 원본 상태입니다.

- state.json: workflow, branch, phase, version 정보
- tasks.jsonl: TASK 목록과 상태
- lanes.jsonl: 병렬 lane, worktree, branch, deps 정보
- commits.jsonl: TASK, lane, commit, 변경 파일 연결
- events.jsonl: 시간순 이벤트 로그
- TASKS.md: 사람이 보는 요약본

TASKS.md는 원본이 아닙니다.
스크립트가 JSONL을 읽고 매번 다시 생성합니다.

이 구조 덕분에 AI가 긴 TASKS.md를 직접 편집하지 않아도 됩니다.
완료 체크, commit 연결, 파일 변경 요약은 모두 스크립트가 처리합니다.
