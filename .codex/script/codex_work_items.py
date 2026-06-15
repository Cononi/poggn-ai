#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
import lib, codex_budget, codex_lanes, codex_skills, codex_state, codex_agent_pool
FEATURE_WORDS = {
    "product": "상품 product item catalog", "order": "주문 order checkout",
    "payment": "결제 payment pay billing", "member": "회원 user member account",
    "cart": "장바구니 cart basket", "coupon": "쿠폰 coupon discount",
}
FEATURE_LABELS = {
    "product": "상품", "order": "주문", "payment": "결제", "member": "회원",
    "cart": "장바구니", "coupon": "쿠폰", "api": "API", "project": "프로젝트",
    "contract": "계약",
}
AGENT_LABELS = {
    "architecture": "API/데이터/보안 계약", "backend": "backend API/service",
    "frontend": "frontend UI", "database": "DB schema/query",
    "integration": "외부 연동", "devops": "배포/운영", "docs": "문서",
    "performance": "성능", "test_writer": "테스트 작성", "test_runner": "테스트 실행",
    "qa": "QA", "refactor": "리팩토링", "security": "보안 검토",
}
DEFAULT_ROLES = {
    "implementation_agents": ["backend", "frontend", "database", "integration",
                               "devops", "docs", "performance"],
    "feature_implementation_agents": ["backend", "frontend", "database", "integration"],
    "single_implementation_agents": ["devops", "docs", "performance"],
    "foundation_agents": ["architecture"],
    "guard_agents": ["test_writer", "test_runner", "qa", "refactor", "security"],
    "default_feature_agents": ["backend"],
    "keyword_agents": {
        "frontend": "frontend ui react next page screen 화면 컴포넌트",
        "database": "database sql schema migration query index db 데이터베이스",
        "integration": "integration webhook kafka rabbitmq external api messaging",
        "devops": "docker kubernetes helm ci cd github actions gitlab deploy",
        "docs": "readme docs wiki manual api guide 문서",
        "performance": "performance cache latency n+1 index slow 성능",
    },
}
def words(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9가-힣_]+", text.lower()))


def compact(text: str, limit: int = 140) -> str:
    value = re.sub(r"\s+", " ", text.strip())
    return value if len(value) <= limit else value[:limit - 1].rstrip() + "…"


def label(value: str, table: dict[str, str]) -> str:
    return table.get(value, value or "work")


def contract_for(row: dict, request_text: str = "") -> dict:
    feature = row.get("feature", "work")
    stage = row.get("stage", "implement")
    agent = row.get("agent", "agent")
    feat = label(feature, FEATURE_LABELS)
    role = label(agent, AGENT_LABELS)
    if stage == "foundation":
        purpose = "요청을 구현 전에 public contract, 보안, 검증 기준으로 고정합니다."
        acceptance = "범위, API/데이터 계약, 보안 경계, lane 완료 기준이 명확합니다."
    elif stage == "implement":
        purpose = f"{feat} 기능의 {role} 책임을 구현합니다."
        acceptance = "사용자 시나리오가 동작하고 owner files, 테스트, 보안 gate 기준을 지킵니다."
    else:
        purpose = f"{feat} 기능의 {role} 단계로 구현 결과를 검증합니다."
        acceptance = "이전 lane 결과를 기준으로 실패 원인, blocker, 남은 위험을 분리합니다."
    non_goals = "TASK/lane 범위 밖 리팩토링, unrelated 파일 수정, 검증 생략은 제외합니다."
    source = "rule-based seed; architecture/security/QA lane에서 확정해야 합니다."
    return {
        "purpose": compact(purpose),
        "acceptance": compact(acceptance),
        "non_goals": compact(non_goals),
        "design_source": source,
        "request_summary": compact(request_text, 160) if request_text else "",
    }


def enrich(row: dict, request_text: str = "") -> dict:
    item = dict(row)
    for key, value in contract_for(row, request_text).items():
        if value:
            item.setdefault(key, value)
    return item
def role_cfg() -> dict:
    path = lib.find_codex() / "state" / "agent_roles.json"
    data = lib.read_json(path, DEFAULT_ROLES)
    out = dict(DEFAULT_ROLES); out.update(data); return out
def agent_exists(name: str) -> bool:
    return (lib.find_codex() / "agents" / f"{name}.toml").exists()
def selected(value: str) -> set[str]:
    return {x.strip() for x in value.split(",") if x.strip()}
def infer_features(text: str, explicit: str = "") -> list[str]:
    if explicit:
        return [x.strip() for x in explicit.split(",") if x.strip()]
    q = words(text); found = []
    for name, keys in FEATURE_WORDS.items():
        if q & words(keys): found.append(name)
    if not found and q & words("쇼핑몰 ecommerce shop mall commerce"):
        found = ["product", "member", "order", "cart"]
    return found or ["api"]
