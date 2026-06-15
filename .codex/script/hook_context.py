#!/usr/bin/env python3
from __future__ import annotations
import json, shlex, subprocess, sys
from pathlib import Path
import codex_shortcuts, lib

CTX = {
    "ko": {
        "project": "프로젝트 파일은 수정 가능하나 .codex는 수정하지 마세요.",
        "codex": ".codex 기능 수정이 허용됩니다. 프로젝트 파일 변경은 피하세요.",
        "lang": "문서와 설명은 현재 언어 정책을 따르세요.",
        "nogit": "Git이 없습니다. 설치할지 직접 설치할지 사용자에게 물으세요.",
        "init": "Git 저장소가 아니면 codex_git_bootstrap.py ensure를 실행하세요.",
        "on": "Codex 수정 모드가 켜졌습니다.",
        "off": "프로젝트 수정 모드로 돌아갑니다.",
        "status": "현재 모드", "usage": "사용법: $codex-edit-mode on|off|status",
        "deny": ".codex 수정은 $codex-edit-mode on 후 가능합니다.",
        "maw": "$maw는 한 질문에 한 답변만 받습니다. agent 개수는 묻지 마세요. "
               "기능 구현 agent는 구현만 수행합니다. 완료 commit 후 "
               "$codex-events가 필요한 test_writer, test_runner, qa, "
               "refactor, security lane만 자동 생성합니다. "
               "TASK는 .codex-state/{날짜}/{vN}-{제목}에 남기고, "
               "완료는 commit 연결 후에만 [x]로 표시하세요.",
        "saw": "$saw는 수술형 패치 모드입니다. 기본은 한 TASK, 한 agent, "
               "필요 skill, staged gate만 사용하세요. test, qa, security를 "
               "별도 agent로 만들지 말고 script gate로 처리하세요. "
               "범위가 크면 $maw 전환을 제안하세요.",
        "cmd": "상태, TASK, 품질 검사는 $codex-* shortcut을 우선 사용하세요. "
               "agent/skill이 없으면 $codex-capabilities inspect를 먼저 사용하세요.",
        "extend": "agent나 skill이 없으면 $codex-extend check를 먼저 실행하고, 중복이 없을 때만 --approve로 생성하세요.",
        "risk": "$saw/$maw 선택 전 $codex-risk classify를 우선 사용하세요.",
        "context": "긴 TASKS.md 대신 $codex-context pack --for-ai를 우선 사용하세요.",
        "quality": "commit 전 $codex-quality gate --for-ai 를 통과해야 합니다. "
                   "프론트는 TS/TSX, 재사용 컴포넌트, hook, typed client를 우선합니다.",
    },
    "en": {
        "project": "Project files are editable, but do not edit .codex.",
        "codex": ".codex maintenance is allowed. Avoid project file edits.",
        "lang": "Follow the current language policy for docs and replies.",
        "nogit": "Git is missing. Ask whether to install it or install manually.",
        "init": "If this is not a Git repo, run codex_git_bootstrap.py ensure.",
        "on": "Codex edit mode is enabled.",
        "off": "Returned to project edit mode.",
        "status": "Current mode", "usage": "Usage: $codex-edit-mode on|off|status",
        "deny": "Edit .codex only after $codex-edit-mode on.",
        "maw": "$maw asks one question at a time. Do not ask for agent count. "
               "Implementation agents implement only. After a completion commit, "
               "$codex-events creates only needed test_writer, test_runner, "
               "qa, refactor, and security lanes. Store TASK data under "
               ".codex-state/{date}/{vN}-{title}. Mark [x] only after commits.",
        "saw": "$saw is surgical patch mode. Default to one TASK, one agent, "
               "needed skills, and staged gates only. Do not create test, qa, "
               "or security agents for normal SAW. Use script gates instead. "
               "Suggest $maw when scope is large.",
        "cmd": "Use $codex-* shortcuts first for state, TASK, and quality work. "
               "Use $codex-capabilities inspect before adding agents or skills.",
        "extend": "If an agent or skill is missing, run $codex-extend check first and create only when no duplicate exists.",
        "risk": "Before choosing $saw or $maw, prefer $codex-risk classify.",
        "context": "Prefer $codex-context pack --for-ai instead of long TASKS.md reads.",
        "quality": "Before commit, pass $codex-quality gate --for-ai. "
                   "Frontend must prefer TS/TSX, reusable components, hooks, and typed clients.",
    },
}
PROTECTED = [".codex/agents", ".codex/skills", ".codex/hooks", ".codex/rules",
             ".codex/config.toml", ".codex/AGENTS.md", ".codex/script"]
WRITE_HINTS = ["apply_patch", ">", ">>", "tee", "touch", "mkdir", "rm ", "mv ",
               "cp ", "cat >", "python3 -", "python -", "perl -", "sed -i"]
