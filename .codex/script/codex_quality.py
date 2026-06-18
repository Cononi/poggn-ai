#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, subprocess
from pathlib import Path
import lib

SRC = {".java", ".kt", ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs"}
FRONT = {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}
SKIP = {".git", ".codex-state", ".worktrees", "node_modules",
        "dist", "build", ".next", ".venv", "venv", "__pycache__"}
CODEX_INTERNAL = {".codex/script", ".codex/tests", ".codex/hooks"}
FRONT_HINT = {"app", "pages", "components", "features", "frontend", "ui", "src"}
SECRET_RX = [
    ("private-key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("openai-key", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
    ("generic-secret", re.compile(r"(?i)(token|secret|password)\s*[:=]\s*['\"]?[^'\"\s]{12,}")),
]


def run(cmd: list[str], cwd: Path) -> str:
    """Run a git helper command and return stdout on success."""
    p = subprocess.run(cmd, cwd=str(cwd), text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout.strip() if p.returncode == 0 else ""


def internal_untracked(cwd: Path) -> list[str]:
    """Return untracked internal .codex files for default quality checks."""
    rows = []
    for prefix in CODEX_INTERNAL:
        base = cwd / prefix
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(cwd).as_posix()
                tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel],
                                         cwd=str(cwd), stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
                if tracked.returncode:
                    rows.append(rel)
    return rows


def changed(cwd: Path, staged: bool, base: str) -> list[str]:
    """Return changed and untracked paths relevant to quality analysis."""
    if staged:
        out = run(["git", "diff", "--cached", "--name-only"], cwd)
    elif base:
        out = run(["git", "diff", "--name-only", f"{base}..HEAD"], cwd)
    else:
        out = run(["git", "diff", "--name-only", "HEAD"], cwd)
    names = [x for x in out.splitlines() if x.strip()]
    if staged or base:
        return names
    extra = run(["git", "ls-files", "--others", "--exclude-standard"], cwd)
    names.extend(x for x in extra.splitlines() if x.strip())
    names.extend(internal_untracked(cwd))
    return sorted(dict.fromkeys(names))


def skipped(path: Path, include_codex: bool) -> bool:
    """Return whether a path is outside the active quality scan scope."""
    parts = path.parts
    if ".codex" in parts and not include_codex:
        return True
    if ".codex" in parts and include_codex:
        rel = path.as_posix()
        return not any(rel.startswith(prefix + "/") for prefix in CODEX_INTERNAL)
    return any(part in SKIP for part in parts)


def all_files(cwd: Path, include_codex: bool = False) -> list[str]:
    """Return all source files visible to the selected quality scope."""
    rows = []
    for p in cwd.rglob("*"):
        rel_path = p.relative_to(cwd)
        if skipped(rel_path, include_codex):
            continue
        if p.is_file() and p.suffix in SRC | FRONT:
            rows.append(str(rel_path))
    return rows


def wanted(path: str, include_codex: bool = False) -> bool:
    """Return whether a path has a source suffix and is not skipped."""
    p = Path(path)
    return p.suffix in SRC | FRONT and not skipped(p, include_codex)


def read(cwd: Path, rel: str) -> str:
    """Read a file defensively for quality analysis."""
    try:
        return (cwd / rel).read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""


def issue(kind: str, severity: str, path: str, msg: str) -> dict:
    """Build a normalized quality issue record."""
    return {"kind": kind, "severity": severity, "path": path, "message": msg}


def repeated(lines: list[str]) -> int:
    """Return a simple repeated-line score for duplication detection."""
    seen: dict[str, int] = {}
    for line in lines:
        s = re.sub(r"\s+", " ", line.strip())
        if len(s) < 28 or s.startswith(("import ", "//", "#", "*")):
            continue
        seen[s] = seen.get(s, 0) + 1
    return sum(v - 2 for v in seen.values() if v > 2)


def is_frontend(rel: str, text: str) -> bool:
    """Return whether a file should receive frontend-specific checks."""
    p = Path(rel)
    parts = {x.lower() for x in p.parts}
    if p.suffix in {".jsx", ".tsx", ".vue", ".svelte"}:
        return True
    if parts & FRONT_HINT and p.suffix in FRONT:
        return True
    return bool(re.search(r"from ['\"]react|<([A-Z][A-Za-z0-9]*|div|span|button)\b", text))


def has_jsx(text: str) -> bool:
    """Return whether text appears to contain JSX markup."""
    return bool(re.search(r"<([A-Z][A-Za-z0-9]*|div|span|button|section)\b", text))


def frontend_checks(rel: str, text: str, args) -> list[dict]:
    """Return frontend quality issues for typed UI boundaries."""
    p = Path(rel); lines = text.splitlines(); out = []
    if not is_frontend(rel, text):
        return out
    if p.suffix in {".js", ".jsx"}:
        out.append(issue("frontend-tsx-required", "error", rel,
                         "React frontend must use .ts or .tsx, not JS/JSX"))
    if p.suffix == ".ts" and has_jsx(text):
        out.append(issue("frontend-tsx", "error", rel,
                         "JSX must live in .tsx files"))
    if p.suffix in {".tsx", ".vue", ".svelte"} and len(lines) > args.front_lines:
        out.append(issue("frontend-size", "error", rel,
                         f"component file has {len(lines)} lines"))
    lower = "/" + rel.lower()
    if re.search(r"/(page|screen|view)\.", lower) and len(lines) > getattr(args, "page_lines", 120):
        out.append(issue("frontend-page", "error", rel,
                         "page or screen must compose smaller components"))
    if re.search(r":\s*any\b|as\s+any\b", text):
        out.append(issue("typescript-any", "error", rel,
                         "avoid any; define props, DTO, and event types"))
    if len(re.findall(r"useState\s*\(", text)) > getattr(args, "state_limit", 6):
        out.append(issue("state-complexity", "warn", rel,
                         "split state or extract a feature hook"))
    if re.search(r"useEffect\s*\([^)]*(fetch|axios)|\b(fetch|axios)\s*\(", text, re.S):
        out.append(issue("api-in-component", "warn", rel,
                         "move API calls to a typed client or service"))
    if len(re.findall(r"className=\"([^\"]{12,})\"", text)) > getattr(args, "style_limit", 8):
        out.append(issue("style-complexity", "warn", rel,
                         "move repeated visual intent to reusable components"))
    if len(re.findall(r"function\s+[A-Z][A-Za-z0-9]*|const\s+[A-Z][A-Za-z0-9]*\s*=", text)) > 3:
        out.append(issue("component-count", "warn", rel,
                         "keep one main component and extract siblings"))
    return out


def previous_doc(lines: list[str], idx: int) -> bool:
    """Return whether the previous non-empty line is a doc comment."""
    j = idx - 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    if j < 0:
        return False
    prev = lines[j].strip()
    return prev.startswith(("/**", "///", "//", "#")) or prev.endswith("*/")


def python_docstring(lines: list[str], idx: int) -> bool:
    """Return whether a Python function starts with a docstring."""
    base = len(lines[idx]) - len(lines[idx].lstrip())
    triple_single = "'" * 3
    for line in lines[idx + 1:idx + 5]:
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        return indent > base and (stripped.startswith(chr(34) * 3) or
                                  stripped.startswith(triple_single))
    return False


def doc_comment_checks(rel: str, text: str) -> list[dict]:
    """Return public contract documentation warnings."""
    p = Path(rel); lines = text.splitlines(); out = []
    if p.suffix not in SRC:
        return out
    for idx, line in enumerate(lines):
        stripped = line.strip()
        needs_doc = False
        if p.suffix in {".java", ".kt"}:
            needs_doc = bool(re.match(r"public\s+(class|interface|enum|record)\b", stripped))
            needs_doc = needs_doc or bool(re.match(r"public\s+.*\w+\s*\([^)]*\)\s*", stripped))
        elif p.suffix in {".ts", ".tsx", ".js", ".jsx"}:
            needs_doc = bool(re.match(r"export\s+(default\s+)?(async\s+)?"
                                      r"(function|class|interface|type|const)\b", stripped))
        elif p.suffix == ".py":
            m = re.match(r"(class|def)\s+([A-Za-z][A-Za-z0-9_]*)\b", stripped)
            needs_doc = bool(m and not m.group(2).startswith("_"))
        if not needs_doc:
            continue
        has_doc = python_docstring(lines, idx) if p.suffix == ".py" else previous_doc(lines, idx)
        if not has_doc:
            out.append(issue("doc-comment", "warn", rel,
                             f"public/exported symbol near line {idx + 1} needs doc comment"))
    return out


def analyze_file(cwd: Path, rel: str, args) -> list[dict]:
    """Return all quality issues for one file."""
    text = read(cwd, rel)
    if not text:
        return []
    lines = text.splitlines(); out = []
    if len(lines) > args.max_lines:
        out.append(issue("file-size", "error", rel, f"file has {len(lines)} lines"))
    score = repeated(lines)
    if score >= args.repeat_limit:
        out.append(issue("duplicate", "error", rel, f"repeat score {score}"))
    if any("TODO" in x or "FIXME" in x for x in lines):
        out.append(issue("todo", "warn", rel, "TODO or FIXME remains"))
    for name, rx in SECRET_RX:
        if rx.search(text):
            out.append(issue("secret", "error", rel, name))
    out.extend(doc_comment_checks(rel, text))
    out.extend(frontend_checks(rel, text, args))
    return out


def analyze(args) -> dict:
    """Run quality analysis for the requested file scope."""
    cwd = Path(args.cwd).resolve() if args.cwd else lib.root_dir()
    files = all_files(cwd, args.include_codex) if args.all else changed(cwd, args.staged, args.base)
    files = sorted({x for x in files if wanted(x, args.include_codex)})
    issues = []
    for rel in files:
        issues.extend(analyze_file(cwd, rel, args))
    errors = sum(1 for x in issues if x["severity"] == "error")
    warns = sum(1 for x in issues if x["severity"] == "warn")
    return {"files": len(files), "errors": errors, "warnings": warns,
            "issues": issues[:100]}


def main() -> int:
    """Parse CLI arguments and return quality gate status."""
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    for name in ["analyze", "gate", "frontend"]:
        s = sub.add_parser(name); s.add_argument("--cwd", default="")
        s.add_argument("--staged", action="store_true"); s.add_argument("--all", action="store_true")
        s.add_argument("--include-codex", action="store_true")
        s.add_argument("--base", default=""); s.add_argument("--strict", action="store_true")
        s.add_argument("--for-ai", action="store_true")
        s.add_argument("--max-lines", type=int, default=200)
        s.add_argument("--front-lines", "--frontend-lines", dest="front_lines", type=int, default=160)
        s.add_argument("--page-lines", type=int, default=120)
        s.add_argument("--repeat-limit", type=int, default=6)
        s.add_argument("--state-limit", type=int, default=6)
        s.add_argument("--style-limit", type=int, default=8)
    args = p.parse_args(); data = analyze(args)
    if args.cmd == "frontend":
        data["issues"] = [x for x in data["issues"] if x["kind"].startswith("frontend")
                          or x["kind"] in {"typescript-any", "state-complexity",
                                            "api-in-component", "style-complexity",
                                            "component-count"}]
    print(json.dumps(data, ensure_ascii=False, indent=2))
    fail = data["errors"] or (args.strict and data["warnings"])
    return 2 if args.cmd == "gate" and fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