def allow(name: str, chosen: set[str]) -> bool:
    return not chosen or name in chosen
def title(feature: str, suffix: str) -> str:
    return feature.replace("-", " ").title() + " " + suffix
def wave(n: int) -> str:
    return f"W{n:03d}"
def keyword_match(agent: str, text: str, cfg: dict) -> bool:
    keys = cfg.get("keyword_agents", {}).get(agent, "")
    return bool(words(text) & words(keys)) if keys else False
def feature_agents(text: str, chosen: set[str], cfg: dict) -> list[str]:
    impl = set(cfg.get("implementation_agents", []))
    feature_impl = set(cfg.get("feature_implementation_agents", []))
    guards = set(cfg.get("guard_agents", [])); foundation = set(cfg.get("foundation_agents", []))
    singles = set(cfg.get("single_implementation_agents", []))
    if not chosen:
        base = list(cfg.get("default_feature_agents", ["backend"]))
        return base + [x for x in feature_impl if x not in base and keyword_match(x, text, cfg)]
    out = []
    for name in sorted(chosen):
        if name in guards or name in foundation or name in singles:
            continue
        if name in feature_impl or (name in impl and name not in singles and keyword_match(name, text, cfg)):
            out.append(name)
        elif agent_exists(name) and name not in cfg.get("single_implementation_agents", []):
            out.append(name)
    return out
def single_agents(text: str, chosen: set[str], cfg: dict) -> list[str]:
    singles = cfg.get("single_implementation_agents", [])
    if not chosen:
        return [x for x in singles if keyword_match(x, text, cfg)]
    return [x for x in singles if x in chosen]
def suffix_for(agent: str) -> str:
    return {"backend":"REST API", "frontend":"UI", "database":"Data Work",
            "integration":"Integration", "devops":"Delivery Work",
            "docs":"Docs", "performance":"Performance Work"}.get(agent, "Implementation")
def skills_for(agent: str, text: str) -> list[str]:
    return codex_skills.recommend(text, agent)
def _wave_of(rows: list[dict], key: str) -> int:
    for row in rows:
        if row.get("key") == key:
            return int(row.get("wave", "W001")[1:])
    return 1
def assign_waves(rows: list[dict]) -> list[dict]:
    max_lanes = int(codex_budget.config()["maw"].get("max_lanes_per_wave", 6))
    out = []; feature_wave = 2; used = 0
    for row in rows:
        stage = row.get("stage", "implement")
        if stage == "foundation": num = 1
        elif stage == "implement":
            if used >= max_lanes: feature_wave += 1; used = 0
            num = feature_wave; used += 1
        else:
            base = max([_wave_of(out, x) for x in row.get("deps", [])] or [feature_wave])
            num = base + 1
        item = dict(row); item["wave"] = wave(num); out.append(item)
    return out
def plan(text: str, features: str = "", agents: str = "", guards: str = "auto") -> list[dict]:
    cfg = role_cfg(); chosen = selected(agents); feats = infer_features(text, features); rows = []
    if allow("architecture", chosen):
        rows.append({"key": "contract", "title": "API contract", "agent": "architecture",
                     "feature": "contract", "stage": "foundation", "deps": []})
    deps0 = ["contract"] if allow("architecture", chosen) else []
    for agent in feature_agents(text, chosen, cfg):
        for feat in feats:
            deps = list(deps0)
            if agent == "frontend" and any(r["key"] == f"impl:{feat}:backend" for r in rows):
                deps = [f"impl:{feat}:backend"]
            rows.append({"key": f"impl:{feat}:{agent}",
                         "title": title(feat, suffix_for(agent)), "agent": agent,
                         "feature": feat, "stage": "implement", "deps": deps})
    impl_keys = [r["key"] for r in rows if r.get("stage") == "implement"]
    for agent in single_agents(text, chosen, cfg):
        rows.append({"key": f"impl:project:{agent}", "title": title("project", suffix_for(agent)),
                     "agent": agent, "feature": "project", "stage": "implement",
                     "deps": impl_keys or deps0})
    if guards == "static": rows += review_rows(feats, chosen, rows)
    return assign_waves([enrich(row, text) for row in rows])
