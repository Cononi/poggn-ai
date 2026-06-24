#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS_TOKEN_BUDGET = 900

TOKEN_FILES = [
    ROOT / "AGENTS.md",
    *sorted((ROOT / ".codex" / "agents").glob("*.toml")),
    ROOT / ".codex" / "skills" / "pogo" / "SKILL.md",
    ROOT / ".codex" / "skills" / "pogo-settings" / "SKILL.md",
    ROOT / ".codex" / "skills" / "pogo-subagent-auto" / "SKILL.md",
]
PYTHON_FILES = [
    ROOT / ".codex" / "hooks" / "pogo_policy_hook.py",
    ROOT / ".codex" / "script" / "_pogo_settings.py",
    ROOT / ".codex" / "script" / "pogo_settings.py",
    ROOT / ".codex" / "script" / "pogo_policy_ci.py",
    ROOT / ".codex" / "script" / "pogo_branch_protection.py",
]


def fail(message: str) -> int:
    print(f"FAILED: {message}", file=sys.stderr)
    return 1


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def check_python() -> None:
    for path in PYTHON_FILES:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path.relative_to(ROOT)))


def check_toml() -> None:
    for path in sorted((ROOT / ".codex" / "agents").glob("*.toml")):
        tomllib.loads(path.read_text(encoding="utf-8"))


def check_settings_json() -> None:
    path = ROOT / ".codex" / "state" / "pogo-settings.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("pogo-settings root must be an object")
    if data.get("subagent", {}).get("auto") is not False:
        raise ValueError("committed pogo-settings.json must keep subagent.auto=false by default")


def check_no_committed_local_evidence() -> None:
    result = git("ls-files", "--error-unmatch", ".codex/state/subagent-evidence.json")
    if result.returncode == 0:
        raise ValueError(".codex/state/subagent-evidence.json must stay local and untracked")


def estimate_tokens(text: str) -> int:
    return max(1, round(len(text) / 4))


def token_report() -> None:
    entries: list[tuple[int, Path]] = []
    total = 0
    agents_tokens = 0
    for path in TOKEN_FILES:
        if not path.exists():
            continue
        tokens = estimate_tokens(path.read_text(encoding="utf-8"))
        if path == ROOT / "AGENTS.md":
            agents_tokens = tokens
        entries.append((tokens, path))
        total += tokens
    if agents_tokens > AGENTS_TOKEN_BUDGET:
        raise ValueError(f"AGENTS.md token estimate {agents_tokens} exceeds budget {AGENTS_TOKEN_BUDGET}")
    largest = sorted(entries, reverse=True)[:5]
    print(f"token-estimate-total={total}")
    print(f"token-estimate-agents={agents_tokens}/{AGENTS_TOKEN_BUDGET}")
    for tokens, path in largest:
        print(f"token-estimate-file={path.relative_to(ROOT)} tokens~{tokens}")


def main() -> int:
    try:
        check_python()
        check_toml()
        check_settings_json()
        check_no_committed_local_evidence()
    except Exception as exc:
        return fail(str(exc))
    token_report()
    print("pogo-policy: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
