#!/usr/bin/env python3
from __future__ import annotations

import sys
from _pogo_settings import (
    VALID_GIT_TARGETS,
    VALID_LANGUAGES,
    git_summary,
    language_summary,
    load_state,
    clear_subagent_evidence,
    save_state,
    subagent_auto_summary,
    subagent_evidence_status,
)

VALID_VALUES = {"on": True, "off": False}

COMMANDS = """  $pogo-settings
  $pogo-settings status
  $pogo-settings git status
  $pogo-settings git commit on|off|once
  $pogo-settings git push on|off|once
  $pogo-settings git merge on|off|once
  $pogo-settings git all on|off|once
  $pogo-settings lang status
  $pogo-settings lang ko|en|bilingual
  $pogo-settings subagent status
  $pogo-settings subagent auto on|off|toggle
  $pogo-settings evidence status|clear
  $pogo-subagent-auto [status|on|off|toggle]  # 기본: status"""


def lang_mode(state: dict) -> str:
    return language_summary(state)


def label(state: dict, key: str) -> str:
    mode = lang_mode(state)
    ko = {
        "usage_title": "현재 설정",
        "commands": "명령",
        "git": "Git 설정",
        "git_updated": "Git 설정 업데이트",
        "lang": "Lang 설정",
        "lang_updated": "Lang 설정 업데이트",
        "subagent": "Subagent auto 설정",
        "subagent_updated": "Subagent auto 업데이트",
        "evidence": "Subagent evidence",
        "evidence_cleared": "Subagent evidence 삭제",
    }
    en = {
        "usage_title": "Pogo settings",
        "commands": "Commands",
        "git": "Pogo settings git",
        "git_updated": "Pogo settings git updated",
        "lang": "Pogo settings lang",
        "lang_updated": "Pogo settings lang updated",
        "subagent": "Pogo settings subagent auto",
        "subagent_updated": "Pogo settings subagent auto updated",
        "evidence": "Pogo settings subagent evidence",
        "evidence_cleared": "Pogo settings subagent evidence cleared",
    }
    if mode == "ko":
        return ko[key]
    if mode == "bilingual":
        return f"{ko[key]} / {en[key]}"
    return en[key]


def usage_text() -> str:
    state = load_state()
    return (
        f"{label(state, 'usage_title')}: "
        f"{git_summary(state)}, {subagent_auto_summary(state)}, lang={language_summary(state)}\n\n"
        f"{label(state, 'commands')}:\n{COMMANDS}"
    ).rstrip()


def show() -> int:
    print(usage_text())
    return 0


def usage_error() -> int:
    print(usage_text(), file=sys.stderr)
    return 2


def show_git() -> int:
    state = load_state()
    print(f"{label(state, 'git')}: {git_summary(state)}")
    return 0


def set_git(target: str, value: str) -> int:
    if target not in VALID_GIT_TARGETS:
        return usage_error()
    state = load_state()
    if value in VALID_VALUES:
        state["gitAutomation"][target] = VALID_VALUES[value]
        if VALID_VALUES[value]:
            state["gitAllowOnce"][target] = False
    elif value == "once":
        state["gitAutomation"][target] = False
        state["gitAllowOnce"][target] = True
    else:
        return usage_error()
    save_state(state)
    print(f"{label(state, 'git_updated')}: {git_summary(state)}")
    return 0


def set_git_all(value: str) -> int:
    state = load_state()
    if value in VALID_VALUES:
        enabled = VALID_VALUES[value]
        for target in VALID_GIT_TARGETS:
            state["gitAutomation"][target] = enabled
            state["gitAllowOnce"][target] = False
    elif value == "once":
        for target in VALID_GIT_TARGETS:
            state["gitAutomation"][target] = False
            state["gitAllowOnce"][target] = True
    else:
        return usage_error()
    save_state(state)
    print(f"{label(state, 'git_updated')}: {git_summary(state)}")
    return 0


def show_lang() -> int:
    state = load_state()
    print(f"{label(state, 'lang')}: {language_summary(state)}")
    return 0


def set_lang(lang: str) -> int:
    if lang not in VALID_LANGUAGES:
        return usage_error()
    state = load_state()
    state["language"]["mode"] = lang
    save_state(state)
    print(f"{label(state, 'lang_updated')}: {language_summary(state)}")
    return 0


def show_subagent() -> int:
    state = load_state()
    print(f"{label(state, 'subagent')}: {subagent_auto_summary(state)}")
    return 0


def set_subagent_auto(value: str) -> int:
    state = load_state()
    if value == "toggle":
        state["subagent"]["auto"] = not bool(state["subagent"].get("auto"))
    elif value in VALID_VALUES:
        state["subagent"]["auto"] = VALID_VALUES[value]
    else:
        return usage_error()
    save_state(state)
    print(f"{label(state, 'subagent_updated')}: {subagent_auto_summary(state)}")
    return 0


def show_evidence() -> int:
    state = load_state()
    ok, detail = subagent_evidence_status()
    result = "PASS" if ok else "FAILED"
    print(f"{label(state, 'evidence')}: {result} - {detail}")
    return 0 if ok else 1


def clear_evidence() -> int:
    state = load_state()
    removed = clear_subagent_evidence()
    detail = "removed" if removed else "already empty"
    print(f"{label(state, 'evidence_cleared')}: {detail}")
    return 0


def main(argv: list[str]) -> int:
    if not argv or argv == ["status"]:
        return show()
    if argv[:1] == ["git"]:
        args = argv[1:]
        if not args or args == ["status"]:
            return show_git()
        if len(args) == 2 and args[0] in VALID_GIT_TARGETS:
            return set_git(args[0], args[1])
        if len(args) == 2 and args[0] == "all":
            return set_git_all(args[1])
        return usage_error()
    if argv[:1] == ["lang"]:
        args = argv[1:]
        if not args or args == ["status"]:
            return show_lang()
        if len(args) == 1:
            return set_lang(args[0])
        return usage_error()
    if argv[:1] == ["subagent"]:
        args = argv[1:]
        if not args or args == ["status"]:
            return show_subagent()
        if args[:1] == ["auto"]:
            if len(args) == 1 or args == ["auto", "status"]:
                return show_subagent()
            if len(args) == 2:
                return set_subagent_auto(args[1])
        return usage_error()
    if argv[:1] == ["evidence"]:
        args = argv[1:]
        if not args or args == ["status"]:
            return show_evidence()
        if args == ["clear"]:
            return clear_evidence()
        return usage_error()
    return usage_error()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