CONTEXT_PREFIXES = ("$maw", "$saw", "$codex-", "/agent")
CONTEXT_HINTS = [
    "codex", ".codex", "maw", "saw", "task", "tasks", "agent", "skill",
    "hook", "git", "commit", "quality", "security", "test", "workflow",
    "lane", "state", "pipeline", "repo", "repository", "implement", "fix",
    "build", "create", "add", "remove", "delete", "refactor", "feature",
    "bug", "code", "file", "diff",
]
CONTEXT_HINTS_KO = [
    "코덱스", "리포", "저장소", "깃", "커밋", "태스크", "작업", "상태",
    "에이전트", "스킬", "훅", "품질", "보안", "검증", "워크플로우", "레인",
    "구현", "수정", "고쳐", "개선", "추가", "삭제", "리팩토", "테스트",
    "기능", "버그", "코드", "파일", "차이",
]


def mode_path() -> Path:
    return lib.find_codex() / "state" / "edit_mode.json"


def read_mode() -> dict:
    return lib.read_json(mode_path(), {"mode": "project", "reason": "default"})


def write_mode(mode: str, reason: str) -> None:
    lib.write_json(mode_path(), {"mode": mode, "reason": reason, "updated_at": lib.now()})


def git_note(root: Path, lang: str) -> str:
    if not lib.has_cmd("git"):
        return CTX[lang]["nogit"]
    proc = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=str(root),
                          text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return "" if proc.returncode == 0 else CTX[lang]["init"]


def needs_context(prompt: str) -> bool:
    text = prompt.strip()
    if not text:
        return False
    if text.startswith(CONTEXT_PREFIXES) or "$" in text:
        return True
    low = text.lower()
    return any(hint in low for hint in CONTEXT_HINTS) or any(hint in text for hint in CONTEXT_HINTS_KO)


def build(prompt: str = "") -> str:
    root = lib.root_dir(); lang = lib.language(); mode = read_mode().get("mode", "project")
    lines = [CTX[lang].get(mode, CTX[lang]["project"]), CTX[lang]["lang"],
             CTX[lang]["cmd"], CTX[lang]["risk"], CTX[lang]["context"],
             CTX[lang]["quality"], CTX[lang]["extend"]]
    if prompt.strip().startswith("$maw"):
        lines.append(CTX[lang]["maw"])
    if prompt.strip().startswith("$saw"):
        lines.append(CTX[lang]["saw"])
    note = git_note(root, lang)
    if note:
        lines.append(note)
    return "\n".join(lines)


def read_input() -> dict:
    try:
        raw = sys.stdin.read(); return json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}


def parse_edit(prompt: str) -> tuple[str, str] | None:
    text = prompt.strip()
    if not text.startswith("$codex-edit-mode"):
        return None
    try: parts = shlex.split(text)
    except ValueError: return ("usage", "")
    if not parts or parts[0] != "$codex-edit-mode": return None
    if len(parts) < 2 or parts[1] not in {"on", "off", "status"}: return ("usage", "")
    return (parts[1], " ".join(parts[2:]).strip())


def block(reason: str) -> dict:
    return {"decision": "block", "reason": reason}


def edit_output(cmd: str, reason: str, lang: str) -> dict:
    if cmd == "usage": return block(CTX[lang]["usage"])
    if cmd == "on": write_mode("codex", reason or "codex maintenance"); return block(CTX[lang]["on"])
    if cmd == "off": write_mode("project", reason or "project work"); return block(CTX[lang]["off"])
    return block(f"{CTX[lang]['status']}: {read_mode().get('mode', 'project')}")


def tool_text(payload: dict) -> str:
    data = payload.get("tool_input", {})
    if isinstance(data, dict) and "command" in data:
        return f"{payload.get('tool_name','')} {data.get('command','')}"
    return f"{payload.get('tool_name','')} {json.dumps(data, ensure_ascii=False)}"


def protected_write(payload: dict) -> bool:
    if read_mode().get("mode") == "codex": return False
    text = tool_text(payload).replace("\\", "/")
    if not any(path in text for path in PROTECTED): return False
    if str(payload.get("tool_name", "")) in {"apply_patch", "Edit", "Write"}: return True
    return any(hint in text for hint in WRITE_HINTS)


def deny(lang: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
            "permissionDecision": "deny", "permissionDecisionReason": CTX[lang]["deny"]}}


def prompt_output(prompt: str, lang: str) -> dict:
    parsed = parse_edit(prompt)
    if parsed:
        return edit_output(parsed[0], parsed[1], lang)
    parts = codex_shortcuts.parse(prompt)
    if parts:
        return codex_shortcuts.run(parts)
    if not needs_context(prompt):
        return {"continue": True}
    return {"continue": True, "hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
            "additionalContext": build(prompt)}}


def output(event: str) -> dict:
    lang = lib.language()
    if event == "pre_tool_use":
        return deny(lang) if protected_write(read_input()) else {}
    if event == "user_prompt_submit":
        prompt = str(read_input().get("prompt", "")); return prompt_output(prompt, lang)
    return {"continue": True, "systemMessage": build(), "suppressOutput": True}


def main() -> int:
    event = sys.argv[1] if len(sys.argv) > 1 else "session_start"
    print(json.dumps(output(event), ensure_ascii=False)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
