#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
import lib

SRC_EXT = {".java", ".kt", ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs"}
SKIP = {".git", ".codex", ".codex-state", ".worktrees", "node_modules", "build", "dist"}


def root() -> Path:
    return lib.root_dir()


def git(args: list[str], check: bool = False) -> str:
    if not lib.has_cmd("git"):
        return ""
    proc = lib.run(["git", *args], cwd=root(), check=False)
    if check and proc.returncode:
        raise SystemExit(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout.strip()


def current() -> dict:
    path = lib.find_codex() / "state" / "current_workflow.json"
    return lib.read_json(path, {})


def jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x]


def commit_files(task_id: str) -> list[str]:
    cur = current()
    rows = jsonl(Path(cur.get("path", "")) / "commits.jsonl") if cur else []
    commits = [x.get("commit", "") for x in rows if x.get("task_id") == task_id]
    files: list[str] = []
    for commit in commits:
        out = git(["show", "--name-only", "--format=", commit])
        files += [x for x in out.splitlines() if x.strip()]
    return files


def diff_files(base: str) -> list[str]:
    cur = current()
    base = base or cur.get("base_branch", "HEAD~1") or "HEAD~1"
    out = git(["diff", "--name-only", f"{base}..HEAD"])
    if not out:
        out = git(["diff", "--name-only", "HEAD"])
    return [x for x in out.splitlines() if x.strip()]


def usable(path: str) -> bool:
    p = Path(path)
    return p.suffix in SRC_EXT and not any(part in SKIP for part in p.parts)


def read(path: str) -> list[str]:
    full = root() / path
    try:
        return full.read_text(encoding="utf-8", errors="ignore").splitlines()
    except FileNotFoundError:
        return []


def repeat_score(lines: list[str]) -> int:
    seen: dict[str, int] = {}
    for line in lines:
        s = re.sub(r"\s+", " ", line.strip())
        if len(s) < 24 or s.startswith(("//", "#", "*", "import ")):
            continue
        seen[s] = seen.get(s, 0) + 1
    return sum(v - 2 for v in seen.values() if v > 2)


def file_metrics(files: list[str]) -> list[dict]:
    rows = []
    for item in sorted(set(x for x in files if usable(x))):
        lines = read(item)
        if not lines:
            continue
        todos = sum(1 for x in lines if "TODO" in x or "FIXME" in x)
        rows.append({"path": item, "lines": len(lines),
                     "repeat_score": repeat_score(lines), "todos": todos})
    return rows


def decide(rows: list[dict], args) -> dict:
    large = [x for x in rows if x["lines"] > args.max_lines]
    repeats = sum(x["repeat_score"] for x in rows)
    todos = sum(x["todos"] for x in rows)
    reasons = []
    if args.test_status == "fail":
        return {"decision": "defer", "reasons": ["tests are failing"]}
    if large:
        reasons.append("source file line limit exceeded")
    if repeats >= args.repeat_limit:
        reasons.append("duplicate-like code detected")
    if len(rows) >= args.file_limit:
        reasons.append("many source files changed")
    if todos:
        reasons.append("todo or fixme left in source")
    decision = "skip"
    if large or repeats >= args.repeat_limit:
        decision = "required"
    elif reasons:
        decision = "recommend"
    return {"decision": decision, "reasons": reasons}


def analyze(args) -> dict:
    files = commit_files(args.task) if args.task else diff_files(args.base)
    rows = file_metrics(files)
    result = decide(rows, args)
    result.update({"source_files": len(rows), "files": rows[:20]})
    if args.for_ai:
        result["files"] = [{"path": x["path"], "lines": x["lines"]} for x in rows[:8]]
    return result


def cmd_analyze(args) -> int:
    print(json.dumps(analyze(args), ensure_ascii=False, indent=2))
    return 0


def cmd_gate(args) -> int:
    data = analyze(args)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    fail = data["decision"] == "required" or (args.strict and data["decision"] == "recommend")
    return 2 if fail else 0


def cmd_add_task(args) -> int:
    data = analyze(args)
    if data["decision"] == "skip":
        print("refactor not needed")
        return 0
    title = args.title or ("리팩토링 정리" if lib.language() == "ko" else "Refactor cleanup")
    script = lib.find_codex() / "script" / "codex_state.py"
    proc = lib.run([sys.executable, str(script), "add", title,
                    "--agent", "refactor",
                    "--skills", "refactor-clean-code,test-generation"], cwd=root())
    print(proc.stdout.strip())
    return proc.returncode


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ["analyze", "gate", "add-task"]:
        s = sub.add_parser(name)
        s.add_argument("--task")
        s.add_argument("--base", default="")
        s.add_argument("--test-status", choices=["pass", "fail", "unknown"], default="unknown")
        s.add_argument("--max-lines", type=int, default=200)
        s.add_argument("--file-limit", type=int, default=12)
        s.add_argument("--repeat-limit", type=int, default=6)
        s.add_argument("--for-ai", action="store_true")
        if name == "gate":
            s.add_argument("--strict", action="store_true")
        if name == "add-task":
            s.add_argument("--title")
    return p


def main() -> int:
    args = parser().parse_args()
    return {"analyze": cmd_analyze, "gate": cmd_gate,
            "add-task": cmd_add_task}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
