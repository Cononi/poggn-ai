# 코드 구현 설명

핵심 구현은 작은 Python 스크립트로 나뉩니다.
각 파일은 200줄 이하를 목표로 합니다.

codex_state.py는 workflow 디렉터리를 만들고 TASK를 관리합니다.
codex_trace_view.py는 JSONL을 읽어 TASKS.md를 다시 렌더링합니다.
codex_task_git.py는 git commit을 만들고 TASK와 연결합니다.
codex_lanes.py는 worktree와 병렬 실행 CSV를 만듭니다.
codex_quality.py는 변경 파일을 스캔해 품질 위험을 JSON으로 출력합니다.
codex_shortcuts.py는 $codex-* 프롬프트를 스크립트 실행으로 바꿉니다.
codex_wiki.py는 docs Markdown을 검색 가능한 index.html로 합칩니다.

hook 흐름입니다.

```text
UserPromptSubmit
  -> dispatch.py
  -> codex_shortcuts.py
  -> 해당 script 실행
  -> decision:block 반환
```

이렇게 하면 상태 명령이 모델 토큰을 쓰지 않습니다.
