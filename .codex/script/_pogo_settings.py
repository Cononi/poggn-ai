#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

VALID_GIT_TARGETS = ("commit", "push", "merge")
VALID_LANGUAGES = {"ko", "en", "bilingual"}
DEFAULT_STATE = {
    "gitAutomation": {"commit": False, "push": False, "merge": False},
    "gitAllowOnce": {"commit": False, "push": False, "merge": False},
    "language": {"mode": "ko"},
}


def repo_root() -> Path:
    current = Path(__file__).resolve()
    for path in (current, *current.parents):
        if path.name == ".codex":
            return path.parent
    raise SystemExit("Unable to locate .codex directory")


ROOT = repo_root()
STATE_PATH = ROOT / ".codex" / "state" / "pogo-settings.json"


def _copy_default() -> dict[str, Any]:
    return json.loads(json.dumps(DEFAULT_STATE))


def _require_dict(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SystemExit(f"Invalid pogo settings: {path} must be an object")
    return value


def _require_bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise SystemExit(f"Invalid pogo settings: {path} must be true or false")
    return value


def normalize_state(data: Any) -> dict[str, Any]:
    raw = _require_dict(data, "root")
    state = _copy_default()

    if "gitAutomation" in raw:
        git = _require_dict(raw["gitAutomation"], "gitAutomation")
        for key in VALID_GIT_TARGETS:
            if key in git:
                state["gitAutomation"][key] = _require_bool(git[key], f"gitAutomation.{key}")

    if "gitAllowOnce" in raw:
        once = _require_dict(raw["gitAllowOnce"], "gitAllowOnce")
        for key in VALID_GIT_TARGETS:
            if key in once:
                state["gitAllowOnce"][key] = _require_bool(once[key], f"gitAllowOnce.{key}")

    if "language" in raw:
        language = _require_dict(raw["language"], "language")
        mode = language.get("mode", state["language"]["mode"])
        if mode not in VALID_LANGUAGES:
            allowed = ", ".join(sorted(VALID_LANGUAGES))
            raise SystemExit(f"Invalid pogo settings: language.mode must be one of {allowed}")
        state["language"]["mode"] = mode

    return state


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return _copy_default()
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid pogo settings JSON at {STATE_PATH}: {exc}") from exc
    except OSError as exc:
        raise SystemExit(f"Unable to read pogo settings at {STATE_PATH}: {exc}") from exc
    return normalize_state(data)


def save_state(state: dict[str, Any]) -> None:
    normalized = normalize_state(state)
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def onoff(value: bool) -> str:
    return "on" if value else "off"


def git_summary(state: dict[str, Any]) -> str:
    git = state["gitAutomation"]
    once = state.get("gitAllowOnce", {})
    active_once = [key for key in VALID_GIT_TARGETS if once.get(key)]
    summary = "commit={commit}, push={push}, merge={merge}".format(
        commit=onoff(bool(git.get("commit"))),
        push=onoff(bool(git.get("push"))),
        merge=onoff(bool(git.get("merge"))),
    )
    return f"{summary}, once={','.join(active_once) if active_once else 'none'}"


def language_summary(state: dict[str, Any]) -> str:
    return str(state["language"].get("mode", "ko"))


def git_allowed(state: dict[str, Any], target: str) -> bool:
    return bool(state["gitAutomation"].get(target)) or bool(state.get("gitAllowOnce", {}).get(target))


def consume_git_once(state: dict[str, Any], target: str) -> bool:
    if state["gitAutomation"].get(target):
        return False
    if state.get("gitAllowOnce", {}).get(target):
        state["gitAllowOnce"][target] = False
        save_state(state)
        return True
    return False
