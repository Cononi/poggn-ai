#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
import lib


def path():
    return lib.find_codex() / "state" / "locale.json"


def read() -> dict:
    return lib.read_json(path(), {"country": "KR", "timezone": "Asia/Seoul"})


def cmd_status(args) -> int:
    data = read(); data["now"] = lib.now()
    print(json.dumps(data, ensure_ascii=False, indent=2)); return 0


def cmd_set(args) -> int:
    data = {"country": args.country, "timezone": args.timezone}
    lib.write_json(path(), data)
    out = {**data, "now": lib.now()}
    print(json.dumps(out, ensure_ascii=False, indent=2)); return 0


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("set"); s.add_argument("timezone"); s.add_argument("--country", default="KR")
    sub.add_parser("status")
    args = p.parse_args()
    return cmd_set(args) if args.cmd == "set" else cmd_status(args)


if __name__ == "__main__":
    raise SystemExit(main())
