#!/usr/bin/env python3
from __future__ import annotations
import argparse, py_compile, re, subprocess, sys
from pathlib import Path
import lib

SKIP = {".git", ".codex-state", ".worktrees", "node_modules", "dist", "build",
        ".venv", "venv", "__pycache__"}


def walk(root: Path, suffixes: set[str]):
    for path in root.rglob("*"):
        if any(part in SKIP for part in path.parts): continue
        if path.is_file() and path.suffix.lower() in suffixes: yield path


def line_gate(root: Path) -> list[str]:
    bad = []
    for path in walk(root, {".md"}):
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if len(line) > 100: bad.append(f"{path.relative_to(root)}:{i}: line > 100")
    return bad


def py_gate(root: Path) -> list[str]:
    bad = []
    for path in walk(root, {".py"}):
        if len(path.read_text(encoding="utf-8").splitlines()) > 200:
            bad.append(f"{path.relative_to(root)}: python > 200 lines")
        try: py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc: bad.append(f"{path.relative_to(root)}: {exc.msg}")
    return bad



def agent_gate(root: Path) -> list[str]:
    script = root / ".codex" / "script" / "codex_agents.py"
    if not script.exists():
        return ["missing codex_agents.py"]
    p = subprocess.run([sys.executable, str(script), "check"], cwd=str(root),
                       text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode == 0:
        return []
    return [(p.stdout or p.stderr).strip() or "agent check failed"]

def language_gate(root: Path) -> list[str]:
    lang = lib.language(); bad = []
    for path in walk(root / ".codex", {".md"}):
        rel_parts = path.relative_to(root).parts
        if len(rel_parts) >= 4 and rel_parts[:3] == (".codex", "templates", "docs"):
            continue
        text = path.read_text(encoding="utf-8")
        hangul = len(re.findall(r"[가-힣]", text)); latin = len(re.findall(r"[A-Za-z]", text))
        rel = path.relative_to(root)
        if lang == "ko" and hangul < 20: bad.append(f"{rel}: Korean text is too low")
        if lang == "en" and hangul > 0: bad.append(f"{rel}: English document has Hangul")
        if lang == "en" and latin < 20: bad.append(f"{rel}: English text is too low")
    return bad


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("command", choices=["gate","lines","py","language"])
    args = p.parse_args(); root = lib.root_dir(); checks = []
    if args.command in {"gate", "lines"}: checks += line_gate(root)
    if args.command in {"gate", "py"}: checks += py_gate(root)
    if args.command in {"gate", "language"}: checks += language_gate(root)
    if args.command == "gate": checks += agent_gate(root)
    if checks: print("\n".join(checks)); return 2
    print("docs gate ok"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
