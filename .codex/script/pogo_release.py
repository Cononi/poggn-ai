#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
PROJECT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
GRADLE_VERSION = re.compile(r"^\s*version\s*=\s*[\"']([^\"']+)[\"']\s*$")


def run(args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)


def text_or_none(args: list[str]) -> str | None:
    proc = run(args)
    if proc.returncode:
        return None
    return proc.stdout.strip() or None


def default_project() -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", ROOT.name).strip("-") or "app"


def project_name(args: argparse.Namespace) -> str:
    project = args.project or default_project()
    if not PROJECT.fullmatch(project):
        raise SystemExit("project must match [A-Za-z0-9][A-Za-z0-9._-]*")
    return project


def project_path(args: argparse.Namespace) -> Path:
    value = args.path or "."
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit("--path must stay inside the repository") from exc
    return path


def display_path(path: Path) -> str:
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return str(path)
    return str(relative) or "."


def read_package_json(path: Path, out: list[str]) -> None:
    package_json = path / "package.json"
    if not package_json.exists():
        return
    try:
        version = json.loads(package_json.read_text(encoding="utf-8")).get("version")
        if version:
            out.append(f"{display_path(package_json)}:{version}")
    except Exception as exc:
        out.append(f"{display_path(package_json)}:invalid ({exc})")


def read_version_files(path: Path, out: list[str]) -> None:
    version_file = path / "VERSION"
    if version_file.exists():
        out.append(f"{display_path(version_file)}:{version_file.read_text(encoding='utf-8').strip()}")
    version_json = path / "version.json"
    if version_json.exists():
        try:
            data = json.loads(version_json.read_text(encoding="utf-8"))
            out.append(f"{display_path(version_json)}:{data.get('version', 'missing')}")
        except Exception as exc:
            out.append(f"{display_path(version_json)}:invalid ({exc})")


def read_gradle(path: Path, out: list[str]) -> None:
    for name in ("build.gradle", "build.gradle.kts"):
        gradle = path / name
        if not gradle.exists():
            continue
        try:
            for line in gradle.read_text(encoding="utf-8").splitlines():
                match = GRADLE_VERSION.match(line)
                if match:
                    out.append(f"{display_path(gradle)}:{match.group(1)}")
                    break
            else:
                out.append(f"{display_path(gradle)}:version missing")
        except Exception as exc:
            out.append(f"{display_path(gradle)}:invalid ({exc})")
    gradle_properties = path / "gradle.properties"
    if gradle_properties.exists():
        try:
            for line in gradle_properties.read_text(encoding="utf-8").splitlines():
                if line.startswith("version="):
                    out.append(f"{display_path(gradle_properties)}:{line.split('=', 1)[1].strip()}")
                    break
        except Exception as exc:
            out.append(f"{display_path(gradle_properties)}:invalid ({exc})")


def read_pom(path: Path, out: list[str]) -> None:
    pom = path / "pom.xml"
    if not pom.exists():
        return
    try:
        root = ET.fromstring(pom.read_text(encoding="utf-8"))
        namespace = ""
        if root.tag.startswith("{"):
            namespace = root.tag.split("}", 1)[0] + "}"
        version = root.findtext(f"{namespace}version")
        out.append(f"{display_path(pom)}:{version or 'version missing'}")
    except Exception as exc:
        out.append(f"{display_path(pom)}:invalid ({exc})")


def version_sources(path: Path) -> list[str]:
    out: list[str] = []
    read_package_json(path, out)
    read_version_files(path, out)
    read_gradle(path, out)
    read_pom(path, out)
    return out


def tag_for(project: str, version: str) -> str:
    if not SEMVER.fullmatch(version):
        raise SystemExit("version must be semver, for example 1.2.3 or 1.2.3-beta.1")
    return f"{project}-v{version}"


def validate_tag(project: str, tag: str) -> None:
    prefix = f"{project}-v"
    if not tag.startswith(prefix):
        raise SystemExit(f"tag must use project prefix: {prefix}<semver>")
    version = tag[len(prefix) :]
    if not SEMVER.fullmatch(version):
        raise SystemExit("tag must use semver: <project>-v<semver>")


def latest_project_tag(project: str) -> str | None:
    proc = run(["git", "tag", "--list", f"{project}-v*", "--sort=-version:refname"])
    if proc.returncode:
        return None
    tags = proc.stdout.splitlines()
    return tags[0] if tags else None


