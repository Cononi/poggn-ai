#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

VALID_GIT_TARGETS = ("commit", "push", "merge")
VALID_LANGUAGES = {"ko", "en", "bilingual"}
DEFAULT_STATE = {
    "gitAutomation": {"commit": False, "push": False, "merge": False},
    "gitAllowOnce": {"commit": False, "push": False, "merge": False},
    "codexEdit": True,
    "language": {"mode": "ko"},
    "subagent": {"auto": False},
}


def repo_root() -> Path:
    current = Path(__file__).resolve()
    for path in (current, *current.parents):
        if path.name == ".codex":
            return path.parent
    raise SystemExit("Unable to locate .codex directory")


ROOT = repo_root()
STATE_DIR = ROOT / "pogo-state"
STATE_PATH = STATE_DIR / "pogo-settings.json"
LOCAL_STATE_PATH = STATE_DIR / "pogo-settings.local.json"
SUBAGENT_EVIDENCE_PATH = STATE_DIR / "subagent-evidence.json"
SUBAGENT_EVIDENCE_AGENTS = {"pogo-verifier", "pogo-tester"}
SUBAGENT_EVIDENCE_RESULTS = {"PASS"}
SUBAGENT_EVIDENCE_MAX_AGE_SECONDS = 24 * 60 * 60


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


