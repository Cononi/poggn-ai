#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shutil, subprocess, sys, textwrap
from pathlib import Path
import lib

EFFORT = {
    "architecture": "high", "backend": "medium", "database": "medium",
    "devops": "medium", "docs": "low", "frontend": "medium",
    "git": "medium", "integration": "medium", "performance": "medium",
    "qa": "medium", "refactor": "high", "security": "high",
    "test": "medium", "test_writer": "medium", "test_runner": "medium",
    "capability_manager": "high",
}
MODEL = "gpt-5.3-codex-spark"


def state_path() -> Path:
    return lib.find_codex() / "state" / "language.json"


def template_path() -> Path:
    return lib.find_codex() / "templates" / "i18n.json"


def read_lang() -> str:
    return lib.read_json(state_path(), {"language": "ko"}).get("language", "ko")


def templates() -> dict:
    return lib.read_json(template_path(), {})


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def skill_text(name: str, desc: str, body: list[str]) -> list[str]:
    lines = ["---", f"name: {name}", f"description: {desc}", "---", "", f"# {name}", ""]
    for item in body:
        if item.startswith("$") or item.startswith("예:") or item.startswith("Example:"):
            lines += ["```text", item, "```", ""]
        else:
            lines += textwrap.wrap(item, width=92) or [""]
            lines.append("")
    return lines


def nicknames(name: str) -> list[str]:
    safe = name.replace("_", "-")
    raw = [safe, f"{safe}-worker", f"{safe}-lane",
           f"{safe}-task", f"{safe}-check", f"{safe}-flow"]
    out = []
    for item in raw:
        if item not in out:
            out.append(item)
    return out


def agent_text(name: str, desc: str, instruction: str) -> str:
    common = [instruction, "Stay inside the assigned TASK scope.",
              "Report changed files, tests, risks, and next steps.",
              "Use TASK skills automatically when they are provided."]
    if read_lang() == "ko":
        common = [instruction, "지정된 TASK 범위를 넘지 않습니다.",
                  "변경 파일, 테스트, 위험, 다음 단계를 보고합니다.",
                  "TASK에 skill이 있으면 자동으로 사용합니다."]
    body = "\n".join(common)
    names = ", ".join(f'"{x}"' for x in nicknames(name))
    return (f'name = "{name}"\n'
            f'description = "{desc}"\n'
            f'nickname_candidates = [{names}]\n'
            f'model = "{MODEL}"\n'
            f'model_reasoning_effort = "{EFFORT.get(name, "medium")}"\n'
            f'developer_instructions = """\n{body}\n"""\n')




def render_skill_templates(lang: str) -> bool:
    root = lib.root_dir()
    src = lib.find_codex() / "templates" / "skills" / lang
    dst = root / ".codex" / "skills"
    if not src.exists():
        return False
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        elif item.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
    return True

def render_docs(lang: str) -> None:
    root = lib.root_dir()
    src = lib.find_codex() / "templates" / "docs" / lang
    dst = root / "docs"
    if not src.exists():
        return
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    script = lib.find_codex() / "script" / "codex_wiki.py"
    if script.exists():
        subprocess.run([sys.executable, str(script), "build"], cwd=str(root), check=False)

def render(lang: str) -> None:
    root = lib.root_dir()
    data = templates().get(lang, {"files": {}, "skills": {}, "agents": {}})
    for rel, lines in data.get("files", {}).items():
        write_lines(root / rel, lines)
    if not render_skill_templates(lang):
        for name, value in data.get("skills", {}).items():
            path = root / ".codex" / "skills" / name / "SKILL.md"
            write_lines(path, skill_text(name, value[0], value[1]))
    for name, value in data.get("agents", {}).items():
        path = root / ".codex" / "agents" / f"{name}.toml"
        path.write_text(agent_text(name, value[0], value[1]), encoding="utf-8")
    try:
        import codex_wiki
        codex_wiki.build()
    except Exception:
        pass
    render_docs(lang)


def set_lang(lang: str) -> None:
    lib.write_json(state_path(), {"language": lang, "updated_at": lib.now()})
    render(lang)


def cmd_status(args) -> int:
    print(read_lang()); return 0


def cmd_set(args) -> int:
    set_lang(args.language); print(args.language); return 0


def cmd_render(args) -> int:
    render(read_lang()); print(read_lang()); return 0


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] in {"ko", "en"}:
        set_lang(sys.argv[1]); print(sys.argv[1]); return 0
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("set"); s.add_argument("language", choices=["ko", "en"])
    sub.add_parser("status"); sub.add_parser("render")
    p.add_argument("direct_language", nargs="?", choices=["ko", "en"])
    args = p.parse_args()
    if args.direct_language and not args.cmd:
        set_lang(args.direct_language); print(args.direct_language); return 0
    if args.cmd == "set": return cmd_set(args)
    if args.cmd == "render": return cmd_render(args)
    return cmd_status(args)


if __name__ == "__main__":
    raise SystemExit(main())