def add_scope_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", help="release project name; tag format is <project>-v<semver>")
    parser.add_argument("--path", help="project path inside the repository; defaults to repo root")


def status(args: argparse.Namespace) -> int:
    inside = text_or_none(["git", "rev-parse", "--is-inside-work-tree"])
    if inside != "true":
        print("Not a git worktree", file=sys.stderr)
        return 2
    project = project_name(args)
    path = project_path(args)
    print(f"project: {project}")
    print(f"path: {display_path(path)}")
    print("tag_policy: <project>-v<semver>")
    print(f"next_tag_example: {tag_for(project, '1.0.0')}")
    print(f"branch: {text_or_none(['git', 'branch', '--show-current']) or 'detached'}")
    print(f"head: {text_or_none(['git', 'rev-parse', '--short', 'HEAD']) or 'unknown'}")
    print(f"latest_project_tag: {latest_project_tag(project) or 'none'}")
    print(f"latest_repo_tag: {text_or_none(['git', 'describe', '--tags', '--abbrev=0']) or 'none'}")
    sources = version_sources(path)
    print("version_sources: " + (", ".join(sources) if sources else "none"))
    print("gh: " + (shutil.which("gh") or "not found"))
    return 0


def notes(args: argparse.Namespace) -> int:
    project = project_name(args)
    path = project_path(args)
    base = args.from_ref or latest_project_tag(project)
    target = args.to_ref or "HEAD"
    rev_range = f"{base}..{target}" if base else target
    cmd = ["git", "log", "--no-merges", "--pretty=format:- %s (%h)", rev_range, "--", display_path(path)]
    proc = run(cmd)
    if proc.returncode:
        print(proc.stderr.strip() or "Unable to collect git log", file=sys.stderr)
        return proc.returncode
    print(f"## 프로젝트\n\n- `{project}` ({display_path(path)})\n")
    print("## 요약\n")
    print("- 변경 내용을 확인하세요.\n")
    print("## 변경 사항\n")
    print(proc.stdout.strip() or "- 변경 commit 없음")
    print("\n## 검증\n")
    print("- `<command>`: NOT RUN")
    print("\n## 호환성 / 마이그레이션\n")
    print("- breaking change 여부: 확인 필요")
    print("- 설정 파일 변경 여부: 확인 필요")
    print("\n## 롤백\n")
    print(f"- 이전 project tag: {base or 'none'}")
    print("- 되돌릴 commit 또는 PR: 확인 필요")
    return 0


def create(args: argparse.Namespace) -> int:
    project = project_name(args)
    if args.version:
        args.tag = tag_for(project, args.version)
    if not args.tag:
        print("--tag or --version is required", file=sys.stderr)
        return 2
    validate_tag(project, args.tag)
    if not args.notes_file:
        print("--notes-file is required", file=sys.stderr)
        return 2
    if not Path(args.notes_file).exists():
        print(f"notes file not found: {args.notes_file}", file=sys.stderr)
        return 2
    cmd = ["gh", "release", "create", args.tag, "--notes-file", args.notes_file]
    cmd.extend(["--title", args.title or args.tag])
    if args.draft:
        cmd.append("--draft")
    if not args.execute:
        print("dry-run: " + " ".join(cmd))
        return 0
    if not shutil.which("gh"):
        print("gh not found", file=sys.stderr)
        return 127
    proc = run(cmd)
    if proc.stdout.strip():
        print(proc.stdout.strip())
    if proc.stderr.strip():
        print(proc.stderr.strip(), file=sys.stderr)
    return proc.returncode


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Pogo project-scoped release helper")
    sub = parser.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status")
    add_scope_args(s)
    s.set_defaults(fn=status)
    n = sub.add_parser("notes")
    add_scope_args(n)
    n.add_argument("--from", dest="from_ref")
    n.add_argument("--to", dest="to_ref")
    n.set_defaults(fn=notes)
    c = sub.add_parser("create")
    add_scope_args(c)
    c.add_argument("--tag")
    c.add_argument("--version", help="semver; converted to <project>-v<semver>")
    c.add_argument("--title")
    c.add_argument("--notes-file", required=True)
    c.add_argument("--draft", action="store_true")
    c.add_argument("--execute", action="store_true")
    c.set_defaults(fn=create)
    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
