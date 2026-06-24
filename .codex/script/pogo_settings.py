#!/usr/bin/env python3
from __future__ import annotations

import sys
from _pogo_settings import (
    VALID_GIT_TARGETS,
    VALID_LANGUAGES,
    git_summary,
    language_summary,
    load_state,
    save_state,
)

VALID_VALUES = {"on": True, "off": False}

COMMANDS = """  $pogo-settings
  $pogo-settings status
  $pogo-settings git status
  $pogo-settings git commit on|off|once
  $pogo-settings git push on|off|once
  $pogo-settings git merge on|off|once
  $pogo-settings git all off|once
  $pogo-settings lang status
  $pogo-settings lang ko|en|bilingual"""


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
    }
    en = {
        "usage_title": "Pogo settings",
        "commands": "Commands",
        "git": "Pogo settings git",
        "git_updated": "Pogo settings git updated",
        "lang": "Pogo settings lang",
        "lang_updated": "Pogo settings lang updated",
    }
    if mode == "ko":
        return ko[key]
    if mode == "bilingual":
        return f"{ko[key]} / {en[key]}"
    return en[key]


def usage_text() -> str:
    state = load_state()
    return (
        f"{label(state, 'usage_title')}: {git_summary(state)}, lang={language_summary(state)}\n\n"
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
    if value == "off":
        for target in VALID_GIT_TARGETS:
            state["gitAutomation"][target] = False
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
    return usage_error()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
