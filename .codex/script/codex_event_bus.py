#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path
import lib, codex_agent_pool, codex_lanes, codex_skills, codex_state, codex_trace_view

SRC = {".java", ".kt", ".py", ".go", ".rs", ".ts", ".tsx", ".sql"}
SENSITIVE = "auth oauth jwt password token secret payment billing refund env security".split()
PUBLIC = "controller api rest openapi swagger component page screen route ui".split()
DONE = {"done", "merged"}
DEFAULT = {"dynamic_downstream": True, "producer_stages": ["foundation", "implement"],
           "producer_agents": [], "test_writer": "code_changed",
           "test_runner": "after_test_writer_or_code", "qa": "public_or_large",
           "refactor": "large_only", "security": "sensitive_only",
           "thread_reuse": "scoped_fresh", "custom_downstream": [], "trigger_stages": ["implement"]}
def policy() -> dict:
    p = lib.find_codex() / "state" / "event_policy.json"
    data = lib.read_json(p, DEFAULT); out = dict(DEFAULT); out.update(data); return out
def current() -> dict:
    c = codex_state.current()
    if not c: raise SystemExit("workflow not initialized")
    return c
def lanes(c: dict) -> list[dict]: return codex_lanes.read_jsonl(codex_lanes.lane_path(c))
def tasks(c: dict) -> list[dict]: return codex_state.read_tasks(c)
def commits(c: dict) -> list[dict]: return codex_trace_view.commits(c)
def task_done(c: dict, task_id: str) -> bool:
    return any(t.get("id") == task_id and t.get("status") == "done"
               for t in tasks(c))
def complete_event(c: dict, row: dict) -> bool:
    return row.get("status") in DONE and task_done(c, row.get("task_id", ""))
def file_name(raw: str) -> str:
    parts = raw.split("\t"); return parts[-1] if len(parts) > 1 else raw.split(maxsplit=1)[-1]
def lane_files(c: dict, lane: str) -> list[str]:
    out = []
    for row in commits(c):
        if row.get("lane_id") == lane: out += [file_name(x) for x in row.get("files", [])]
    return out
def root_lane(row: dict) -> str: return row.get("root_lane_id") or row.get("id", "")
def root_files(c: dict, row: dict) -> list[str]: return lane_files(c, root_lane(row)) or lane_files(c, row.get("id", ""))
def classify(files: list[str], title: str = "") -> dict:
    paths = [Path(x) for x in files]; lower = (" ".join(files) + " " + title).lower()
    code = [str(x) for x in paths if x.suffix in SRC]
    tests = [x for x in files if re.search(r"(^|/)(test|tests|spec|__tests__)(/|$)", x.lower())]
    return {"code": bool(code), "tests": bool(tests), "docs_only": bool(files) and not code,
            "sensitive": any(x in lower for x in SENSITIVE),
            "public": any(x in lower for x in PUBLIC),
            "large": len(code) >= 6 or len(files) >= 12, "files": files[:12]}
def exists(rows: list[dict], root: str, stage: str, feature: str) -> bool:
    for row in rows:
        same = row.get("root_lane_id") == root or row.get("upstream_lane_id") == root
        if same and row.get("stage") == stage and row.get("feature") == feature: return True
    return False
def next_id(rows: list[dict], prefix: str) -> str: return f"{prefix}{len(rows) + 1:03d}"
def create(c: dict, all_tasks: list[dict], all_lanes: list[dict], row: dict,
           stage: str, agent: str, title: str, deps: list[str]) -> dict | None:
    root = root_lane(row); feat = row.get("feature", "work")
    if exists(all_lanes, root, stage, feat): return None
    tid = next_id(all_tasks, "T"); lid = next_id(all_lanes, "L")
    agent_file = lib.find_codex() / "agents" / f"{agent}.toml"
    if not agent_file.exists():
        codex_state.events(c, "missing_agent", {"agent": agent})
        return None
    skills = codex_skills.recommend(title, agent)
    task = {"id": tid, "title": title, "agent": agent, "skills": skills,
            "status": "todo", "commit": "", "commits": [], "wave": row.get("wave", "W001"),
            "stage": stage, "feature": feat, "triggered_by": row.get("id"),
            "root_lane_id": root}
    all_tasks.append(task)
    lane = {"id": lid, "task_id": tid, "agent": agent, "skills": skills,
            "title": title, "wave": task["wave"], "stage": stage, "feature": feat,
            "status": "todo", "commit": "", "commits": [],
            "branch": codex_lanes.branch_name(c, lid),
            "worktree": str(codex_lanes.worktree_path(c, lid)), "deps": deps,
            "upstream_lane_id": row.get("id"), "root_lane_id": root}
    lane["worker_name"] = codex_agent_pool.label(lane); lane["reuse_key"] = codex_agent_pool.reuse_key(lane)
    all_lanes.append(lane); codex_lanes.write_jsonl(codex_lanes.lane_path(c), all_lanes)
    codex_state.events(c, "trigger_lane", {"id": lid, "agent": agent, "stage": stage,
        "upstream": row.get("id"), "root": root, "task_id": tid})
    return lane
def custom_match(rule: dict, row: dict, meta: dict) -> bool:
    if rule.get("after_stage") and rule.get("after_stage") != row.get("stage"):
        return False
    keys = [str(x).lower() for x in rule.get("keywords", []) if x]
    if not keys:
        return True
    hay = " ".join(meta.get("files", [])) + " " + row.get("title", "")
    hay += " " + row.get("feature", "")
    return any(k in hay.lower() for k in keys)
