#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
import lib

KEYWORDS = {
    "spring-boot": "spring boot java backend server api 서버",
    "jpa": "jpa entity repository query transaction orm 데이터",
    "database-migration": "database db schema migration sql table 데이터",
    "api-contract": "api rest dto request response error contract endpoint",
    "openapi-swagger": "swagger openapi api docs spec 문서",
    "react": "react frontend ui component 화면",
    "nextjs": "next nextjs routing page server action",
    "frontend-component-architecture": "frontend component reusable variant compound primitive ui",
    "frontend-typescript": "frontend react typescript tsx ts strict props dto",
    "quality-gate": "quality gate spaghetti duplicate large security 품질",
    "verify-gate": "verify validation test security quality staged 검증",
    "test-generation": "test unit integration coverage 테스트",
    "security-gate": "security auth permission secret token 보안 권한",
    "ci-cd": "ci cd docker github gitlab deploy 배포",
    "rollback": "rollback revert git history 복구",
    "docs": "docs readme markdown release 문서",
    "task-trace": "task commit trace diff compare tracking",
    "refactor-clean-code": "refactor clean duplicate method 리팩토링 중복",
}

AGENT_BASE = {
    "architecture": ["api-contract"],
    "backend": ["spring-boot", "api-contract"],
    "frontend": ["react", "frontend-typescript", "api-contract",
                 "frontend-component-architecture"],
    "database": ["database-migration"],
    "qa": ["quality-gate", "verify-gate"],
    "test": ["test-generation", "verify-gate"],
    "test_writer": ["test-generation", "verify-gate"],
    "test_runner": ["verify-gate", "test-generation"],
    "security": ["security-gate", "verify-gate"],
    "devops": ["ci-cd"],
    "git": ["git-automation", "task-trace", "rollback"],
    "docs": ["docs", "language-policy"],
    "integration": ["api-contract"],
    "performance": [],
    "refactor": ["refactor-clean-code", "quality-gate"],
}

AGENT_ALLOWED = {
    "architecture": {"api-contract", "openapi-swagger", "docs"},
    "backend": {"spring-boot", "jpa", "api-contract", "openapi-swagger"},
    "frontend": {"react", "nextjs", "frontend-typescript", "api-contract",
                 "openapi-swagger", "frontend-component-architecture", "quality-gate"},
    "database": {"database-migration", "jpa"},
    "qa": {"test-generation", "quality-gate", "verify-gate", "refactor-clean-code",
           "frontend-component-architecture"},
    "test": {"test-generation", "verify-gate", "api-contract", "openapi-swagger"},
    "test_writer": {"test-generation", "verify-gate", "api-contract", "openapi-swagger"},
    "test_runner": {"test-generation", "verify-gate", "api-contract", "openapi-swagger"},
    "security": {"security-gate", "quality-gate", "verify-gate"},
    "devops": {"ci-cd", "security-gate"},
    "git": {"git-automation", "task-trace", "rollback"},
    "docs": {"docs", "language-policy", "openapi-swagger"},
    "integration": {"api-contract", "test-generation"},
    "performance": {"test-generation"},
    "refactor": {"refactor-clean-code", "test-generation", "task-trace",
                 "quality-gate", "frontend-component-architecture"},
}

RULES = {
    "jpa": "jpa entity repository sql database db orm shop 쇼핑몰",
    "openapi-swagger": "swagger openapi rest api endpoint docs",
    "nextjs": "next nextjs app router server action",
    "react": "react ui component frontend 화면",
    "test-generation": "test 테스트 unit integration qa regression",
    "security-gate": "security auth permission secret token 보안",
    "database-migration": "schema migration table database db sql",
    "refactor-clean-code": "refactor duplicate clean cleanup 리팩토링",
    "quality-gate": "quality clean maintainability spaghetti duplicate 보완 품질",
    "verify-gate": "verify validation test security quality staged 검증",
    "frontend-component-architecture": "frontend react component reusable variant compound primitive",
    "frontend-typescript": "typescript tsx react props strict any jsx",
}


def skill_docs() -> dict[str, str]:
    root = lib.find_codex() / "skills"
    out = {}
    for p in root.iterdir():
        f = p / "SKILL.md"
        if f.exists(): out[p.name] = f.read_text(encoding="utf-8")
    return out



def meta() -> dict[str, str]:
    out = {}
    root = lib.find_codex() / "skills"
    for path in root.iterdir():
        skill = path / "SKILL.md"
        if not skill.exists():
            continue
        txt = skill.read_text(encoding="utf-8", errors="ignore")[:1200]
        m = re.search(r"^description:\s*(.+)$", txt, re.M)
        out[path.name] = (m.group(1) if m else "")
    return out

def names() -> list[str]:
    return sorted(skill_docs())


def words(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9가-힣_]+", text.lower()))


def add_if(out: list[str], item: str, available: set[str]) -> None:
    if item in available and item not in out:
        out.append(item)


def selected_agents(agents: str) -> list[str]:
    return [x.strip() for x in agents.split(",") if x.strip()]


def allowed_for(agents: str, available: set[str]) -> set[str]:
    picked = selected_agents(agents)
    if not picked:
        return available
    allowed: set[str] = set()
    for agent in picked:
        allowed |= AGENT_ALLOWED.get(agent, set())
    allowed |= (dynamic_names() & available)
    return allowed & available


def dynamic_names() -> set[str]:
    data = lib.read_json(lib.find_codex() / "state" / "extension_registry.json", {"items": []})
    return {x.get("name", "") for x in data.get("items", []) if x.get("kind") == "skill"}

def skill_doc(name: str) -> str:
    path = lib.find_codex() / "skills" / name / "SKILL.md"
    try:
        return path.read_text(encoding="utf-8")[:2000]
    except FileNotFoundError:
        return ""

def recommend(text: str, agents: str) -> list[str]:
    query = words(text); available = set(names()); allowed = allowed_for(agents, available)
    out: list[str] = []
    for agent in selected_agents(agents):
        for item in AGENT_BASE.get(agent, []):
            if item in allowed:
                add_if(out, item, available)
    merged = {**KEYWORDS, **RULES}
    for name in dynamic_names():
        if name in available:
            merged[name] = skill_doc(name)
    for name, key in merged.items():
        if name in allowed and query & words(key):
            add_if(out, name, available)
    return out


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list"); l.add_argument("--json", action="store_true")
    r = sub.add_parser("recommend"); r.add_argument("--text", required=True)
    r.add_argument("--agents", default=""); r.add_argument("--json", action="store_true")
    args = p.parse_args()
    data = names() if args.cmd == "list" else recommend(args.text, args.agents)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        label = "추천 skill" if lib.language() == "ko" else "Recommended skills"
        print(label + ": " + ",".join(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
