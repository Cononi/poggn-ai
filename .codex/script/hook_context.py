#!/usr/bin/env python3
from __future__ import annotations
import json, shlex, sys
from pathlib import Path
import codex_shortcuts, lib

CTX = {
    "ko": {
        "on": "Codex edit mode: codex. .codex 수정 가능, 프로젝트 파일 변경은 대기합니다.",
        "off": "Codex edit mode: project. 프로젝트 파일 수정 가능, .codex 수정은 보호됩니다.",
        "status": "현재 모드",
        "usage": "사용법: $codex-edit-mode on|off|status",
        "deny": ".codex 수정은 $codex-edit-mode on 후 가능합니다.",
    },
    "en": {
        "on": "Codex edit mode: codex. .codex edits are allowed; project edits should wait.",
        "off": "Codex edit mode: project. Project files are editable; .codex edits are protected.",
        "status": "Current mode",
        "usage": "Usage: $codex-edit-mode on|off|status",
        "deny": "Edit .codex only after $codex-edit-mode on.",
    },
}
PROTECTED = [
    ".codex/agents",
    ".codex/skills",
    ".codex/hooks",
    ".codex/rules",
    ".codex/config.toml",
    ".codex/AGENTS.md",
    ".codex/script",
]
WRITE_HINTS = [
    "apply_patch",
    ">",
    ">>",
    "tee",
    "touch",
    "mkdir",
    "rm ",
    "mv ",
    "cp ",
    "cat >",
    "python3 -",
    "python -",
    "perl -",
    "sed -i",
]


def mode_path() -> Path:
    return lib.find_codex() / "state" / "edit_mode.json"


def read_mode() -> dict:
    return lib.read_json(mode_path(), {"mode": "project", "reason": "default"})


def write_mode(mode: str, reason: str) -> None:
    lib.write_json(mode_path(), {"mode": mode, "reason": reason, "updated_at": lib.now()})


def read_input() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}


def parse_edit(prompt: str) -> tuple[str, str] | None:
    text = prompt.strip()
    if not text.startswith("$codex-edit-mode"):
        return None
    try:
        parts = shlex.split(text)
    except ValueError:
        return ("usage", "")
    if not parts or parts[0] != "$codex-edit-mode":
        return None
    if len(parts) < 2 or parts[1] not in {"on", "off", "status"}:
        return ("usage", "")
    return (parts[1], " ".join(parts[2:]).strip())


def block(reason: str) -> dict:
    return {"decision": "block", "reason": reason}


def edit_output(cmd: str, reason: str, lang: str) -> dict:
    if cmd == "usage":
        return block(CTX[lang]["usage"])
    if cmd == "on":
        write_mode("codex", reason or "codex maintenance")
        return block(CTX[lang]["on"])
    if cmd == "off":
        write_mode("project", reason or "project work")
        return block(CTX[lang]["off"])
    status = read_mode().get("mode", "project")
    return block(f"{CTX[lang]['status']}: {status}")


def tool_text(payload: dict) -> str:
    data = payload.get("tool_input", {})
    if isinstance(data, dict) and "command" in data:
        return f"{payload.get('tool_name', '')} {data.get('command', '')}"
    return f"{payload.get('tool_name', '')} {json.dumps(data, ensure_ascii=False)}"


def protected_write(payload: dict) -> bool:
    if read_mode().get("mode") == "codex":
        return False
    text = tool_text(payload).replace("\\", "/")
    if not any(path in text for path in PROTECTED):
        return False
    if str(payload.get("tool_name", "")) in {"apply_patch", "Edit", "Write"}:
        return True
    return any(hint in text for hint in WRITE_HINTS)


def deny(lang: str) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": CTX[lang]["deny"],
        }
    }


def prompt_output(prompt: str, lang: str) -> dict:
    parsed = parse_edit(prompt)
    if parsed:
        return edit_output(parsed[0], parsed[1], lang)
    parts = codex_shortcuts.parse(prompt)
    if parts:
        return codex_shortcuts.run(parts)
    return {"continue": True}


def output(event: str) -> dict:
    lang = lib.language()
    if event == "pre_tool_use":
        return deny(lang) if protected_write(read_input()) else {}
    if event == "user_prompt_submit":
        prompt = str(read_input().get("prompt", ""))
        return prompt_output(prompt, lang)
    return {"continue": True, "suppressOutput": True}


def main() -> int:
    event = sys.argv[1] if len(sys.argv) > 1 else "session_start"
    print(json.dumps(output(event), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