def _read_state_file(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid pogo settings JSON at {path}: {exc}") from exc
    except OSError as exc:
        raise SystemExit(f"Unable to read pogo settings at {path}: {exc}") from exc
    return _require_dict(data, label)


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

    if "codexEdit" in raw:
        state["codexEdit"] = _require_bool(raw["codexEdit"], "codexEdit")

    if "language" in raw:
        language = _require_dict(raw["language"], "language")
        mode = language.get("mode", state["language"]["mode"])
        if mode not in VALID_LANGUAGES:
            allowed = ", ".join(sorted(VALID_LANGUAGES))
            raise SystemExit(f"Invalid pogo settings: language.mode must be one of {allowed}")
        state["language"]["mode"] = mode

    if "subagent" in raw:
        subagent = _require_dict(raw["subagent"], "subagent")
        if "auto" in subagent:
            state["subagent"]["auto"] = _require_bool(subagent["auto"], "subagent.auto")

    return state


def _merge_state_data(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = json.loads(json.dumps(base))
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged


def load_state() -> dict[str, Any]:
    base_data = _read_state_file(STATE_PATH, "root")
    local_data = _read_state_file(LOCAL_STATE_PATH, "root")
    return normalize_state(_merge_state_data(base_data, local_data))


def _state_overrides(default_state: dict[str, Any], current_state: dict[str, Any]) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    for key in ("gitAutomation", "gitAllowOnce"):
        base_child = default_state.get(key, {})
        current_child = current_state.get(key, {})
        diff: dict[str, Any] = {}
        for child_key, base_value in base_child.items():
            if current_child.get(child_key) != base_value:
                diff[child_key] = current_child.get(child_key)
        if diff:
            overrides[key] = diff


    if current_state.get("codexEdit") != default_state.get("codexEdit"):
        overrides["codexEdit"] = current_state.get("codexEdit")

    if current_state.get("language", {}).get("mode") != default_state.get("language", {}).get("mode"):
        overrides["language"] = {"mode": current_state.get("language", {}).get("mode")}

    if current_state.get("subagent", {}).get("auto") != default_state.get("subagent", {}).get("auto"):
        overrides["subagent"] = {"auto": current_state.get("subagent", {}).get("auto")}

    return overrides


def save_state(state: dict[str, Any]) -> None:
    normalized = normalize_state(state)
    base_data = _read_state_file(STATE_PATH, "root")
    base_state = normalize_state(base_data)
    overrides = _state_overrides(base_state, normalized)
    if overrides:
        LOCAL_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        LOCAL_STATE_PATH.write_text(json.dumps(overrides, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return
    if LOCAL_STATE_PATH.exists():
        LOCAL_STATE_PATH.unlink()


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


def subagent_auto_summary(state: dict[str, Any]) -> str:
    enabled = bool(state.get("subagent", {}).get("auto"))
    return f"subagent-auto={onoff(enabled)}"


def subagent_auto_enabled(state: dict[str, Any]) -> bool:
    return bool(state.get("subagent", {}).get("auto"))


def _git_lines(*args: str) -> tuple[bool, list[str] | str]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        return False, str(exc)
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"git {' '.join(args)} failed"
        return False, detail
    return True, [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _current_branch() -> tuple[bool, str]:
    ok, lines_or_detail = _git_lines("branch", "--show-current")
    if not ok:
        return False, str(lines_or_detail)
    lines = lines_or_detail if isinstance(lines_or_detail, list) else []
    if not lines:
        return False, "detached HEAD is not supported for subagent evidence"
    return True, lines[0]


def _current_head() -> tuple[bool, str]:
    ok, lines_or_detail = _git_lines("rev-parse", "HEAD")
    if not ok:
        return False, str(lines_or_detail)
    lines = lines_or_detail if isinstance(lines_or_detail, list) else []
    if not lines:
        return False, "unable to resolve HEAD"
    return True, lines[0]


def _current_changed_files() -> tuple[bool, list[str] | str]:
    names: set[str] = set()
    for args in (("diff", "--name-only"), ("diff", "--cached", "--name-only")):
        ok, lines_or_detail = _git_lines(*args)
        if not ok:
            return False, str(lines_or_detail)
        names.update(lines_or_detail if isinstance(lines_or_detail, list) else [])
    ok, lines_or_detail = _git_lines("ls-files", "--others", "--exclude-standard")
    if not ok:
        return False, str(lines_or_detail)
    names.update(lines_or_detail if isinstance(lines_or_detail, list) else [])
    names.discard(str(SUBAGENT_EVIDENCE_PATH.relative_to(ROOT)))
    return True, sorted(names)


def _read_subagent_evidence() -> tuple[bool, dict[str, Any] | str]:
    if not SUBAGENT_EVIDENCE_PATH.exists():
        return False, f"missing {SUBAGENT_EVIDENCE_PATH.relative_to(ROOT)}"
    try:
        age_seconds = time.time() - SUBAGENT_EVIDENCE_PATH.stat().st_mtime
    except OSError as exc:
        return False, f"unable to stat evidence: {exc}"
    if age_seconds >= SUBAGENT_EVIDENCE_MAX_AGE_SECONDS:
        return False, "evidence is 24h or older; run `$pogo-settings evidence clear`"
    try:
        data = json.loads(SUBAGENT_EVIDENCE_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"invalid JSON: {exc}"
    if not isinstance(data, dict):
        return False, "root must be an object"
    return True, data


def subagent_evidence_status(strict: bool = True) -> tuple[bool, str]:
    ok, data_or_detail = _read_subagent_evidence()
    if not ok:
        return False, str(data_or_detail)
    data = data_or_detail if isinstance(data_or_detail, dict) else {}
    if data.get("version") != 1:
        return False, "version must be 1"
    agents = data.get("agents")
    if not isinstance(agents, list):
        return False, "agents must be a list"
    has_pass = False
    for item in agents:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        result = item.get("result")
        if name in SUBAGENT_EVIDENCE_AGENTS and result in SUBAGENT_EVIDENCE_RESULTS:
            has_pass = True
            break
    if not has_pass:
        return False, "requires PASS evidence from pogo-verifier or pogo-tester"
    changed_files = data.get("changedFiles")
    if not isinstance(changed_files, list):
        return False, "changedFiles must be a list"
    if not all(isinstance(item, str) and item.strip() for item in changed_files):
        return False, "changedFiles must contain non-empty strings"
    if not strict:
        return True, "ok"

    branch = data.get("branch")
    if not isinstance(branch, str) or not branch.strip():
        return False, "branch must be a non-empty string"
    ok, current_branch = _current_branch()
    if not ok:
        return False, current_branch
    if branch != current_branch:
        return False, f"branch mismatch: evidence={branch}, current={current_branch}"

    head = data.get("head")
    if not isinstance(head, str) or not head.strip():
        return False, "head must be a non-empty string"
    ok, current_head = _current_head()
    if not ok:
        return False, current_head
    if head != current_head:
        return False, f"head mismatch: evidence={head}, current={current_head}"

    ok, current_files_or_detail = _current_changed_files()
    if not ok:
        return False, str(current_files_or_detail)
    current_files = current_files_or_detail if isinstance(current_files_or_detail, list) else []
    evidence_files = sorted({item.strip() for item in changed_files})
    if evidence_files != current_files:
        return False, "changedFiles mismatch: evidence does not match current git changes"
    return True, "ok"


def clear_subagent_evidence() -> bool:
    if not SUBAGENT_EVIDENCE_PATH.exists():
        return False
    SUBAGENT_EVIDENCE_PATH.unlink()
    return True
