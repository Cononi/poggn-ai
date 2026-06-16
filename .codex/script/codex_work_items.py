#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
import lib, codex_budget, codex_feature_infer, codex_lanes, codex_skills, codex_state, codex_agent_pool
FEATURE_LABELS = {
    "product": "상품", "order": "주문", "payment": "결제", "member": "회원",
    "cart": "장바구니", "coupon": "쿠폰", "post": "게시글", "comment": "댓글",
    "delivery": "배송", "review": "리뷰", "inventory": "재고",
    "notification": "알림", "file": "파일", "report": "신고",
    "reservation": "예약", "availability": "예약 가능 시간", "resource": "예약 자원",
    "cancellation": "취소", "course": "강의", "lesson": "수업",
    "enrollment": "수강", "progress": "진도", "quiz": "퀴즈",
    "certificate": "수료증", "account": "고객사", "contact": "연락처",
    "deal": "영업기회", "activity": "활동", "pipeline": "파이프라인",
    "permission": "권한", "category": "카테고리", "tag": "태그",
    "author": "작성자", "seller": "판매자", "buyer": "구매자",
    "listing": "매물", "settlement": "정산", "dispute": "분쟁",
    "chat": "채팅", "patient": "환자", "doctor": "의사",
    "schedule": "일정", "media": "미디어",
    "api": "API", "project": "프로젝트", "contract": "계약",
}
AGENT_LABELS = {
    "architecture": "API/데이터/보안 계약", "backend": "backend API/service",
    "frontend": "frontend UI", "database": "DB schema/query",
    "integration": "외부 연동", "devops": "배포/운영", "docs": "문서",
    "performance": "성능", "test_writer": "테스트 작성", "test_runner": "테스트 실행",
    "qa": "QA", "refactor": "리팩토링", "security": "보안 검토",
}
OWNER_HINTS = {
    "architecture": {
        "owner_files": [".codex-state/*/DECISIONS.md", ".codex-state/*/RISKS.md"],
        "forbidden_files": ["implementation source files unless contract-only stubs are requested"],
        "verification": ["contract review"],
    },
    "backend": {
        "owner_files": ["backend/**", "server/**", "src/main/**", "src/test/**"],
        "forbidden_files": ["frontend/**", "client/**", "ui/**"],
        "verification": ["backend targeted tests"],
    },
    "frontend": {
        "owner_files": ["frontend/**", "client/**", "src/**/*.ts", "src/**/*.tsx"],
        "forbidden_files": ["backend/**", "server/**", "src/main/java/**"],
        "verification": ["frontend targeted tests or build"],
    },
    "database": {
        "owner_files": ["**/migration/**", "**/schema/**", "**/entity/**", "**/repository/**"],
        "forbidden_files": ["unrelated UI files"],
        "verification": ["migration/schema validation or repository tests"],
    },
    "integration": {
        "owner_files": ["**/integration/**", "**/client/**", "**/adapter/**"],
        "forbidden_files": ["unrelated domain/UI files"],
        "verification": ["integration contract tests or documented mock verification"],
    },
    "devops": {
        "owner_files": [".github/**", "Dockerfile", "docker-compose*.yml", "**/build.gradle", "**/package.json"],
        "forbidden_files": ["business logic unless required by delivery config"],
        "verification": ["config lint/build command"],
    },
    "docs": {
        "owner_files": ["README*", "docs/**", ".codex-state/**"],
        "forbidden_files": ["application code"],
        "verification": ["docs review"],
    },
    "performance": {
        "owner_files": ["files directly related to measured bottleneck"],
        "forbidden_files": ["broad rewrites without benchmark evidence"],
        "verification": ["targeted performance or regression check"],
    },
    "test_writer": {
        "owner_files": ["**/*Test.*", "**/*.test.*", "**/__tests__/**", "src/test/**"],
        "forbidden_files": ["production behavior changes"],
        "verification": ["targeted test run"],
    },
    "test_runner": {
        "owner_files": [".codex-state/**"],
        "forbidden_files": ["production source changes"],
        "verification": ["run configured test command"],
    },
    "qa": {
        "owner_files": [".codex-state/**"],
        "forbidden_files": ["production source changes"],
        "verification": ["acceptance review"],
    },
    "refactor": {
        "owner_files": ["files from upstream lane only"],
        "forbidden_files": ["behavior changes without tests"],
        "verification": ["targeted regression tests"],
    },
    "security": {
        "owner_files": [".codex-state/**", "auth/security related files only when fixing findings"],
        "forbidden_files": ["security weakening, secret exposure, broad unrelated rewrites"],
        "verification": ["security gate and negative auth/input checks"],
    },
}


