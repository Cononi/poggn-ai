#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path
import lib

try:
    import tomllib
except Exception:
    tomllib = None

KEYWORDS = {
    "architecture": "architecture design plan domain 요구사항 설계 구조",
    "backend": "backend api server spring boot jpa service 서버 api",
    "frontend": "frontend react next ui page 화면 컴포넌트",
    "database": "database db sql migration schema jpa query 데이터",
    "qa": "qa acceptance scenario regression 품질 검수 시나리오",
    "test": "test unit integration coverage 테스트 검증",
    "security": "security auth permission secret token 보안 권한",
    "devops": "ci cd docker deploy github gitlab pipeline 배포",
    "git": "git branch commit rollback revert remote history",
    "docs": "docs readme markdown release 문서 가이드",
    "integration": "external api event kafka redis message 연동",
    "performance": "performance cache slow query latency 성능",
    "refactor": "refactor cleanup duplicate clean code 리팩토링 정리 중복",
}

DEFAULTS = {
    "shop": ["architecture", "backend", "database", "test", "qa", "security"],
    "쇼핑몰": ["architecture", "backend", "database", "test", "qa", "security"],
    "admin": ["architecture", "frontend", "backend", "test", "qa"],
    "배포": ["devops", "git", "security", "qa"],
}


def load_toml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if tomllib:
        return tomllib.loads(text)
    out = {}
    for line in text.splitlines():
        m = re.match(r'^(name|description|model|model_reasoning_effort)\s*=\s*"(.*)"', line)
        if m:
            out[m.group(1)] = m.group(2)
        n = re.match(r'^nickname_candidates\s*=\s*\[(.*)\]', line)
        if n:
            out['nickname_candidates'] = re.findall(r'"([^"]+)"', n.group(1))
    if "developer_instructions" in text:
        out["developer_instructions"] = "present"
    return out


def agents() -> list[dict]:
    root = lib.find_codex() / "agents"; out = []
    for path in sorted(root.glob("*.toml")):
        data = load_toml(path)
        if data.get("name"):
            data["file"] = str(path.relative_to(lib.root_dir()))
            out.append(data)
    return out


def words(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9가-힣_]+", text.lower()))


def score_item(item: dict, query: set[str]) -> int:
    name = item.get("name", "")
    hay = words(name + " " + KEYWORDS.get(name, "") + " "
                + item.get("description", "") + " "
                + str(item.get("developer_instructions", "")))
    return len(query & hay)


def recommend(text: str) -> list[dict]:
    local = {x["name"]: x for x in agents()}; query = words(text)
    names = []
    for key, value in DEFAULTS.items():
        if key.lower() in text.lower():
            names += value
    ranked = sorted(local, key=lambda n: score_item(local[n], query), reverse=True)
    names += [n for n in ranked if score_item(local[n], query) > 0]
    names += ["architecture", "backend", "test", "qa", "security"]
    seen = []
    for name in names:
        if name in local and name not in seen:
            seen.append(name)
    return [local[n] for n in seen[:8]]


def check() -> int:
    errors = []; seen = set()
    pat = re.compile(r"^[A-Za-z0-9 _-]+$")
    for item in agents():
        name = item.get("name", "")
        if name in seen:
            errors.append(f"duplicate agent: {name}")
        seen.add(name)
        fields = ["name", "description", "developer_instructions"]
        fields += ["model", "model_reasoning_effort"]
        for field in fields:
            if not item.get(field):
                errors.append(f"{item.get('file')}: missing {field}")
        nicks = item.get("nickname_candidates", [])
        if nicks:
            if len(nicks) != len(set(nicks)):
                errors.append(f"{item.get('file')}: duplicate nickname_candidates")
            bad = [x for x in nicks if not re.match(r"^[A-Za-z0-9 _-]+$", x)]
            if bad:
                errors.append(f"{item.get('file')}: invalid nickname_candidates {bad}")
        nicks = item.get("nickname_candidates", [])
        if nicks:
            if len(nicks) != len(set(nicks)):
                errors.append(f"{item.get('file')}: duplicate nickname_candidates")
            bad = [x for x in nicks if not pat.match(str(x))]
            if bad:
                errors.append(f"{item.get('file')}: invalid nickname {bad[0]}")
    if errors:
        print("\n".join(errors)); return 2
    print("agent check ok"); return 0


def show(items: list[dict], as_json: bool) -> None:
    if as_json:
        print(json.dumps(items, ensure_ascii=False, indent=2)); return
    ko = lib.language() == "ko"
    print(("추천 agent" if ko else "Recommended agents") + ":")
    for item in items:
        print(f"- {item['name']}: {item.get('description','')}")
    print("")
    if ko:
        print("선택 예시: backend,database,test,qa")
        print("추가 예시: architecture,backend,database,test,qa,security")
    else:
        print("Selection example: backend,database,test,qa")
        print("Add example: architecture,backend,database,test,qa,security")


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list"); l.add_argument("--json", action="store_true")
    r = sub.add_parser("recommend"); r.add_argument("--text", required=True)
    r.add_argument("--json", action="store_true")
    sub.add_parser("check"); args = p.parse_args()
    if args.cmd == "list":
        show(agents(), args.json); return 0
    if args.cmd == "recommend":
        show(recommend(args.text), args.json); return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
