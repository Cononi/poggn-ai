#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS_TOKEN_BUDGET = 900
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")

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


def check_project_map() -> None:
    path = ROOT / ".codex" / "project-map.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("project-map version must be 1")
    projects = data.get("projects")
    if not isinstance(projects, list):
        raise ValueError("project-map projects must be a list")
    names: set[str] = set()
    for project in projects:
        if not isinstance(project, dict):
            raise ValueError("project-map project entries must be objects")
        name = project.get("name")
        if not isinstance(name, str) or not name or name in names:
            raise ValueError("project-map project names must be unique non-empty strings")
        names.add(name)
        paths = project.get("paths", project.get("path"))
        if isinstance(paths, str):
            paths = [paths]
        if not isinstance(paths, list) or not paths:
            raise ValueError(f"project-map {name}.paths must be a non-empty list")
        for item in paths:
            if not isinstance(item, str) or not item or item.startswith("/") or ".." in Path(item).parts:
                raise ValueError(f"project-map {name}.paths contains an invalid path")
        version_source = project.get("versionSource")
        if version_source is not None and (
            not isinstance(version_source, str)
            or not version_source
            or version_source.startswith("/")
            or ".." in Path(version_source).parts
        ):
            raise ValueError(f"project-map {name}.versionSource is invalid")
        if "release" in project and not isinstance(project["release"], bool):
            raise ValueError(f"project-map {name}.release must be true or false")
        if project.get("release", True):
            if not version_source:
                raise ValueError(f"project-map {name}.versionSource is required when release=true")
            source_path = ROOT / version_source
            if not source_path.exists():
                raise ValueError(f"project-map {name}.versionSource is missing: {version_source}")
            if source_path.name in {"package.json", "version.json"}:
                version_data = json.loads(source_path.read_text(encoding="utf-8"))
                version = version_data.get("version") if isinstance(version_data, dict) else None
            else:
                version = source_path.read_text(encoding="utf-8").strip()
            if not isinstance(version, str) or not SEMVER.fullmatch(version):
                raise ValueError(f"project-map {name}.versionSource must contain a semver version")


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
        check_project_map()
    except Exception as exc:
        return fail(str(exc))
    token_report()
    print("pogo-policy: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
