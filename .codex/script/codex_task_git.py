#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys
from pathlib import Path
import lib, codex_state, codex_trace_view

def cur() -> dict:
    data = codex_state.current()
    if not data: raise SystemExit("workflow not initialized")
    return data

def commits_path(c: dict) -> Path: return Path(c["path"]) / "commits.jsonl"

def append_commit(c: dict, row: dict) -> None:
    rows = codex_trace_view.commits(c); key = (row.get("task_id"), row.get("lane_id"), row.get("commit"))
    if any((r.get("task_id"), r.get("lane_id"), r.get("commit")) == key for r in rows): return
    with commits_path(c).open("a", encoding="utf-8") as f: f.write(json.dumps(row, ensure_ascii=False)+"\n")

def git(args: list[str], cwd: Path | None = None, check: bool = True) -> str:
    p = lib.run(["git", *args], cwd=cwd or lib.root_dir(), check=False)
    if check and p.returncode: raise SystemExit(p.stderr.strip() or p.stdout.strip())
    return p.stdout.strip()

def short(commit: str) -> str: return git(["rev-parse", "--short", commit])
def changed_files(commit: str) -> list[str]:
    return [x for x in git(["show", "--name-status", "--format=", commit]).splitlines() if x.strip()]

def find_task(tasks: list[dict], tid: str) -> dict:
    for item in tasks:
        if item["id"] == tid: return item
    raise SystemExit("task not found")

def lane_file(c: dict) -> Path: return Path(c["path"]) / "lanes.jsonl"
def write_lanes(c: dict, rows: list[dict]) -> None:
    lane_file(c).write_text("".join(json.dumps(x, ensure_ascii=False)+"\n" for x in rows), encoding="utf-8")

def get_lane(c: dict, lane_id: str) -> dict | None:
    for row in codex_trace_view.lanes(c):
        if row.get("id") == lane_id: return row
    return None

def update_lane(c: dict, lane_id: str, commit: str) -> None:
    rows = codex_trace_view.lanes(c)
    for row in rows:
        if row.get("id") == lane_id:
            row["status"] = "done"; row["commit"] = short(commit)
            items = row.setdefault("commits", [])
            if commit not in items: items.append(commit)
    write_lanes(c, rows)

def task_lane_done(c: dict, tid: str) -> bool:
    rows = [x for x in codex_trace_view.lanes(c) if x.get("task_id") == tid]
    return bool(rows) and all(x.get("status") in {"done", "merged"} for x in rows)

def link_task(tid: str, commit: str, lane_id: str = "", done: bool = True) -> dict:
    c = cur(); tasks = codex_state.read_tasks(c); task = find_task(tasks, tid); commit = git(["rev-parse", commit])
    commits = task.setdefault("commits", [])
    if commit not in commits: commits.append(commit)
    task["commit"] = short(commit)
    if lane_id: update_lane(c, lane_id, commit)
    if done and (not lane_id or task_lane_done(c, tid)): task["status"] = "done"
    lane = get_lane(c, lane_id) if lane_id else {}
    row = {"time": lib.now(), "task_id": tid, "lane_id": lane_id,
           "wave": lane.get("wave") or task.get("wave", ""), "commit": commit,
           "short": short(commit), "files": changed_files(commit),
           "agent": task.get("agent", ""), "skills": task.get("skills", [])}
    append_commit(c, row); codex_state.write_tasks(c, tasks)
    codex_state.events(c, "commit_link", {"id": tid, "commit": row["short"], "lane_id": lane_id})
    return row

def clean_generated(cwd: Path) -> None:
    for name in ["__pycache__", ".pytest_cache"]:
        for path in cwd.rglob(name):
            if path.is_dir(): shutil.rmtree(path, ignore_errors=True)

def stage_all(cwd: Path) -> None:
    clean_generated(cwd); git(["add", "-A"], cwd=cwd)
    skip = [".codex", ".agents", ".codex-state", "node_modules",
            "dist", "build", ".next"]
    git(["reset", "--", *skip], cwd=cwd, check=False)

