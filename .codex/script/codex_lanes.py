#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import lib, codex_state


def current() -> dict:
    data = codex_state.current()
    if not data: raise SystemExit("workflow not initialized")
    return data


def lane_path(cur: dict) -> Path: return Path(cur["path"]) / "lanes.jsonl"


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists(): return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    text = "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows)
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding="utf-8")


def branch_name(cur: dict, lane: str) -> str:
    return f"{cur.get('branch', 'release/work')}-{lane.lower()}"


def worktree_path(cur: dict, lane: str) -> Path:
    return lib.root_dir() / ".worktrees" / Path(cur["path"]).name / lane.lower()


def ko() -> bool:
    return lib.language() == "ko"


def rerender(cur: dict) -> None: codex_state.write_tasks(cur, codex_state.read_tasks(cur))


def wave_value(value: str) -> str:
    if not value: return ""
    value = str(value).upper()
    return value if value.startswith("W") else f"W{int(value):03d}"


def selected(rows: list[dict], args) -> list[dict]:
    wave = wave_value(getattr(args, "wave", ""))
    return [r for r in rows if not wave or r.get("wave", "W001") == wave]


def cmd_add(args) -> int:
    cur = current(); rows = read_jsonl(lane_path(cur)); lid = args.id or f"L{len(rows)+1:03d}"
    wave = wave_value(args.wave) or "W001"
    row = {"id": lid, "task_id": args.task, "agent": args.agent,
           "skills": [x for x in args.skills.split(",") if x], "title": args.title,
           "wave": wave, "status": "todo", "commit": "", "commits": [],
           "branch": branch_name(cur, lid), "worktree": str(worktree_path(cur, lid)),
           "deps": [x for x in args.deps.split(",") if x]}
    rows.append(row); write_jsonl(lane_path(cur), rows); rerender(cur)
    print(lid); return 0


def cmd_list(args) -> int:
    rows = selected(read_jsonl(lane_path(current())), args)
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2)); return 0
    for row in rows:
        skills = ",".join(row.get("skills", [])); deps = ",".join(row.get("deps", [])) or "-"
        print(f"{row['id']} {row.get('wave','W001')} {row['agent']} {row['status']} {row['title']}")
        print(f"  task={row['task_id']} skills={skills} deps={deps}")
        print(f"  branch={row['branch']} commit={row.get('commit','')}")
    return 0


def git(args: list[str], cwd: Path | None = None, check: bool = True):
    proc = lib.run(["git", *args], cwd=cwd or lib.root_dir())
    if check and proc.returncode: raise SystemExit(proc.stderr.strip() or proc.stdout.strip())
    return proc


def resolve_base(name: str) -> str:
    proc = git(["rev-parse", "--verify", name], check=False)
    return name if proc.returncode == 0 else "HEAD"


def cmd_prepare(args) -> int:
    cur = current(); rows = selected(read_jsonl(lane_path(cur)), args)
    base = resolve_base(args.base or cur.get("base_branch", "main"))
    for row in rows:
        wt = Path(row["worktree"]); branch = row["branch"]
        if wt.exists(): print(f"skip exists {row['id']} {wt}"); continue
        wt.parent.mkdir(parents=True, exist_ok=True)
        git(["worktree", "add", "-B", branch, str(wt), base])
        print(f"prepared {row['id']} {branch}")
    return 0


def cmd_csv(args) -> int:
    cur = current(); rows = selected(read_jsonl(lane_path(cur)), args)
    suffix = "_" + wave_value(args.wave) if args.wave else ""
    out = Path(cur["path"]) / f"agent_jobs{suffix}.csv"
    fields = ["wave", "lane_id", "task_id", "agent", "skills", "worktree",
              "branch", "deps", "instruction"]
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        for row in rows:
            skills = ",".join(row.get("skills", [])); deps = ",".join(row.get("deps", []))
            cmd = f"cd {lib.root_dir()} && python3 .codex/script/codex_task_git.py"
            cmd += f" commit {row['task_id']} --lane {row['id']} --message \"{row['title']}\""
            if ko():
                instr = f"작업 위치: {row['worktree']}. 스킬={skills}. 루트에서 완료: {cmd}"
            else:
                instr = f"Work in {row['worktree']}. Skills={skills}. Finish from root: {cmd}"
            writer.writerow({"wave": row.get("wave", "W001"), "lane_id": row["id"],
                             "task_id": row["task_id"], "agent": row["agent"],
                             "skills": skills, "worktree": row["worktree"],
                             "branch": row["branch"], "deps": deps, "instruction": instr})
    print(out); return 0


