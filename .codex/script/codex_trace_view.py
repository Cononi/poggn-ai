#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import lib


def jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x]


def lanes(cur: dict) -> list[dict]:
    return jsonl(Path(cur["path"]) / "lanes.jsonl")


def commits(cur: dict) -> list[dict]:
    return jsonl(Path(cur["path"]) / "commits.jsonl")


def waves(cur: dict) -> list[dict]:
    return jsonl(Path(cur["path"]) / "waves.jsonl")


def by_task(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for row in rows:
        out.setdefault(row.get("task_id", ""), []).append(row)
    return out


def by_id(rows: list[dict]) -> dict[str, dict]:
    return {row.get("id", ""): row for row in rows if row.get("id")}


LABELS = {
    "ko": {
        "heading": "# 태스크", "summary": "요약", "commit_map": "커밋 맵",
        "tasks_detail": "태스크 상세", "task_info": "태스크 정보",
        "work_list": "작업 리스트", "change_summary": "변경 요약",
        "changed_files": "변경 파일", "verification": "검증", "item": "항목", "value": "값",
        "title": "제목", "branch": "브랜치", "base": "기준", "workflow": "워크플로",
        "phase": "단계", "run_version": "실행버전", "project_version": "프로젝트버전",
        "next_version": "다음버전", "created_at": "생성시각", "progress": "진행률",
        "waves": "웨이브", "agents": "에이전트", "tasks": "태스크", "commits": "커밋",
        "lanes": "레인", "stages": "단계", "purpose": "목적", "acceptance": "완료기준",
        "non_goals": "제외범위", "worker": "작업자", "last": "마지막", "deps": "의존성",
        "lane": "레인", "stage": "단계", "wave": "웨이브", "commit": "커밋",
        "revert": "되돌리기", "agent": "에이전트", "type": "유형", "task": "태스크",
        "summary_col": "요약", "done": "완료", "instruction": "작업 지시", "assignee": "담당",
        "completed_at": "완료 시간", "status": "상태", "skills": "스킬", "feature": "기능",
        "file_type": "유형", "file": "파일", "result": "결과", "evidence": "근거",
        "pending": "대기", "complete": "완료", "none": "-", "linked_commit": "연결 커밋",
        "no_file": "파일 없음", "no_commit": "연결된 커밋 없음", "no_verification": "검증 lane 없음",
    },
    "en": {
        "heading": "# TASKS", "summary": "Summary", "commit_map": "Commit Map",
        "tasks_detail": "Task Details", "task_info": "Task Info",
        "work_list": "Work List", "change_summary": "Change Summary",
        "changed_files": "Changed Files", "verification": "Verification", "item": "Item", "value": "Value",
        "title": "Title", "branch": "Branch", "base": "Base", "workflow": "Workflow",
        "phase": "Phase", "run_version": "Run Version", "project_version": "Project Version",
        "next_version": "Next Version", "created_at": "Created At", "progress": "Progress",
        "waves": "Waves", "agents": "Agents", "tasks": "Tasks", "commits": "Commits",
        "lanes": "Lanes", "stages": "Stages", "purpose": "Purpose", "acceptance": "Acceptance",
        "non_goals": "Non-goals", "worker": "Worker", "last": "Last", "deps": "Deps",
        "lane": "Lane", "stage": "Stage", "wave": "Wave", "commit": "Commit",
        "revert": "Revert", "agent": "Agent", "type": "Type", "task": "Task",
        "summary_col": "Summary", "done": "Done", "instruction": "Instruction", "assignee": "Assignee",
        "completed_at": "Completed At", "status": "Status", "skills": "Skills", "feature": "Feature",
        "file_type": "Type", "file": "File", "result": "Result", "evidence": "Evidence",
        "pending": "Pending", "complete": "Complete", "none": "-", "linked_commit": "Linked commit",
        "no_file": "No changed files", "no_commit": "No linked commits", "no_verification": "No verification lanes",
    },
}


VERIFY_STAGES = {"test", "test_writer", "test_runner", "qa", "security", "refactor", "review"}


def current_labels() -> dict:
    return LABELS.get(lib.language(), LABELS["ko"])


def md(value) -> str:
    text = str(value if value is not None else "-")
    return text.replace("|", "\\|").replace("\n", " ")


def code(value) -> str:
    value = str(value or "-")
    return f"`{md(value)}`" if value != "-" else "-"


def short_path(path: str, max_len: int = 96) -> str:
    return path if len(path) <= max_len else "..." + path[-max_len + 3:]


def value_text(value, limit: int = 220) -> str:
    if isinstance(value, list):
        value = "; ".join(str(x) for x in value if x)
    elif value is None:
        value = ""
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


def fallback_purpose(item: dict) -> str:
    stage = item.get("stage", "implement")
    feature = item.get("feature", "work")
    agent = item.get("agent", "agent")
    if stage == "foundation":
        return "요청을 구현 전에 public contract, 보안, 검증 기준으로 고정합니다."
    if stage == "implement":
        return f"{feature} 기능의 {agent} 책임을 구현합니다."
    return f"{feature} 기능의 {agent} 단계로 구현 결과를 검증합니다."


def fallback_acceptance(item: dict) -> str:
    stage = item.get("stage", "implement")
    if stage == "foundation":
        return "범위, 계약, 보안 경계, lane 완료 기준이 명확합니다."
    if stage == "implement":
        return "사용자 시나리오, owner files, 테스트, 보안 기준을 충족합니다."
    return "실패 원인, blocker, 남은 위험을 분리해 보고합니다."


def file_code(raw: str) -> str:
    parts = raw.split("	")
    raw_code = parts[0][:1] if parts else "?"
    return raw_code if raw_code in {"A", "M", "D", "R"} else "?"


def file_path(raw: str) -> str:
    parts = raw.split("	")
    return parts[-1] if len(parts) > 1 else raw


def file_counts(rows: list[dict]) -> dict[str, int]:
    counts = {"A": 0, "M": 0, "D": 0, "R": 0}
    for row in rows:
        for raw in row.get("files", []):
            code_ = file_code(raw)
            if code_ in counts:
                counts[code_] += 1
    return counts


def table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    if not rows:
        rows = [["-" for _ in headers]]
    lines.extend("| " + " | ".join(md(cell) for cell in row) + " |" for row in rows)
    return lines


def info_table(rows: list[tuple[str, str]]) -> list[str]:
    labels = current_labels()
    return table([labels["item"], labels["value"]], [[k, v] for k, v in rows])


def commit_short(row: dict) -> str:
    return row.get("short") or str(row.get("commit", ""))[:7] or "-"


def commit_summary(row: dict, task: dict | None, lane: dict | None) -> str:
    return value_text(row.get("summary") or row.get("subject") or
                      (lane or {}).get("title") or (task or {}).get("title") or "-")


def commit_map_rows(tasks: list[dict], lane_rows: list[dict], commit_rows: list[dict]) -> list[list[str]]:
    labels = current_labels(); tasks_by_id = by_id(tasks); lanes_by_id = by_id(lane_rows)
    rows = []
    for row in commit_rows:
        task = tasks_by_id.get(row.get("task_id", ""), {})
        lane = lanes_by_id.get(row.get("lane_id", ""), {})
        short = commit_short(row)
        rows.append([
            code(short), row.get("task_id", "-"), row.get("lane_id") or "-",
            lane.get("worker_name") or row.get("agent") or task.get("agent", "-"),
            lane.get("stage") or task.get("stage") or "-", commit_summary(row, task, lane),
            code(f"git revert {short}") if short != "-" else labels["none"],
        ])
    return rows


def completed_at(row: dict | None) -> str:
    return (row or {}).get("time") or "-"


def lane_commit_rows(lane: dict, commits_for_task: list[dict]) -> list[dict]:
    lid = lane.get("id", "")
    return [row for row in commits_for_task if row.get("lane_id") == lid]


def task_direct_commits(task: dict, commits_for_task: list[dict]) -> list[dict]:
    return [row for row in commits_for_task if not row.get("lane_id")]


def commit_cell(rows: list[dict], task: dict, lane: dict | None = None) -> str:
    if not rows:
        return "-"
    cells = []
    for row in rows:
        short = commit_short(row)
        cells.append(f"{code(short)} - {md(commit_summary(row, task, lane))}")
    return "<br>".join(cells)


def work_rows(task: dict, task_lanes: list[dict], commits_for_task: list[dict]) -> list[list[str]]:
    labels = current_labels(); rows = []
    if task_lanes:
        for lane in task_lanes:
            commits_ = lane_commit_rows(lane, commits_for_task)
            done = "[x]" if lane.get("status") in {"done", "merged"} else "[ ]"
            rows.append([
                done, lane.get("id", "-"), value_text(lane.get("title") or task.get("title")),
                lane.get("worker_name") or lane.get("agent", "-"), completed_at(commits_[0] if commits_ else None),
                commit_cell(commits_, task, lane),
            ])
        return rows
    commits_ = task_direct_commits(task, commits_for_task) or commits_for_task
    done = "[x]" if task.get("status") == "done" and commits_ else "[ ]"
    rows.append([
        done, task.get("id", "-"), value_text(task.get("title")), task.get("agent", "-"),
        completed_at(commits_[0] if commits_ else None), commit_cell(commits_, task),
    ])
    return rows


def changed_file_rows(commits_for_task: list[dict]) -> list[list[str]]:
    rows = []
    seen = set()
    for row in commits_for_task:
        for raw in row.get("files", []):
            item = (file_code(raw), file_path(raw))
            if item in seen:
                continue
            seen.add(item); rows.append([item[0], code(short_path(item[1]))])
    return rows


def verification_rows(task: dict, task_lanes: list[dict], commits_for_task: list[dict]) -> list[list[str]]:
    labels = current_labels(); rows = []
    for lane in task_lanes:
        stage = lane.get("stage") or lane.get("agent", "")
        if stage not in VERIFY_STAGES and lane.get("agent") not in VERIFY_STAGES:
            continue
        commits_ = lane_commit_rows(lane, commits_for_task)
        result = labels["complete"] if lane.get("status") in {"done", "merged"} else labels["pending"]
        rows.append([stage, result, commit_cell(commits_, task, lane) or lane.get("title", "-")])
    return rows


def summary_lines(cur: dict, tasks: list[dict], lane_rows: list[dict], commit_rows: list[dict]) -> list[str]:
    labels = current_labels()
    done = sum(1 for t in tasks if task_done(t, [x for x in lane_rows if x.get("task_id") == t.get("id")],
                                      [x for x in commit_rows if x.get("task_id") == t.get("id")]))
    counts = file_counts(commit_rows)
    return [
        f"## {labels['summary']}",
        *info_table([
            (labels["title"], cur.get("title", "-")),
            (labels["workflow"], cur.get("workflow", "-")),
            (labels["phase"], cur.get("phase", "-")),
            (labels["progress"], f"{done}/{len(tasks)}"),
            (labels["branch"], cur.get("branch", "-")),
            (labels["base"], cur.get("base_branch", "-")),
            (labels["run_version"], str(cur.get("run_version", "-"))),
            (labels["project_version"], cur.get("project_version", "-")),
            (labels["next_version"], cur.get("next_version", "-")),
            (labels["created_at"], cur.get("created_at", "-")),
            (labels["tasks"], str(len(tasks))),
            (labels["lanes"], str(len(lane_rows))),
            (labels["commits"], str(len(commit_rows))),
            (labels["changed_files"], f"A{counts['A']} M{counts['M']} D{counts['D']} R{counts['R']}"),
        ]),
    ]


def task_done(task: dict, task_lanes: list[dict], task_commits: list[dict]) -> bool:
    if task.get("status") != "done":
        return False
    if task_lanes:
        ok = all(x.get("status") in {"done", "merged"} for x in task_lanes)
        return ok and bool(task_commits)
    return bool(task.get("commits") or task_commits)


def task_section(task: dict, task_lanes: list[dict], commits_for_task: list[dict]) -> list[str]:
    labels = current_labels(); counts = file_counts(commits_for_task)
    worker_names = [x.get("worker_name") for x in task_lanes if x.get("worker_name")]
    worker = ", ".join(worker_names) if worker_names else task.get("agent", "-")
    status = labels["complete"] if task_done(task, task_lanes, commits_for_task) else labels["pending"]
    lines = ["", f"## {task.get('id', '-')} - {task.get('title', '-')}", "",
             f"### {labels['task_info']}"]
    lines += info_table([
        (labels["agent"], task.get("agent", "-")),
        (labels["worker"], worker),
        (labels["stage"], task.get("stage", "-")),
        (labels["wave"], task.get("wave", "-")),
        (labels["feature"], task.get("feature", "-")),
        (labels["status"], status),
        (labels["skills"], ",".join(task.get("skills", [])) or "-"),
        (labels["purpose"], value_text(task.get("purpose") or fallback_purpose(task))),
        (labels["acceptance"], value_text(task.get("acceptance") or fallback_acceptance(task))),
        (labels["non_goals"], value_text(task.get("non_goals")) or "-"),
    ])
    lines += ["", f"### {labels['work_list']}"]
    lines += table([labels["done"], labels["lane"], labels["instruction"], labels["assignee"],
                    labels["completed_at"], labels["commit"]], work_rows(task, task_lanes, commits_for_task))
    lines += ["", f"### {labels['change_summary']}"]
    lines += table(["ADD", "UPDATE", "DELETE", "RENAME"],
                   [[str(counts["A"]), str(counts["M"]), str(counts["D"]), str(counts["R"])]])
    lines += ["", f"### {labels['changed_files']}"]
    file_rows = changed_file_rows(commits_for_task)
    lines += table([labels["file_type"], labels["file"]], file_rows or [["-", labels["no_file"]]])
    lines += ["", f"### {labels['verification']}"]
    verify = verification_rows(task, task_lanes, commits_for_task)
    lines += table([labels["type"], labels["result"], labels["evidence"]],
                   verify or [["-", labels["pending"], labels["no_verification"]]])
    return lines


def render(cur: dict, tasks: list[dict]) -> None:
    labels = current_labels(); lane_rows = lanes(cur); commit_rows = commits(cur)
    lane_map = by_task(lane_rows); commit_map = by_task(commit_rows)
    lines = [labels["heading"], ""]
    lines += summary_lines(cur, tasks, lane_rows, commit_rows)
    lines += ["", f"## {labels['commit_map']}"]
    lines += table([labels["commit"], labels["task"], labels["lane"], labels["agent"], labels["type"],
                    labels["summary_col"], labels["revert"]],
                   commit_map_rows(tasks, lane_rows, commit_rows) or
                   [["-", "-", "-", "-", "-", labels["no_commit"], "-"]])
    lines += ["", f"# {labels['tasks_detail']}"]
    for task in tasks:
        lines += task_section(task, lane_map.get(task.get("id", ""), []),
                              commit_map.get(task.get("id", ""), []))
    (Path(cur["path"]) / "TASKS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
