#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import lib
import codex_trace_view

def version_path() -> Path:
    return lib.find_codex() / "state" / "VERSION.json"

def current_path() -> Path:
    return lib.find_codex() / "state" / "current_workflow.json"

def load_version() -> dict:
    return lib.read_json(version_path(), {"project_version": "0.1.0", "run_version": 0})

def bump(ver: str, kind: str) -> str:
    major, minor, patch = [int(x) for x in ver.split(".")]
    if kind == "major":
        return f"{major + 1}.0.0"
    if kind == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"

def wf_dir(run: int, title: str) -> Path:
    date = lib.today()
    return lib.root_dir() / ".codex-state" / date / f"v{run}-{lib.safe_slug(title)}"

def current() -> dict:
    return lib.read_json(current_path(), {})

def save_current(data: dict) -> None:
    lib.write_json(current_path(), data)
    lib.write_json(Path(data["path"]) / "state.json", data)

def events(cur: dict, event: str, extra: dict | None = None) -> None:
    row = {"time": lib.now(), "event": event, **(extra or {})}
    path = Path(cur["path"]) / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x]

def task_path(cur: dict) -> Path:
    return Path(cur["path"]) / "tasks.jsonl"

def commits_path(cur: dict) -> Path:
    return Path(cur["path"]) / "commits.jsonl"

def read_tasks(cur: dict) -> list[dict]:
    return jsonl(task_path(cur))

def read_commits(cur: dict) -> list[dict]:
    return jsonl(commits_path(cur))

def write_tasks(cur: dict, tasks: list[dict]) -> None:
    text = "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in tasks)
    task_path(cur).write_text(text, encoding="utf-8")
    codex_trace_view.render(cur, tasks)

def cmd_init(args) -> int:
    ver = load_version(); run = int(ver.get("run_version", 0)) + 1
    title = args.title or args.branch
    cur = {"workflow": args.workflow, "title": title, "branch": args.branch,
           "base_branch": args.base_branch, "bump": args.bump,
           "run_version": run, "project_version": ver.get("project_version", "0.1.0"),
           "next_version": bump(ver.get("project_version", "0.1.0"), args.bump),
           "phase": "plan", "path": str(wf_dir(run, title)), "created_at": lib.now(),
           "agent_pool_generation": run if args.workflow == "maw" else 0}
    Path(cur["path"]).mkdir(parents=True, exist_ok=True)
    save_current(cur); ver["run_version"] = run; lib.write_json(version_path(), ver)
    write_tasks(cur, []); events(cur, "init", {"title": title}); print(cur["path"])
    return 0

def cmd_add(args) -> int:
    cur = current(); tasks = read_tasks(cur); tid = args.id or f"T{len(tasks)+1:03d}"
    skills = [x for x in args.skills.split(",") if x]
    item = {"id": tid, "title": args.title, "agent": args.agent,
            "skills": skills, "status": "todo", "commit": "", "commits": []}
    tasks.append(item); write_tasks(cur, tasks)
    events(cur, "task_add", {"id": tid}); print(tid); return 0

def add_commit(item: dict, commit: str) -> None:
    commits = item.setdefault("commits", [])
    if commit and commit not in commits:
        commits.append(commit)
    if commit:
        item["commit"] = commit[:12]

def update(tid: str, status: str, commit: str = "") -> int:
    cur = current(); tasks = read_tasks(cur)
    for item in tasks:
        if item["id"] == tid:
            item["status"] = status; add_commit(item, commit)
            write_tasks(cur, tasks)
            extra = {"id": tid, "commit": commit[:12]} if commit else {"id": tid}
            events(cur, "task_" + status, extra); print(f"{tid}={status}"); return 0
    raise SystemExit("task not found")


def brief_task(item: dict) -> dict:
    return {"id": item.get("id"), "title": item.get("title"),
            "agent": item.get("agent"), "stage": item.get("stage"),
            "feature": item.get("feature"), "wave": item.get("wave"),
            "status": item.get("status"),
            "purpose": codex_trace_view.value_text(item.get("purpose") or
                                                     codex_trace_view.fallback_purpose(item)),
            "acceptance": codex_trace_view.value_text(item.get("acceptance") or
                                                        codex_trace_view.fallback_acceptance(item)),
            "commits": len(item.get("commits", []))}

