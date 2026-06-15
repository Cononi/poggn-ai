#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path
import lib
DEFAULT = {
    "foundation_agents": ["architecture"],
    "implementation_agents": ["backend", "frontend", "database", "integration", "devops", "docs", "performance"],
    "feature_implementation_agents": ["backend", "frontend", "database", "integration"],
    "single_implementation_agents": ["devops", "docs", "performance"],
    "guard_agents": ["test_writer", "test_runner", "test", "qa", "refactor", "security"],
    "management_agents": ["git", "capability_manager"],
    "default_feature_agents": ["backend"],
    "keyword_agents": {
        "frontend": "frontend react next ui page screen component tsx 화면 컴포넌트",
        "database": "database db sql schema migration query index table jpa 데이터베이스",
        "integration": "integration webhook external api kafka event message grpc",
        "devops": "docker ci cd deploy pipeline kubernetes helm action gitlab",
        "docs": "readme docs document wiki changelog release note 문서",
        "performance": "performance cache latency n+1 index slow 성능",
    },
}
def path() -> Path: return lib.find_codex() / "state" / "agent_roles.json"
def config() -> dict:
    data = lib.read_json(path(), DEFAULT); out = dict(DEFAULT); out.update(data)
    out["keyword_agents"] = {**DEFAULT["keyword_agents"], **out.get("keyword_agents", {})}
    return out
def words(text: str) -> set[str]: return set(re.findall(r"[A-Za-z0-9가-힣_]+", text.lower()))
def selected(value: str | set[str] | list[str]) -> set[str]:
    if isinstance(value, set): return value
    if isinstance(value, list): return {str(x).strip() for x in value if str(x).strip()}
    return {x.strip() for x in str(value).split(",") if x.strip()}
def known_agents() -> set[str]: return {p.stem for p in (lib.find_codex() / "agents").glob("*.toml")}
def role(agent: str) -> str:
    c = config()
    if agent in c.get("foundation_agents", []): return "foundation"
    if agent in c.get("guard_agents", []): return "guard"
    if agent in c.get("management_agents", []): return "management"
    if agent in c.get("single_implementation_agents", []): return "implementation_single"
    if agent in c.get("feature_implementation_agents", []): return "implementation_feature"
    if agent in c.get("implementation_agents", []) or agent in known_agents(): return "implementation_feature"
    return "unknown"
def trigger(agent: str, text: str) -> bool:
    keys = config().get("keyword_agents", {}).get(agent, agent)
    return bool(words(text) & words(keys))
def implementers(text: str = "", agents: str | set[str] | list[str] = "") -> dict:
    c = config(); chosen = selected(agents); known = known_agents()
    source = chosen or set(c.get("default_feature_agents", [])) | set(c.get("implementation_agents", []))
    feature, single = [], []
    for a in sorted(source):
        if a not in known or not role(a).startswith("implementation"): continue
        if chosen or a in c.get("default_feature_agents", []) or trigger(a, text):
            (single if role(a) == "implementation_single" else feature).append(a)
    return {"feature": feature, "single": single}
def groups(agents: str = "") -> dict:
    items = selected(agents) or known_agents(); out: dict[str, list[str]] = {}
    for a in sorted(items): out.setdefault(role(a), []).append(a)
    return out
def cmd_list(args) -> int:
    print(json.dumps(groups(args.agents), ensure_ascii=False, indent=2)); return 0
def cmd_impl(args) -> int:
    print(json.dumps(implementers(args.text, args.agents), ensure_ascii=False, indent=2)); return 0
def cmd_policy(args) -> int:
    print(json.dumps(config(), ensure_ascii=False, indent=2)); return 0
def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list"); l.add_argument("--agents", default="")
    i = sub.add_parser("implementers"); i.add_argument("--text", default=""); i.add_argument("--agents", default="")
    sub.add_parser("policy"); args = p.parse_args()
    return {"list": cmd_list, "implementers": cmd_impl, "policy": cmd_policy}[args.cmd](args)
if __name__ == "__main__": raise SystemExit(main())
