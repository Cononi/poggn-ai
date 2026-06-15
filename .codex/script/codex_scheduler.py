#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import lib, codex_agent_pool, codex_event_bus, codex_lanes, codex_pipeline, codex_state


def cur() -> dict:
    c = codex_state.current()
    if not c: raise SystemExit("workflow not initialized")
    return c


def rows() -> list[dict]: return codex_lanes.read_jsonl(codex_lanes.lane_path(cur()))
def ready() -> list[dict]: return codex_pipeline.ready_rows(rows())


def cmd_ready(args) -> int:
    out = [{"lane_id": r["id"], "task_id": r["task_id"], "agent": r["agent"],
            "stage": r.get("stage"), "feature": r.get("feature"),
            "worker_name": r.get("worker_name"), "reuse_key": r.get("reuse_key"),
            "title": r["title"]} for r in ready()]
    print(json.dumps(out, ensure_ascii=False, indent=2)); return 0


def cmd_csv(args) -> int:
    c = cur(); out = Path(c["path"]) / "agent_jobs_ready.csv"
    fields = ["job_name", "worker_name", "reuse_key", "agent", "lane_id",
              "task_id", "stage", "feature", "instruction"]
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r in ready():
            name = r.get("worker_name") or f"{r['agent']}-{r.get('feature','work')}"
            cmd = f"cd {lib.root_dir()} && python3 .codex/script/codex_task_git.py commit {r['task_id']} --lane {r['id']} --message \"{r['title']}\" --allow-empty"
            inst = f"Use worker {name}. Agent={r['agent']}. Worktree={r['worktree']}. Finish: {cmd}"
            w.writerow({"job_name": f"{name}-{r['id']}", "worker_name": name,
                        "reuse_key": r.get("reuse_key", name), "agent": r["agent"],
                        "lane_id": r["id"], "task_id": r["task_id"],
                        "stage": r.get("stage"), "feature": r.get("feature"),
                        "instruction": inst})
    print(out); return 0


def cmd_prompt(args) -> int:
    print("Use $codex-scheduler csv --ready.")
    print("Spawn one subagent per CSV row and use worker_name as label.")
    print("Reuse only when reuse_key matches and context is still clean.")
    print("Close completed threads before a new $maw run."); return 0


def cmd_workers(args) -> int: return codex_agent_pool.cmd_status(args)
def cmd_policy(args) -> int: return codex_event_bus.cmd_policy(args)


def cmd_enqueue(args) -> int:
    args.lane = args.from_lane
    return codex_event_bus.cmd_process(args)


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ready").add_argument("--for-ai", action="store_true")
    sub.add_parser("csv").add_argument("--ready", action="store_true")
    sub.add_parser("prompt"); sub.add_parser("workers").add_argument("--for-ai", action="store_true")
    sub.add_parser("policy")
    e = sub.add_parser("enqueue"); e.add_argument("--from-lane", required=True)
    e.add_argument("--force", default=""); e.add_argument("--for-ai", action="store_true")
    args = p.parse_args(); return globals()["cmd_" + args.cmd](args)


if __name__ == "__main__": raise SystemExit(main())