def add_custom(c: dict, row: dict, all_tasks: list[dict], all_lanes: list[dict],
               meta: dict) -> list[dict]:
    made = []
    for rule in policy().get("custom_downstream", []):
        if not custom_match(rule, row, meta):
            continue
        agent = rule.get("agent", "qa")
        stage = rule.get("stage", agent)
        label = rule.get("title", f"{agent}: {row.get('feature','work')}")
        item = create(c, all_tasks, all_lanes, row, stage, agent, label, [row["id"]])
        if item:
            made.append(item)
    return made
def custom_rules(pol: dict, stage: str, meta: dict, title: str) -> list[dict]:
    out = []
    lower = (title + " " + " ".join(meta.get("files", []))).lower()
    for rule in pol.get("custom_downstream", []):
        if rule.get("after_stage", "implement") != stage:
            continue
        keys = [x.lower() for x in rule.get("keywords", []) if x]
        if keys and not any(x in lower for x in keys):
            continue
        out.append(rule)
    return out


def is_producer(pol: dict, row: dict) -> bool:
    stages = set(pol.get("producer_stages", ["implement"]))
    agents = set(pol.get("producer_agents", []))
    return row.get("stage") in stages and (not agents or row.get("agent") in agents)

def should(pol: dict, name: str, meta: dict) -> bool:
    if pol.get(name) in {"off", False}: return False
    if name == "test_writer": return meta["code"] and not meta["tests"]
    if name == "test_runner": return meta["code"]
    if name == "qa": return meta["public"] or meta["large"]
    if name == "refactor": return meta["large"]
    if name == "security": return meta["sensitive"]
    return False
def title(row: dict, name: str) -> str:
    feat = str(row.get("feature") or row.get("title", "work")).replace("-", " ").title()
    return f"{name}: {feat}"
def after(c: dict, row: dict | None, force: set[str] | None = None) -> list[dict]:
    if not row: return []
    force = force or set(); pol = policy(); all_tasks = tasks(c); all_lanes = lanes(c); made = []
    stage = row.get("stage", "implement"); meta = classify(root_files(c, row), row.get("title", ""))
    def add(stg: str, agent: str, label: str, dep: str | None = None):
        made.append(create(c, all_tasks, all_lanes, row, stg, agent, title(row, label), [dep or row["id"]]))
    if is_producer(pol, row):
        if should(pol, "test_writer", meta) or "test_writer" in force: add("test_writer", "test_writer", "Test code")
        dep = made[-1]["id"] if made and made[-1] and made[-1]["stage"] == "test_writer" else row["id"]
        if should(pol, "test_runner", meta) or "test_runner" in force: add("test_runner", "test_runner", "Run tests", dep)
        if should(pol, "qa", meta) or "qa" in force: add("qa", "qa", "QA review")
        if should(pol, "refactor", meta) or "refactor" in force: add("refactor", "refactor", "Refactor check")
        if should(pol, "security", meta) or "security" in force: add("security", "security", "Security review")
        for rule in custom_rules(pol, stage, meta, row.get("title", "")):
            stg = rule.get("stage", rule.get("agent", "custom"))
            agent = rule.get("agent", stg)
            label = rule.get("title", f"{agent} review")
            add(stg, agent, label)
    elif stage == "test_writer":
        add("test_runner", "test_runner", "Run tests")
    elif stage in {"refactor", "security"} and meta["code"]:
        add("test_runner", "test_runner", "Retest")
    made += add_custom(c, row, all_tasks, all_lanes, meta)
    if any(made): codex_state.write_tasks(c, all_tasks)
    return [x for x in made if x]
def cmd_process(args) -> int:
    c = current(); made = []
    if c.get("workflow") != "maw" or not policy().get("dynamic_downstream", True):
        print(json.dumps({"created": []}, ensure_ascii=False)); return 0
    rows = lanes(c); force = set(args.force.split(",")) if getattr(args, "force", "") else set()
    for row in rows:
        if args.lane and row.get("id") != args.lane: continue
        if complete_event(c, row): made += after(c, row, force)
    print(json.dumps({"created": made}, ensure_ascii=False, indent=2)); return 0
def cmd_enqueue(args) -> int:
    args.lane = args.from_lane; return cmd_process(args)
def cmd_workers(args) -> int:
    data = [{"lane": r.get("id"), "task": r.get("task_id"), "worker": r.get("worker_name"),
             "reuse_key": r.get("reuse_key"), "agent": r.get("agent"), "stage": r.get("stage"),
             "feature": r.get("feature"), "status": r.get("status")} for r in lanes(current())]
    print(json.dumps(data, ensure_ascii=False, indent=2)); return 0
def cmd_clear(args) -> int:
    codex_state.events(current(), "worker_threads_clear", {"reason": args.reason or "new maw"})
    print("recorded clear event. Close completed /agent threads in Codex."); return 0
def cmd_policy(args) -> int: print(json.dumps(policy(), ensure_ascii=False, indent=2)); return 0
def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    pr = sub.add_parser("process"); pr.add_argument("--task", default=""); pr.add_argument("--lane", default=""); pr.add_argument("--force", default=""); pr.add_argument("--for-ai", action="store_true")
    en = sub.add_parser("enqueue"); en.add_argument("--from-lane", required=True); en.add_argument("--force", default=""); en.add_argument("--for-ai", action="store_true")
    sub.add_parser("workers").add_argument("--for-ai", action="store_true")
    sub.add_parser("policy"); cl = sub.add_parser("clear"); cl.add_argument("--reason", default="")
    args = p.parse_args(); return globals()["cmd_" + args.cmd](args)

if __name__ == "__main__": raise SystemExit(main())