def verify_gate(cwd: Path, mode: str, allow_no_test: bool = False) -> None:
    script = lib.find_codex() / "script" / "codex_verify.py"
    cmd = [sys.executable, str(script), "gate", "--staged", "--cwd", str(cwd),
           "--mode", mode]
    if allow_no_test:
        cmd.append("--allow-no-test")
    p = subprocess.run(cmd, cwd=str(lib.root_dir()), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise SystemExit((p.stdout or p.stderr).strip())

def process_events(c, tid, lane_id):
    if c.get("workflow") != "maw" or not lane_id: return {}
    script = lib.find_codex() / "script" / "codex_event_bus.py"
    cmd = [sys.executable, str(script), "process", "--task", tid, "--lane", lane_id, "--for-ai"]
    p = subprocess.run(cmd, cwd=str(lib.root_dir()), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try: return json.loads((p.stdout or "{}").strip())
    except Exception: return {"event_output": (p.stdout or p.stderr).strip()}
CONVENTIONAL_RE = re.compile(r"^[a-z]+(?:\([^)]+\))?!?: .+")


def compact(value, limit: int = 180) -> str:
    if isinstance(value, list):
        value = "; ".join(str(x) for x in value if x)
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "..."


def commit_type(task: dict, lane: dict | None = None) -> str:
    row = lane or task
    stage = row.get("stage") or task.get("stage", "")
    agent = row.get("agent") or task.get("agent", "")
    if stage == "test" or agent in {"test", "test_writer", "test_runner"}:
        return "test"
    if stage == "refactor" or agent == "refactor":
        return "refactor"
    if stage == "security" or agent == "security":
        return "fix"
    if agent == "docs":
        return "docs"
    if agent == "devops":
        return "ci"
    if stage in {"implement", "foundation"}:
        return "feat"
    return "chore"


def commit_subject(message: str, task: dict, lane: dict | None = None) -> str:
    title = compact(message or task.get("title") or "update task", 72)
    if CONVENTIONAL_RE.match(title):
        return title
    return f"{commit_type(task, lane)}: {title}"


def commit_body(task: dict, c: dict, lane: dict | None, mode: str, lang: str) -> str:
    purpose = compact(task.get("purpose") or codex_trace_view.fallback_purpose(task))
    acceptance = compact(task.get("acceptance") or codex_trace_view.fallback_acceptance(task))
    lane_id = lane.get("id") if lane else "-"
    if lang == "ko":
        lines = [
            f"목적: {purpose}",
            f"범위: TASK {task.get('id')} / lane {lane_id} / workflow {c.get('workflow')}",
            f"완료 기준: {acceptance}",
            f"검증: codex_verify gate --staged --mode {mode}",
        ]
    else:
        lines = [
            f"Purpose: {purpose}",
            f"Scope: TASK {task.get('id')} / lane {lane_id} / workflow {c.get('workflow')}",
            f"Acceptance: {acceptance}",
            f"Verification: codex_verify gate --staged --mode {mode}",
        ]
    return "\n".join(lines)


def commit_footer(args, task: dict, c: dict, mode: str, lang: str) -> str:
    lines = [f"Codex-Task: {args.id}", f"Codex-Workflow: {Path(c['path']).name}"]
    if args.lane:
        lines.append(f"Codex-Lane: {args.lane}")
    if task.get("agent"):
        lines.append(f"Codex-Agent: {task['agent']}")
    if task.get("skills"):
        lines.append("Codex-Skills: " + ",".join(task["skills"]))
    lines.append(f"Codex-Verification: codex_verify gate --staged --mode {mode}")
    lines.append(f"Codex-Language: {lang}")
    return "\n".join(lines)


def commit_message_parts(args, task: dict, c: dict, lane: dict | None,
                         mode: str) -> tuple[str, str, str]:
    lang = lib.language()
    subject = commit_subject(args.message or task.get("title", ""), task, lane)
    body = commit_body(task, c, lane, mode, lang)
    footer = commit_footer(args, task, c, mode, lang)
    return subject, body, footer


def commit_cwd(args, cwd: Path, task: dict, c: dict) -> str:
    stage_all(cwd)
    mode = "saw" if c.get("workflow") == "saw" else "maw"
    verify_gate(cwd, mode, args.allow_no_test)
    lane = get_lane(c, args.lane) if args.lane else None
    subject, body, footer = commit_message_parts(args, task, c, lane, mode)
    cmd = ["commit"]
    if getattr(args, "allow_empty", False):
        cmd.append("--allow-empty")
    cmd += ["-m", subject, "-m", body, "-m", footer]
    git(cmd, cwd=cwd)
    return git(["rev-parse", "HEAD"], cwd=cwd)

def maybe_enqueue(c: dict, lane_id: str, row: dict, no_events: bool = False) -> None:
    if no_events or c.get("workflow") != "maw" or not lane_id:
        return
    try:
        import codex_event_bus
        src = next((x for x in codex_event_bus.lanes(c) if x.get("id") == lane_id), None)
        made = codex_event_bus.after(c, src) if src else []
        if made:
            row["enqueued"] = [{"lane": x["id"], "agent": x["agent"],
                                  "stage": x.get("stage")} for x in made]
            codex_state.write_tasks(c, codex_state.read_tasks(c))
    except Exception as exc:
        row["enqueue_warning"] = str(exc)


def cmd_commit(args) -> int:
    c = cur(); tasks = codex_state.read_tasks(c); task = find_task(tasks, args.id)
    lane = get_lane(c, args.lane) if args.lane else None; cwd = Path(lane["worktree"]) if lane else lib.root_dir()
    row = link_task(args.id, commit_cwd(args, cwd, task, c), args.lane, not args.no_done)
    maybe_enqueue(c, args.lane, row, args.no_events)
    print(json.dumps(row, ensure_ascii=False, indent=2)); return 0

def cmd_link(args) -> int:
    c = cur(); row = link_task(args.id, args.commit, args.lane, not args.no_done)
    maybe_enqueue(c, args.lane, row, args.no_events)
    print(json.dumps(row, ensure_ascii=False, indent=2)); return 0

def task_commits(tid: str) -> list[dict]:
    c = cur(); rows = [r for r in codex_trace_view.commits(c) if r.get("task_id") == tid]
    if rows: return rows
    task = find_task(codex_state.read_tasks(c), tid)
    return [{"commit": x, "short": short(x), "files": changed_files(x)} for x in task.get("commits", [])]

def cmd_files(args) -> int:
    print(json.dumps({"task_id": args.id, "commits": task_commits(args.id)}, ensure_ascii=False, indent=2)); return 0

def cmd_diff(args) -> int:
    commits = [r["commit"] for r in task_commits(args.id)]
    if not commits: raise SystemExit("no commits linked")
    if args.name_status:
        for commit in commits: print(f"# {short(commit)}\n" + git(["show", "--name-status", "--format=", commit]))
        return 0
    print(git(["diff", args.base or f"{commits[0]}^", commits[-1]])); return 0

def cmd_revert(args) -> int:
    commits = [r["commit"] for r in task_commits(args.id)]
    if not commits: raise SystemExit("no commits linked")
    for commit in reversed(commits): git(["revert", "--no-edit", commit])
    print("reverted " + args.id); return 0

def state_commit_parts(args, c: dict) -> tuple[str, str, str]:
    lang = lib.language()
    if lang == "ko":
        default_subject = "chore(codex-state): TASK trace 상태 갱신"
        body = "목적: TASK, lane, commit 원본 상태를 최신 실행 결과와 동기화합니다."
    else:
        default_subject = "chore(codex-state): update TASK trace"
        body = "Purpose: synchronize TASK, lane, and commit state with current execution."
    subject = args.message or default_subject
    if not CONVENTIONAL_RE.match(subject):
        subject = f"chore(codex-state): {subject}"
    footer = "\n".join([f"Codex-Workflow: {Path(c['path']).name}",
                        f"Codex-Language: {lang}"])
    return subject, body, footer


def cmd_state_commit(args) -> int:
    c = cur(); path = Path(c["path"]).relative_to(lib.root_dir())
    if not git(["status", "--porcelain", "--", str(path)], check=False): print("state clean"); return 0
    git(["add", "-A", "--", str(path)])
    subject, body, footer = state_commit_parts(args, c)
    git(["commit", "-m", subject, "-m", body, "-m", footer])
    print(git(["rev-parse", "--short", "HEAD"])); return 0

def cmd_scan(args) -> int:
    out = git(["log", "--format=%H%x09%s%x09%(trailers:key=Codex-Task,valueonly)", "--all"], check=False); rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and parts[2].strip(): rows.append({"commit": parts[0], "subject": parts[1], "task_id": parts[2].strip()})
    print(json.dumps(rows, ensure_ascii=False, indent=2)); return 0

def cmd_trace(args) -> int:
    c = cur(); rows = codex_trace_view.commits(c); lanes = codex_trace_view.lanes(c); data = []; agents = {}
    for task in codex_state.read_tasks(c):
        linked = [r for r in rows if r.get("task_id") == task["id"]]; tl = [x for x in lanes if x.get("task_id") == task["id"]]
        agent = task.get("agent"); ar = agents.setdefault(agent, {"tasks": 0, "done": 0}); ar["tasks"] += 1; ar["done"] += 1 if task.get("status") == "done" else 0
        item = {"id": task["id"], "status": task.get("status"), "agent": agent, "commits": [r.get("short") for r in linked], "lanes": f"{sum(x.get('status') in {'done','merged'} for x in tl)}/{len(tl)}"}
        if not args.for_ai: item.update({"lane_rows": tl, "files": sorted({f for r in linked for f in r.get("files", [])})})
        data.append(item)
    print(json.dumps({"agents": agents, "tasks": data} if args.for_ai else data, ensure_ascii=False, indent=2)); return 0

def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    cm = sub.add_parser("commit"); cm.add_argument("id"); cm.add_argument("--message"); cm.add_argument("--lane", default=""); cm.add_argument("--no-done", action="store_true"); cm.add_argument("--allow-no-test", action="store_true"); cm.add_argument("--allow-empty", action="store_true"); cm.add_argument("--no-events", action="store_true")
    ln = sub.add_parser("link"); ln.add_argument("id"); ln.add_argument("commit"); ln.add_argument("--lane", default=""); ln.add_argument("--no-done", action="store_true"); ln.add_argument("--no-events", action="store_true")
    fl = sub.add_parser("files"); fl.add_argument("id")
    df = sub.add_parser("diff"); df.add_argument("id"); df.add_argument("--base"); df.add_argument("--name-status", action="store_true")
    rv = sub.add_parser("revert-task"); rv.add_argument("id"); sub.add_parser("scan-log")
    st = sub.add_parser("state-commit"); st.add_argument("--message")
    tr = sub.add_parser("trace"); tr.add_argument("--for-ai", action="store_true")
    args = p.parse_args(); return {"commit": cmd_commit, "link": cmd_link, "files": cmd_files, "diff": cmd_diff, "revert-task": cmd_revert, "state-commit": cmd_state_commit, "scan-log": cmd_scan, "trace": cmd_trace}[args.cmd](args)

if __name__ == "__main__": raise SystemExit(main())
