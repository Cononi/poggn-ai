#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, json, re
from pathlib import Path
import lib

SKIP = {"index.html"}


def docs_dir() -> Path:
    return lib.root_dir() / "docs"


def md_files() -> list[Path]:
    root = docs_dir()
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.md") if p.name not in SKIP)


def title(path: Path, text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").title()


def slug(path: Path) -> str:
    rel = path.relative_to(docs_dir()).with_suffix("")
    return re.sub(r"[^A-Za-z0-9가-힣_-]+", "-", str(rel)).strip("-")


def inline(value: str) -> str:
    value = html.escape(value)
    value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    return value


def md_to_html(text: str) -> str:
    out: list[str] = []; in_code = False; code: list[str] = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            if in_code:
                out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
                code = []; in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code.append(line); continue
        if not line:
            out.append(""); continue
        if line.startswith("### "):
            out.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.startswith("- "):
            out.append(f"<p class='li'>• {inline(line[2:])}</p>")
        else:
            out.append(f"<p>{inline(line)}</p>")
    return "\n".join(out)


def build() -> Path:
    docs = []
    for path in md_files():
        text = path.read_text(encoding="utf-8")
        docs.append({"id": slug(path), "path": str(path.relative_to(docs_dir())),
                     "title": title(path, text), "text": text,
                     "html": md_to_html(text)})
    lang = lib.language(); name = "Codex 위키" if lang == "ko" else "Codex Wiki"
    search = "검색" if lang == "ko" else "Search"
    nav = "문서" if lang == "ko" else "Docs"
    sections = "\n".join(
        f"<article id='{d['id']}' data-title='{html.escape(d['title'].lower())}' "
        f"data-text='{html.escape(d['text'].lower())}'>"
        f"<div class='path'>{html.escape(d['path'])}</div>{d['html']}</article>" for d in docs)
    items = "\n".join(
        f"<a href='#{d['id']}' data-title='{html.escape(d['title'].lower())}' "
        f"data-text='{html.escape(d['text'].lower())}'>{html.escape(d['title'])}"
        f"<small>{html.escape(d['path'])}</small></a>" for d in docs)
    data = json.dumps([{"id": d["id"], "title": d["title"], "text": d["text"][:2000]}
                       for d in docs], ensure_ascii=False)
    html_text = f"""<!doctype html>
<html lang='{lang}'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>{name}</title>
<style>
body{{margin:0;font-family:system-ui,Arial,sans-serif;background:#f7f7f8;color:#18181b}}
header{{position:sticky;top:0;background:#111827;color:white;padding:14px 18px;z-index:2}}
.layout{{display:grid;grid-template-columns:310px 1fr;min-height:100vh}}
aside{{border-right:1px solid #ddd;background:white;padding:14px;position:sticky;top:58px;height:calc(100vh - 58px);overflow:auto}}
main{{padding:24px;max-width:980px}}
input{{width:100%;padding:10px;border:1px solid #bbb;border-radius:8px;box-sizing:border-box}}
a{{display:block;color:#111827;text-decoration:none;padding:9px;border-radius:8px;margin:4px 0}}
a:hover{{background:#eef2ff}}small{{display:block;color:#666;font-size:12px;margin-top:3px}}
article{{background:white;border:1px solid #e5e7eb;border-radius:12px;padding:22px;margin-bottom:18px}}
.path{{color:#6b7280;font-size:12px;margin-bottom:8px}}pre{{background:#111827;color:#f9fafb;padding:12px;border-radius:8px;overflow:auto}}
code{{background:#eef2ff;padding:2px 4px;border-radius:4px}}.li{{margin-left:12px}}
@media(max-width:850px){{.layout{{display:block}}aside{{position:relative;top:0;height:auto}}}}
</style>
</head>
<body>
<header><strong>{name}</strong></header>
<div class='layout'>
<aside><label>{search}<input id='q' placeholder='{search}'></label><h3>{nav}</h3>{items}</aside>
<main>{sections}</main>
</div>
<script>
const docs = {data};
const q = document.getElementById('q');
const links = [...document.querySelectorAll('aside a')];
const articles = [...document.querySelectorAll('article')];
q.addEventListener('input', () => {{
  const v = q.value.toLowerCase().trim();
  for (const el of [...links, ...articles]) {{
    const ok = !v || el.dataset.title.includes(v) || el.dataset.text.includes(v);
    el.style.display = ok ? '' : 'none';
  }}
}});
</script>
</body>
</html>
"""
    out = docs_dir() / "index.html"; out.write_text(html_text, encoding="utf-8"); return out


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    args = p.parse_args()
    if args.cmd == "build":
        print(build()); return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