def review_rows(feats: list[str], chosen: set[str], rows: list[dict]) -> list[dict]:
    out = []
    for row in [x for x in rows if x.get("stage") == "implement"]:
        feat = row.get("feature", "work"); prev = row["key"]
        for agent, label in [("test_writer", "Test Code"), ("test_runner", "Run Tests"),
                             ("qa", "QA Review"), ("refactor", "Refactor Gate"),
                             ("security", "Security Gate")]:
            if allow(agent, chosen) or (agent.startswith("test") and "test" in chosen):
                key = f"{agent}:{feat}:{row['agent']}"
                out.append(review(key, prev, feat, agent, label)); prev = key
    return out
def review(key: str, dep: str, feat: str, agent: str, name: str) -> dict:
    return {"key": key, "title": f"{name}: {title(feat, 'work')}",
            "agent": agent, "feature": feat, "stage": agent, "deps": [dep]}
def task_id(tasks: list[dict]) -> str: return f"T{len(tasks) + 1:03d}"
def add_task(cur: dict, tasks: list[dict], row: dict, skills: list[str]) -> str:
    tid = task_id(tasks)
    item = {"id": tid, "title": row["title"], "agent": row["agent"],
            "skills": skills, "wave": row["wave"], "stage": row["stage"],
            "feature": row["feature"], "status": "todo", "commit": "", "commits": []}
    for key in ["purpose", "acceptance", "non_goals", "design_source", "request_summary"]:
        if row.get(key):
            item[key] = row[key]
    tasks.append(item)
    codex_state.write_tasks(cur, tasks)
    codex_state.events(cur, "task_add", {"id": tid, "agent": row["agent"],
                                          "stage": row["stage"], "wave": row["wave"]})
    return tid
def add_lane(cur: dict, row: dict, task: str, skills: list[str], deps: list[str]) -> str:
    path = codex_lanes.lane_path(cur); rows = codex_lanes.read_jsonl(path); lid = f"L{len(rows) + 1:03d}"
    item = {"id": lid, "task_id": task, "agent": row["agent"], "skills": skills,
            "title": row["title"], "wave": row["wave"], "stage": row["stage"],
            "feature": row["feature"], "status": "todo", "commit": "", "commits": [],
            "branch": codex_lanes.branch_name(cur, lid), "worktree": str(codex_lanes.worktree_path(cur, lid)),
            "deps": deps, "upstream_lane_id": deps[-1] if deps else "", "key": row["key"]}
    for key in ["purpose", "acceptance", "non_goals", "design_source", "request_summary"]:
        if row.get(key):
            item[key] = row[key]
    item["worker_name"] = codex_agent_pool.label(item); item["reuse_key"] = codex_agent_pool.reuse_key(item)
    rows.append(item); codex_lanes.write_jsonl(path, rows)
    codex_state.events(cur, "lane_add", {"id": lid, "task_id": task,
                                          "agent": row["agent"], "stage": row["stage"]})
    return lid
def cmd_suggest(args) -> int:
    guards = "static" if args.static_reviews else args.guards
    print(json.dumps(plan(args.text, args.features, args.agents, guards), ensure_ascii=False, indent=2)); return 0
def cmd_apply(args) -> int:
    cur = codex_state.current()
    if not cur: raise SystemExit("workflow not initialized")
    cur["selected_agents"] = sorted(selected(args.agents)); cur["pipeline_mode"] = "event_driven"
    cur["agent_pool"] = sorted(selected(args.agents))
    cur["request_summary"] = compact(args.text, 240)
    cur["planning_source"] = "rule_based_seed_with_expert_lane_review"
    codex_state.save_current(cur)
    tasks = codex_state.read_tasks(cur); key_to_lane = {}; created = []
    guards = "static" if args.static_reviews else args.guards
    for row in plan(args.text, args.features, args.agents, guards):
        skills = skills_for(row["agent"], args.text); tid = add_task(cur, tasks, row, skills)
        deps = [key_to_lane[x] for x in row.get("deps", []) if x in key_to_lane]
        lid = add_lane(cur, row, tid, skills, deps); key_to_lane[row["key"]] = lid
        created.append({"task_id": tid, "lane_id": lid, "stage": row["stage"],
                        "wave": row["wave"], "agent": row["agent"],
                        "deps": deps, "title": row["title"],
                        "purpose": row.get("purpose"),
                        "acceptance": row.get("acceptance")})
    codex_state.write_tasks(cur, tasks); print(json.dumps(created, ensure_ascii=False, indent=2)); return 0
def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    for name in ["suggest", "apply"]:
        s = sub.add_parser(name); s.add_argument("--text", required=True)
        s.add_argument("--features", default=""); s.add_argument("--agents", default="")
        s.add_argument("--static-reviews", action="store_true")
        s.add_argument("--guards", choices=["auto", "static", "off"], default="auto")
    args = p.parse_args(); return globals()["cmd_" + args.cmd](args)
if __name__ == "__main__":
    raise SystemExit(main())