def cmd_phase(args) -> int:
    cur = current()
    if args.set:
        cur["phase"] = args.set; save_current(cur); events(cur, "phase", {"phase": args.set})
    print(cur.get("phase", "unknown")); return 0

def cmd_summary(args) -> int:
    cur = current()
    if not cur or "path" not in cur:
        raise SystemExit("workflow not initialized")
    tasks = read_tasks(cur); commits = codex_trace_view.commits(cur)
    lanes = codex_trace_view.lanes(cur); cm = codex_trace_view.by_task(commits)
    done = sum(1 for x in tasks if x.get("status") == "done")
    if args.for_ai:
        pending = [x for x in tasks if x.get("status") != "done"]
        nxt = [brief_task(x) for x in pending[:3]]
        data = {"path": cur.get("path"), "phase": cur.get("phase"),
                "workflow": cur.get("workflow"), "title": cur.get("title"),
                "request_summary": cur.get("request_summary", ""),
                "planning_source": cur.get("planning_source", ""),
                "progress": f"{done}/{len(tasks)}", "next": nxt,
                "next_shown": len(nxt), "next_total": len(pending),
                "next_hidden": max(0, len(pending) - len(nxt)),
                "lanes": len(lanes), "commits": len(commits)}
    else:
        data = {"workflow": cur, "tasks": tasks, "commits": commits,
                "lanes": lanes, "commit_map": cm}
    print(json.dumps(data, ensure_ascii=False, indent=2)); return 0

def ready() -> int:
    cur = current()
    if not cur or "path" not in cur:
        raise SystemExit("workflow not initialized")
    missing = []
    cm = codex_trace_view.by_task(codex_trace_view.commits(cur))
    lm = codex_trace_view.by_task(codex_trace_view.lanes(cur))
    for x in read_tasks(cur):
        lanes = lm.get(x["id"], [])
        lane_ok = all(y.get("status") in {"done", "merged"} for y in lanes)
        if x.get("status") != "done" or not cm.get(x["id"]) or not lane_ok:
            missing.append(x["id"])
    print("ready" if not missing else "not ready: " + ",".join(missing))
    return 0 if not missing else 2

def approve() -> int:
    cur = current()
    if not cur or "next_version" not in cur:
        raise SystemExit("workflow not initialized")
    ver = load_version(); ver["project_version"] = cur["next_version"]
    ver["approved_at"] = lib.now(); lib.write_json(version_path(), ver)
    print(ver["project_version"]); return 0

def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init"); i.add_argument("--workflow", choices=["maw","saw"], required=True)
    i.add_argument("--title", required=True); i.add_argument("--branch", required=True)
    i.add_argument("--base-branch", default="main")
    i.add_argument("--bump", choices=["major","minor","patch"], default="patch")
    a = sub.add_parser("add"); a.add_argument("title"); a.add_argument("--agent", required=True)
    a.add_argument("--skills", default=""); a.add_argument("--id")
    s = sub.add_parser("start"); s.add_argument("id")
    d = sub.add_parser("done"); d.add_argument("id"); d.add_argument("--commit", default="")
    ph = sub.add_parser("phase"); ph.add_argument("--set", choices=["plan","implement","test","refactor","qa","security","review","done"])
    sm = sub.add_parser("summary"); sm.add_argument("--for-ai", action="store_true")
    sub.add_parser("ready"); sub.add_parser("approve-version"); args = p.parse_args()
    if args.cmd == "init": return cmd_init(args)
    if args.cmd == "add": return cmd_add(args)
    if args.cmd == "start": return update(args.id, "doing")
    if args.cmd == "done": return update(args.id, "done", args.commit)
    if args.cmd == "phase": return cmd_phase(args)
    if args.cmd == "summary": return cmd_summary(args)
    if args.cmd == "ready": return ready()
    return approve()

if __name__ == "__main__":
    raise SystemExit(main())
