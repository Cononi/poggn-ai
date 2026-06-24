#!/usr/bin/env python3
from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / ".codex" / "script"
sys.path.insert(0, str(SCRIPT_DIR))

from _pogo_settings import (
    consume_git_once,
    git_allowed,
    git_summary,
    language_summary,
    load_state,
    subagent_auto_summary,
    subagent_evidence_status,
)

GIT_TARGETS = ("commit", "push", "merge")
SHELL_SEPARATORS = {";", "&", "&&", "|", "||", "(", ")"}
GIT_OPTIONS_WITH_VALUE = {
    "-C",
    "-c",
    "--git-dir",
    "--work-tree",
    "--namespace",
    "--exec-path",
    "--config-env",
}


def read_payload() -> Any:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {"raw": raw}


def block(reason: str) -> dict[str, str]:
    return {"decision": "block", "reason": reason}


def prompt_text(payload: Any) -> str:
    if isinstance(payload, dict):
        return str(payload.get("prompt", ""))
    return ""


def run_script(args: list[str]) -> str:
    proc = subprocess.run(
        args,
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output = proc.stdout.strip() or proc.stderr.strip() or "ok"
    if proc.returncode:
        output = "failed:\n" + output
    return output


def run_shortcut(prompt: str) -> dict[str, str] | None:
    text = prompt.strip()
    if not text.startswith("$"):
        return None
    try:
        parts = shlex.split(text)
    except ValueError as exc:
        return block(str(exc))
    if not parts:
        return None
    script = SCRIPT_DIR / "pogo_settings.py"
    if parts[0] == "$pogo-settings":
        return block(run_script([sys.executable, str(script), *parts[1:]]))
    if parts[0] == "$pogo-subagent-auto":
        args = parts[1:] if len(parts) > 1 else ["status"]
        return block(run_script([sys.executable, str(script), "subagent", "auto", *args]))
    return None


def flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            out.extend(flatten_strings(item))
        return out
    if isinstance(value, dict):
        out: list[str] = []
        for item in value.values():
            out.extend(flatten_strings(item))
        return out
    return []


def command_text(payload: Any) -> str:
    return "\n".join(flatten_strings(payload))


def shell_tokens(text: str) -> list[str]:
    try:
        lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError:
        return text.replace(";", " ; ").replace("&", " & ").replace("|", " | ").split()


def git_subcommands(text: str) -> set[str]:
    commands: set[str] = set()
    tokens = shell_tokens(text)
    for index, token in enumerate(tokens):
        if token != "git":
            continue
        cursor = index + 1
        while cursor < len(tokens):
            item = tokens[cursor]
            if item in SHELL_SEPARATORS:
                break
            if item in GIT_OPTIONS_WITH_VALUE:
                cursor += 2
                continue
            if any(item.startswith(option + "=") for option in GIT_OPTIONS_WITH_VALUE):
                cursor += 1
                continue
            if item.startswith("-"):
                cursor += 1
                continue
            commands.add(item)
            break
    return commands


def deny_message(mode: str, key: str) -> str:
    en = (
        f"Blocked by pogo settings: git {key} automation is off. "
        f"Use `$pogo-settings git {key} once` for one run, "
        f"or `$pogo-settings git {key} on` for ongoing automation."
    )
    ko = (
        f"pogo settings가 git {key} 실행을 차단했습니다. "
        f"한 번만 허용하려면 `$pogo-settings git {key} once`, "
        f"계속 허용하려면 `$pogo-settings git {key} on`을 사용하세요."
    )
    if mode == "ko":
        return ko
    if mode == "bilingual":
        return f"{ko}\n{en}"
    return en


def subagent_evidence_deny_message(mode: str, key: str, detail: str) -> str:
    path = ".codex/state/subagent-evidence.json"
    en = (
        f"Blocked by pogo subagent-auto: git {key} requires subagent evidence. "
        f"Create {path} with PASS evidence from pogo-verifier or pogo-tester. Detail: {detail}"
    )
    ko = (
        f"pogo subagent-auto가 git {key} 실행을 차단했습니다. "
        f"pogo-verifier 또는 pogo-tester PASS 증거를 {path}에 남겨야 합니다. 상세: {detail}"
    )
    if mode == "ko":
        return ko
    if mode == "bilingual":
        return f"{ko}\n{en}"
    return en


def run_pre_tool_use() -> int:
    state = load_state()
    payload = read_payload()
    text = command_text(payload)
    mode = language_summary(state)
    commands = git_subcommands(text)
    for key in GIT_TARGETS:
        if key in commands:
            if not git_allowed(state, key):
                print(deny_message(mode, key), file=sys.stderr)
                return 1
            if state.get("subagent", {}).get("auto"):
                ok, detail = subagent_evidence_status()
                if not ok:
                    print(subagent_evidence_deny_message(mode, key, detail), file=sys.stderr)
                    return 1
            consume_git_once(state, key)
            return 0
    return 0


def run_session_start() -> int:
    state = load_state()
    mode = language_summary(state)
    subagent_auto = subagent_auto_summary(state)
    auto_note = ""
    if state.get("subagent", {}).get("auto"):
        if mode == "ko":
            auto_note = " 개발/수정/리뷰/QA 작업은 Subagents 필수입니다."
        elif mode == "bilingual":
            auto_note = " 개발/수정/리뷰/QA 작업은 Subagents 필수입니다. Subagents are required for development/review/QA tasks."
        else:
            auto_note = " Subagents are required for development/review/QA tasks."
    if mode == "ko":
        print(f"Pogo 설정: {git_summary(state)}, {subagent_auto}, lang={mode}.{auto_note}")
    elif mode == "bilingual":
        print(f"Pogo 설정 / Pogo settings: {git_summary(state)}, {subagent_auto}, lang={mode}.{auto_note}")
    else:
        print(f"Pogo settings: {git_summary(state)}, {subagent_auto}, lang={mode}.{auto_note}")
    return 0


def run_user_prompt_submit() -> int:
    result = run_shortcut(prompt_text(read_payload()))
    if result is None:
        print(json.dumps({"continue": True, "suppressOutput": True}, ensure_ascii=False))
        return 0
    print(json.dumps(result, ensure_ascii=False))
    return 0


def main(argv: list[str]) -> int:
    event = argv[0] if argv else ""
    if event == "pre-tool-use":
        return run_pre_tool_use()
    if event == "session-start":
        return run_session_start()
    if event == "user-prompt-submit":
        return run_user_prompt_submit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
