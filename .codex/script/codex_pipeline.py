#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import lib, codex_lanes, codex_state, codex_agent_pool, codex_trace_view

DONE = {"done", "merged"}
READY_AI_LIMIT = 4


def cur() -> dict:
    data = codex_state.current()
    if not data: raise SystemExit("workflow not initialized")
    return data


def lanes(c: dict) -> list[dict]: return codex_lanes.read_jsonl(codex_lanes.lane_path(c))


def dep_ok(row: dict, by_id: dict[str, dict]) -> bool:
    return all(by_id.get(x, {}).get("status") in DONE for x in row.get("deps", []))


def ready_rows(rows: list[dict], stage: str = "", wave: str = "") -> list[dict]:
    by_id = {x.get("id", ""): x for x in rows}; out = []
    for row in rows:
        if row.get("status") in DONE: continue
        if stage and row.get("stage") != stage: continue
        if wave and row.get("wave") != wave.upper(): continue
        if dep_ok(row, by_id): out.append(row)
    return out


def stats(rows: list[dict]) -> dict:
    stages: dict[str, dict] = {}; agents: dict[str, dict] = {}; features: dict[str, dict] = {}
    for row in rows:
        stage = row.get("stage", "implement"); agent = row.get("agent", "none")
        feat = row.get("feature", "work")
        s = stages.setdefault(stage, {"todo": 0, "done": 0})
        a = agents.setdefault(agent, {"todo": 0, "done": 0})
        f = features.setdefault(feat, {"todo": 0, "done": 0})
        key = "done" if row.get("status") in DONE else "todo"
        s[key] += 1; a[key] += 1; f[key] += 1
    return {"stages": stages, "agents": agents, "features": features, "total_lanes": len(rows)}


def compact(value, limit: int = 180) -> str:
    if isinstance(value, list):
        value = "; ".join(str(x) for x in value if x)
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


def ko() -> bool:
    return lib.language() == "ko"


def slim(row: dict) -> dict:
    purpose = row.get("purpose") or codex_trace_view.fallback_purpose(row)
    acceptance = row.get("acceptance") or codex_trace_view.fallback_acceptance(row)
    return {"id": row.get("id"), "task_id": row.get("task_id"),
            "agent": row.get("agent"), "stage": row.get("stage"),
            "feature": row.get("feature"), "wave": row.get("wave"),
            "title": compact(row.get("title"), 80), "purpose": compact(purpose, 100),
            "acceptance": compact(acceptance, 100),
            "owner_files": row.get("owner_files", [])[:4],
            "forbidden_files": row.get("forbidden_files", [])[:4],
            "verification": row.get("verification", [])[:3],
            "frontend_contract": row.get("frontend_contract", [])[:3],
            "deps": row.get("deps", [])}


def instruction(row: dict) -> str:
    root = lib.root_dir(); skills = ",".join(row.get("skills", []))
    cmd = f"cd {root} && python3 .codex/script/codex_task_git.py"
    cmd += f" commit {row['task_id']} --lane {row['id']}"
    cmd += f" --message \"{row['title']}\" --allow-empty"
    deps = ",".join(row.get("deps", [])) or ("없음" if ko() else "none")
    label = codex_agent_pool.label(row); key = codex_agent_pool.reuse_key(row)
    purpose = compact(row.get("purpose") or codex_trace_view.fallback_purpose(row), 160)
    acceptance = compact(row.get("acceptance") or codex_trace_view.fallback_acceptance(row), 160)
    owner = compact(row.get("owner_files", []), 180)
    forbidden = compact(row.get("forbidden_files", []), 180)
    verification = compact(row.get("verification", []), 160)
    done = compact(row.get("done_contract", []), 180)
    budget = compact(row.get("budget_note", ""), 140)
    frontend = compact(row.get("frontend_contract", []), 240)
    frontend_ko = f"frontend_contract={frontend} " if frontend else ""
    frontend_en = f"Frontend contract={frontend}. " if frontend else ""
    if ko():
        return (f"에이전트 {row['agent']}를 {label}로 사용하세요. 재사용 키={key}. "
                f"목적={purpose} 완료기준={acceptance} "
                f"owner_files={owner} forbidden_files={forbidden} "
                f"verification={verification} done_contract={done} budget={budget} "
                f"{frontend_ko}"
                f"단계={row.get('stage','implement')}. 작업 위치는 {row['worktree']}로 제한합니다. "
                f"상위 레인={deps}. 스킬={skills}. 루트에서 완료 명령: {cmd}")
    return (f"Use agent {row['agent']} as {label}. Reuse key={key}. "
            f"Purpose={purpose}. Acceptance={acceptance}. "
            f"Owner files={owner}. Forbidden files={forbidden}. "
            f"Verification={verification}. Done contract={done}. Budget={budget}. "
            f"{frontend_en}"
            f"Stage={row.get('stage','implement')}. Work only in {row['worktree']}. "
            f"Upstream lanes={deps}. Skills={skills}. Finish from root with: {cmd}")