def cmd_status(args) -> int:
    for row in selected(read_jsonl(lane_path(current())), args):
        wt = Path(row["worktree"])
        if not wt.exists(): print(f"{row['id']} missing worktree"); continue
        proc = git(["status", "--short"], cwd=wt, check=False)
        print(f"{row['id']} {row.get('wave','W001')} {row['agent']} {row['status']} "
              f"{proc.stdout.strip() or 'clean'}")
    return 0


def set_status(cur: dict, lane_id: str, status: str) -> None:
    rows = read_jsonl(lane_path(cur))
    for row in rows:
        if row.get("id") == lane_id: row["status"] = status
    write_jsonl(lane_path(cur), rows); rerender(cur)


def cmd_merge(args) -> int:
    cur = current(); rows = {x["id"]: x for x in read_jsonl(lane_path(cur))}
    row = rows.get(args.lane)
    if not row: raise SystemExit("lane not found")
    git(["merge", "--no-ff", row["branch"], "-m", f"Merge {args.lane}: {row['title']}"])
    set_status(cur, args.lane, "merged"); print(f"merged {args.lane}"); return 0


def cmd_prompt(args) -> int:
    cur = current(); suffix = "_" + wave_value(args.wave) if args.wave else ""
    out = Path(cur["path"]) / f"parallel_prompt{suffix}.md"
    if ko():
        text = ["# 병렬 레인", "", "각 레인을 해당 worktree에서 실행하세요.", ""]
        labels = {"task": "태스크", "worktree": "작업트리", "branch": "브랜치",
                  "deps": "의존성", "skills": "스킬", "goal": "목표", "commit": "커밋"}
    else:
        text = ["# Parallel lanes", "", "Run each lane in its worktree.", ""]
        labels = {"task": "task", "worktree": "worktree", "branch": "branch",
                  "deps": "deps", "skills": "skills", "goal": "goal", "commit": "commit"}
    for row in selected(read_jsonl(lane_path(cur)), args):
        text += [f"## {row.get('wave','W001')} {row['id']} {row['agent']}",
                 f"{labels['task']}: {row['task_id']}", f"{labels['worktree']}: {row['worktree']}",
                 f"{labels['branch']}: {row['branch']}",
                 f"{labels['deps']}: {','.join(row.get('deps', [])) or '-'}",
                 f"{labels['skills']}: {','.join(row.get('skills', []))}",
                 f"{labels['goal']}: {row['title']}",
                 f"{labels['commit']}: cd {lib.root_dir()} && python3 .codex/script/codex_task_git.py commit {row['task_id']} --lane {row['id']}", ""]
    out.write_text("\n".join(text), encoding="utf-8"); print(out); return 0


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add"); a.add_argument("title"); a.add_argument("--task", required=True)
    a.add_argument("--agent", required=True); a.add_argument("--skills", default="")
    a.add_argument("--deps", default=""); a.add_argument("--id"); a.add_argument("--wave", default="")
    l = sub.add_parser("list"); l.add_argument("--json", action="store_true"); l.add_argument("--wave", default="")
    pr = sub.add_parser("prepare"); pr.add_argument("--base"); pr.add_argument("--wave", default="")
    c = sub.add_parser("csv"); c.add_argument("--wave", default="")
    st = sub.add_parser("status"); st.add_argument("--wave", default="")
    pp = sub.add_parser("prompt"); pp.add_argument("--wave", default="")
    m = sub.add_parser("merge"); m.add_argument("lane")
    args = p.parse_args(); return globals()["cmd_" + args.cmd.replace("-", "_")](args)


if __name__ == "__main__":
    raise SystemExit(main())
