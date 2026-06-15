#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, textwrap
from pathlib import Path
import lib
STOP = set('the a an and or to for of in on with by is are be 를 을 은 는 이 가 에 의'.split())
DEFAULT = {"require_approve": True, "require_edit_mode": True,
           "similarity_threshold": 0.38, "model": "gpt-5.3-codex-spark"}
def cfg() -> dict:
    data = lib.read_json(lib.find_codex() / "state" / "extension_policy.json", DEFAULT)
    out = dict(DEFAULT); out.update(data); return out
def words(text: str) -> set[str]:
    return {x for x in re.findall(r"[A-Za-z0-9가-힣_]+", text.lower()) if x not in STOP}
def slug(text: str) -> str:
    return lib.safe_slug(text).replace("_", "-")
def read_agent(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    data = {"file": str(path.relative_to(lib.root_dir())), "kind": "agent", "text": text}
    for key in ["name", "description", "model", "model_reasoning_effort"]:
        m = re.search(rf'^{key}\s*=\s*"([^"]*)"', text, re.M)
        if m: data[key] = m.group(1)
    data.setdefault("name", path.stem); data.setdefault("description", "")
    return data
def read_skill(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    data = {"file": str(path.relative_to(lib.root_dir())), "kind": "skill", "text": text}
    m = re.search(r"---\n(.*?)\n---", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1); data[k.strip()] = v.strip()
    data.setdefault("name", path.parent.name); data.setdefault("description", "")
    return data
def inventory(kind: str) -> list[dict]:
    base = lib.find_codex() / ("agents" if kind == "agent" else "skills")
    if kind == "agent": return [read_agent(p) for p in sorted(base.glob("*.toml"))]
    return [read_skill(p / "SKILL.md") for p in sorted(base.iterdir()) if (p / "SKILL.md").exists()]
def score(item: dict, name: str, purpose: str) -> float:
    q = words(name + " " + purpose)
    hay = item.get("name", "") + " " + item.get("description", "")
    h = words(hay + " " + item.get("text", ""))
    return 0.0 if not q or not h else len(q & h) / max(1, min(len(q), len(h)))
def similar(kind: str, name: str, purpose: str) -> list[dict]:
    out = []
    for item in inventory(kind):
        val = score(item, name, purpose)
        if item.get("name") == slug(name) or val >= cfg()["similarity_threshold"]:
            out.append({"name": item.get("name"), "file": item.get("file"),
                        "score": round(val, 2),
                        "description": item.get("description", "")})
    return sorted(out, key=lambda x: x["score"], reverse=True)
def duplicate_report() -> dict:
    issues = []
    for kind in ["agent", "skill"]:
        rows = inventory(kind)
        for i, a in enumerate(rows):
            for b in rows[i + 1:]:
                val = score(a, b.get("name", ""), b.get("description", ""))
                if val >= cfg()["similarity_threshold"]:
                    issues.append({"kind": kind, "a": a.get("name"),
                                   "b": b.get("name"), "score": round(val, 2)})
    return {"issues": issues}
def edit_allowed() -> bool:
    p = lib.find_codex() / "state" / "edit_mode.json"
    return lib.read_json(p, {"mode": "project"}).get("mode") == "codex"
def need_approve(args) -> None:
    if cfg().get("require_edit_mode", True) and not edit_allowed():
        raise SystemExit("run $codex-edit-mode on before extending .codex")
    if cfg().get("require_approve", True) and not getattr(args, "approve", False):
        raise SystemExit("add --approve after reviewing duplicate results")
def block_if_duplicate(kind: str, name: str, purpose: str, force: bool) -> None:
    hits = similar(kind, name, purpose)
    if hits and not force:
        data = {"blocked": True, "similar": hits[:5], "next": "reuse or pass --force"}
        raise SystemExit(json.dumps(data, ensure_ascii=False, indent=2))
def registry(row: dict) -> None:
    p = lib.find_codex() / "state" / "extension_registry.json"
    data = lib.read_json(p, {"items": []})
    data.setdefault("items", []).append({**row, "time": lib.now(), "language": lib.language()})
    lib.write_json(p, data)
def agent_text(name: str, purpose: str) -> str:
    hard = words(purpose) & words("security architecture refactor payment auth")
    effort = "high" if hard else "medium"; ko = lib.language() == "ko"
    desc = purpose.replace('"', "'")[:92]; nick = name.replace("_", "-")
    pool = [name, f"{nick}-worker", f"{nick}-lane"]
    unique = []
    for item in pool:
        if item not in unique:
            unique.append(item)
    nick_text = ", ".join(json.dumps(x) for x in unique)
    ko_body = [f"{name} agent는 {purpose} 역할만 수행합니다.",
               "다른 agent 책임을 대신 수행하지 않습니다.",
               "TASK, lane, feature 범위를 벗어나지 않습니다.",
               "구현 agent는 테스트, QA, 보안 완료를 주장하지 않습니다.",
               "변경 파일, 검증 결과, 위험, 후속 요청만 보고합니다."]
    en_body = [f"The {name} agent only performs this role: {purpose}.",
               "Do not take over another agent's responsibility.",
               "Stay inside the assigned TASK, lane, and feature scope.",
               "Implementation agents must not claim test, QA, or security completion.",
               "Report changed files, verification, risks, and downstream needs."]
    instr = "\n".join(ko_body if ko else en_body)
    return (f'name = "{name}"\ndescription = "{desc}"\n'
            f'nickname_candidates = [{nick_text}]\n'
            f'model = "{cfg()["model"]}"\nmodel_reasoning_effort = "{effort}"\n'
            f'developer_instructions = """\n{instr}\n"""\n')
def skill_body(name: str, purpose: str, domain: str) -> str:
    ko = lib.language() == "ko"; desc = purpose.replace("\n", " ")[:92]
    ko_body = ["## 목적", purpose, "## 사용 시점", f"{domain} 작업에 직접 필요할 때만 사용합니다.",
               "## 금지", "다른 skill과 같은 절차를 중복 생성하지 않습니다.",
               "## 클린 코드", "작은 함수, 명확한 이름, 단일 책임, 중복 제거를 지킵니다.",
               "## 보안", "secret, token, 권한, 입력 검증, 배포 유출을 확인합니다."]
    en_body = ["## Goal", purpose, "## When to use", f"Use only when {domain} is directly needed.",
               "## Do not", "Do not duplicate another skill's workflow.",
               "## Clean code", "Use small functions, clear names, one responsibility, no duplication.",
               "## Security", "Check secrets, tokens, permissions, input validation, release leakage."]
    lines = ["---", f"name: {name}", f"description: {desc}", "---", ""]
    for item in ko_body if ko else en_body:
        lines += textwrap.wrap(item, width=92) or [""]; lines.append("")
    return "\n".join(lines).rstrip() + "\n"
def cmd_scan(args) -> int:
    data = {"agents": similar("agent", args.text, args.text)[:8],
            "skills": similar("skill", args.text, args.text)[:8],
            "advice": "reuse similar items first"}
    print(json.dumps(data, ensure_ascii=False, indent=2)); return 0
def cmd_inspect(args) -> int:
    text = args.text or " ".join([args.agents, args.skills])
    data = {"agents": similar("agent", text, text), "skills": similar("skill", text, text)}
    print(json.dumps(data, ensure_ascii=False, indent=2)); return 0

def cmd_check(args) -> int:
    if args.kind:
        hits = similar(args.kind, args.name, args.purpose)
        data = {"kind": args.kind, "name": slug(args.name),
                "decision": "reuse_or_refine" if hits else "create",
                "similar": hits}
        print(json.dumps(data, ensure_ascii=False, indent=2)); return 0
    data = duplicate_report(); print(json.dumps(data, ensure_ascii=False, indent=2))
    return 2 if data["issues"] else 0
def purpose(args) -> str:
    return args.purpose or args.mission or args.description
def create(kind: str, args) -> int:
    name = slug(args.name); job = purpose(args)
    need_approve(args); block_if_duplicate(kind, name, job, args.force)
    if kind == "agent":
        path = lib.find_codex() / "agents" / f"{name}.toml"; text = agent_text(name, job)
    else:
        path = lib.find_codex() / "skills" / name / "SKILL.md"; text = skill_body(name, job, args.domain)
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    registry({"kind": kind, "name": name, "purpose": job, "reason": args.reason})
    print(json.dumps({"created": str(path.relative_to(lib.root_dir()))}, ensure_ascii=False)); return 0
def cmd_create_agent(args) -> int: return create("agent", args)
def cmd_create_skill(args) -> int: return create("skill", args)
def cmd_create(args) -> int: return create(args.kind, args)
def cmd_add_downstream(args) -> int:
    need_approve(args); p = lib.find_codex() / "state" / "event_policy.json"
    data = lib.read_json(p, {}); rules = data.setdefault("custom_downstream", [])
    rule = {"after_stage": args.after_stage, "stage": args.stage,
            "agent": slug(args.agent), "title": args.title,
            "keywords": [x for x in args.keywords.split(",") if x]}
    if rule not in rules: rules.append(rule)
    lib.write_json(p, data); print(json.dumps(rule, ensure_ascii=False, indent=2)); return 0
def add_common(s):
    s.add_argument("--name", required=True); s.add_argument("--purpose", default="")
    s.add_argument("--description", default=""); s.add_argument("--mission", default="")
    s.add_argument("--reason", default=""); s.add_argument("--approve", action="store_true")
    s.add_argument("--force", action="store_true"); s.add_argument("--domain", default="general")
def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("scan"); sc.add_argument("--text", required=True); sc.add_argument("--for-ai", action="store_true")
    ins = sub.add_parser("inspect"); ins.add_argument("--text", default="")
    ins.add_argument("--agents", default=""); ins.add_argument("--skills", default="")
    ins.add_argument("--for-ai", action="store_true")
    ch = sub.add_parser("check"); ch.add_argument("kind", choices=["agent", "skill"], nargs="?")
    ch.add_argument("--name", default=""); ch.add_argument("--purpose", default="")
    ch.add_argument("--for-ai", action="store_true")
    cr = sub.add_parser("create"); cr.add_argument("kind", choices=["agent", "skill"]); add_common(cr)
    add_common(sub.add_parser("create-agent")); add_common(sub.add_parser("create-skill"))
    ds = sub.add_parser("add-downstream"); ds.add_argument("--agent", required=True)
    ds.add_argument("--stage", required=True); ds.add_argument("--after-stage", default="implement")
    ds.add_argument("--title", required=True); ds.add_argument("--keywords", default="")
    ds.add_argument("--reason", default=""); ds.add_argument("--approve", action="store_true")
    args = p.parse_args(); return globals()["cmd_" + args.cmd.replace("-", "_")](args)
if __name__ == "__main__":
    raise SystemExit(main())