def contract_scope(agent: str) -> dict:
    hint = OWNER_HINTS.get(agent, OWNER_HINTS["performance"])
    return {
        "owner_files": hint["owner_files"],
        "forbidden_files": hint["forbidden_files"],
        "verification": hint["verification"],
        "done_contract": [
            "changed files stay inside owner_files",
            "acceptance criteria are checked",
            "verification result and residual risk are reported",
        ],
    }


def budget_note() -> str:
    maw = codex_budget.config()["maw"]
    return (f"Spark lane budget: <= {maw.get('max_files_per_lane')} files, "
            f"<= {maw.get('max_lines_per_lane')} changed lines; split when larger.")


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
    return codex_feature_infer.words(text)


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
    item.setdefault("budget_note", budget_note())
    for key, value in contract_scope(item.get("agent", "")).items():
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
    return codex_feature_infer.infer_features(text, explicit)
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
    out = []; counts: dict[int, int] = {}; feature_wave = 2
    for row in rows:
        stage = row.get("stage", "implement")
        if stage == "foundation":
            num = 1
        elif stage == "implement":
            num = feature_wave
            while counts.get(num, 0) >= max_lanes:
                num += 1
            feature_wave = num
        else:
            base = max([_wave_of(out, x) for x in row.get("deps", [])] or [feature_wave])
            num = base + 1
            while counts.get(num, 0) >= max_lanes:
                num += 1
        item = dict(row); item["wave"] = wave(num); out.append(item)
        counts[num] = counts.get(num, 0) + 1
    return out
def needs_contract(chosen: set[str], cfg: dict) -> bool:
    if not chosen:
        return True
    contract_relevant = set(cfg.get("implementation_agents", [])) | set(cfg.get("guard_agents", []))
    return bool(chosen & contract_relevant)


def plan(text: str, features: str = "", agents: str = "", guards: str = "auto") -> list[dict]:
    cfg = role_cfg(); chosen = selected(agents); feats = infer_features(text, features); rows = []
    contract_enabled = needs_contract(chosen, cfg)
    if contract_enabled:
        rows.append({"key": "contract", "title": "API contract", "agent": "architecture",
                     "feature": "contract", "stage": "foundation", "deps": []})
    deps0 = ["contract"] if contract_enabled else []
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
    impl_by_feature: dict[str, list[dict]] = {}
    for row in [x for x in rows if x.get("stage") == "implement"]:
        impl_by_feature.setdefault(row.get("feature", "work"), []).append(row)
    for feat in feats:
        impls = impl_by_feature.get(feat, [])
        if not impls:
            continue
        deps = [x["key"] for x in impls]
        for agent, label in [("test_writer", "Test Code"), ("test_runner", "Run Tests"),
                             ("qa", "QA Review"), ("refactor", "Refactor Gate"),
                             ("security", "Security Gate")]:
            if allow(agent, chosen) or (agent.startswith("test") and "test" in chosen):
                key = f"{agent}:{feat}:feature"
                out.append(review(key, deps, feat, agent, label)); deps = [key]
    return out
def review(key: str, deps: list[str], feat: str, agent: str, name: str) -> dict:
    return {"key": key, "title": f"{name}: {title(feat, 'work')}",
            "agent": agent, "feature": feat, "stage": agent, "deps": deps}
def task_id(tasks: list[dict]) -> str: return f"T{len(tasks) + 1:03d}"
def add_task(cur: dict, tasks: list[dict], row: dict, skills: list[str]) -> str:
    tid = task_id(tasks)
    item = {"id": tid, "title": row["title"], "agent": row["agent"],
            "skills": skills, "wave": row["wave"], "stage": row["stage"],
            "feature": row["feature"], "status": "todo", "commit": "", "commits": []}
    for key in ["purpose", "acceptance", "non_goals", "design_source", "request_summary",
                "budget_note", "owner_files", "forbidden_files", "verification",
                "done_contract"]:
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
    for key in ["purpose", "acceptance", "non_goals", "design_source", "request_summary",
                "budget_note", "owner_files", "forbidden_files", "verification",
                "done_contract"]:
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
                        "acceptance": row.get("acceptance"),
                        "owner_files": row.get("owner_files"),
                        "verification": row.get("verification")})
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