def write_csv(c: dict, rows: list[dict], name: str) -> Path:
    out = Path(c["path"]) / name
    fields = ["job_name", "worker_name", "worker_label", "reuse_key", "wave",
              "lane_id", "task_id", "agent", "stage", "feature", "skills",
              "purpose", "acceptance", "non_goals",
              "owner_files", "forbidden_files", "verification", "done_contract",
              "frontend_contract", "budget_note", "worktree", "branch", "deps", "instruction"]
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for row in rows:
            wname = row.get("worker_name") or f"{row['agent']}-{row.get('feature','work')}"
            w.writerow({"job_name": f"{wname}-{row['id']}", "worker_name": wname,
                        "wave": row.get("wave", "W001"), "lane_id": row["id"],
                        "task_id": row["task_id"], "agent": row["agent"],
                        "stage": row.get("stage", "implement"),
                        "feature": row.get("feature", ""),
                        "purpose": compact(row.get("purpose")),
                        "acceptance": compact(row.get("acceptance")),
                        "non_goals": compact(row.get("non_goals")),
                        "owner_files": compact(row.get("owner_files")),
                        "forbidden_files": compact(row.get("forbidden_files")),
                        "verification": compact(row.get("verification")),
                        "done_contract": compact(row.get("done_contract")),
                        "frontend_contract": compact(row.get("frontend_contract")),
                        "budget_note": compact(row.get("budget_note")),
                        "worker_label": codex_agent_pool.label(row),
                        "reuse_key": codex_agent_pool.reuse_key(row),
                        "skills": ",".join(row.get("skills", [])),
                        "worktree": row["worktree"], "branch": row["branch"],
                        "deps": ",".join(row.get("deps", [])),
                        "instruction": instruction(row)})
    return out


def cmd_status(args) -> int:
    c = cur(); rows = lanes(c); data = stats(rows)
    ready = ready_rows(rows, args.stage, args.wave)
    if args.for_ai:
        shown = ready[:READY_AI_LIMIT]
        data["ready"] = [slim(x) for x in shown]
        data["ready_shown"] = len(shown)
        data["ready_total"] = len(ready)
        data["ready_hidden"] = max(0, len(ready) - len(shown))
    else:
        data["ready"] = [slim(x) for x in ready]
    print(json.dumps(data, ensure_ascii=False, indent=2)); return 0


def cmd_ready(args) -> int:
    rows = ready_rows(lanes(cur()), args.stage, args.wave)
    if args.for_ai:
        shown = rows[:READY_AI_LIMIT]
        data = {"ready": [slim(x) for x in shown],
                "ready_shown": len(shown), "ready_total": len(rows),
                "ready_hidden": max(0, len(rows) - len(shown)),
                "note": ("전체 spawn 표는 $codex-pipeline csv --ready를 사용하세요."
                         if ko() else "Use $codex-pipeline csv --ready for the full spawn table.")}
    else:
        data = rows
    print(json.dumps(data, ensure_ascii=False, indent=2)); return 0


