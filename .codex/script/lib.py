#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess
from datetime import datetime, timezone
from pathlib import Path
try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None


def find_codex(start: Path | None = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for item in (cur, *cur.parents):
        hit = item / ".codex"
        if hit.is_dir():
            return hit
    raise SystemExit(".codex not found")


def root_dir() -> Path:
    return find_codex().parent


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON: {path}: {exc}")


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")


def locale() -> dict:
    path = find_codex() / "state" / "locale.json"
    return read_json(path, {"timezone": "Asia/Seoul", "country": "KR"})


def timezone_obj():
    name = locale().get("timezone", "Asia/Seoul")
    if ZoneInfo:
        try:
            return ZoneInfo(name)
        except Exception:
            pass
    return timezone.utc


def now() -> str:
    return datetime.now(timezone_obj()).isoformat(timespec="seconds")


def today() -> str:
    return now()[:10]


def run(args: list[str], cwd: Path | None = None, check: bool = False):
    proc = subprocess.run(
        args,
        cwd=str(cwd or Path.cwd()),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and proc.returncode:
        raise SystemExit(proc.stderr.strip() or proc.stdout.strip())
    return proc


def has_cmd(name: str) -> bool:
    from shutil import which
    return which(name) is not None


def safe_slug(value: str) -> str:
    keep = []
    for ch in value.replace("/", "-").replace(" ", "-"):
        if ch.isalnum() or ch in "._-":
            keep.append(ch.lower())
    return "".join(keep).strip("-._") or "task"


def language() -> str:
    data = read_json(find_codex() / "state" / "language.json", {"language": "ko"})
    return data.get("language", "ko")