def cmd_prepare(args) -> int:
    c = cur(); rows = ready_rows(lanes(c), args.stage, args.wave)
    if not rows: raise SystemExit("no ready lanes")
    by_id = {x.get("id", ""): x for x in lanes(c)}
    for row in rows:
        wt = Path(row["worktree"])
        if wt.exists():
            print("skip exists " + row["id"]); continue
        deps = row.get("deps", [])
        base = by_id.get(deps[-1], {}).get("branch", "HEAD") if deps else c.get("base_branch", "main")
        base = codex_lanes.resolve_base(base)
        wt.parent.mkdir(parents=True, exist_ok=True)
        codex_lanes.git(["worktree", "add", "-B", row["branch"], str(wt), base])
        print("prepared " + row["id"] + " " + row["branch"])
    return 0


def cmd_csv(args) -> int:
    c = cur(); rows = ready_rows(lanes(c), args.stage, args.wave) if args.ready else lanes(c)
    if not rows: raise SystemExit("no ready lanes")
    name = "agent_jobs_ready.csv" if args.ready else "agent_jobs_all.csv"
    print(write_csv(c, rows, name)); return 0


def cmd_prompt(args) -> int:
    c = cur(); rows = ready_rows(lanes(c), args.stage, args.wave)
    if not rows:
        print("준비된 레인이 없습니다." if ko() else "No ready lanes."); return 0
    path = write_csv(c, rows, "agent_jobs_ready.csv")
    if ko():
        print("worktree가 없으면 먼저 $codex-pipeline prepare를 실행하세요.")
        print("ready CSV의 각 행마다 subagent 1개를 실행하고 모든 결과를 기다리세요.")
        print("행 계약만 사용하고 전체 TASKS.md를 subagent prompt에 붙이지 마세요.")
        print("main은 orchestrator입니다. lane 완료 전 subagent 결과를 검토하세요.")
        print("변경 파일, 테스트, blocker, 보안 메모, acceptance criteria를 확인하세요.")
        print("검토 실패 시 구체적 지적과 함께 해당 lane을 다시 전달하세요.")
        print("worker_name이 같은 MAW run과 일치하면 활성 worker를 재사용하세요.")
        print(f"csv_path: {path}")
        print("id_column: lane_id")
        print("instruction: instruction 컬럼을 그대로 사용하세요.")
        print("workflow나 wave가 끝나면 완료된 worker를 닫으세요.")
        print("output_csv_path: " + str(Path(c["path"]) / "agent_jobs_result.csv"))
        print("batch 후 $codex-pipeline status --for-ai를 실행하세요.")
        return 0
    print("First run $codex-pipeline prepare if worktrees are missing.")
    print("Spawn one subagent per ready CSV row and wait for all results.")
    print("Use only the row contract; do not paste full TASKS.md into subagent prompts.")
    print("Main is the orchestrator: review subagent outputs before marking lanes done.")
    print("Check changed files, tests, blockers, security notes, and acceptance criteria.")
    print("If review fails, re-dispatch that lane with concrete findings.")
    print("Reuse an active worker when worker_name matches this MAW run.")
    print(f"csv_path: {path}")
    print("id_column: lane_id")
    print("instruction: use the instruction column exactly.")
    print("Close completed workers when the workflow or wave ends.")
    print("output_csv_path: " + str(Path(c["path"]) / "agent_jobs_result.csv"))
    print("After the batch, run $codex-pipeline status --for-ai")
    return 0


def cmd_mark(args) -> int:
    c = cur(); rows = lanes(c)
    for row in rows:
        if row.get("id") == args.lane:
            row["status"] = args.status
    codex_lanes.write_jsonl(codex_lanes.lane_path(c), rows)
    codex_state.write_tasks(c, codex_state.read_tasks(c))
    print(args.lane + "=" + args.status); return 0


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    for name in ["status", "ready"]:
        s = sub.add_parser(name); s.add_argument("--stage", default="")
        s.add_argument("--wave", default=""); s.add_argument("--for-ai", action="store_true")
    c = sub.add_parser("csv"); c.add_argument("--ready", action="store_true")
    c.add_argument("--stage", default=""); c.add_argument("--wave", default="")
    pr = sub.add_parser("prompt"); pr.add_argument("--stage", default="")
    pr.add_argument("--wave", default="")
    prep = sub.add_parser("prepare"); prep.add_argument("--stage", default="")
    prep.add_argument("--wave", default="")
    m = sub.add_parser("mark"); m.add_argument("lane"); m.add_argument("status")
    args = p.parse_args(); return globals()["cmd_" + args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
