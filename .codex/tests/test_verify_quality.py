#!/usr/bin/env python3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "script"))


def test_verify_and_quality_include_untracked_internal_files(tmp_path):
    import subprocess
    import codex_quality
    import codex_verify

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, stdout=subprocess.PIPE)
    rel = ".codex/script/new_gate.py"
    path = tmp_path / rel
    path.parent.mkdir(parents=True)
    path.write_text('def new_gate():\n    """Return marker."""\n    return 1\n')

    class Args:
        cwd = str(tmp_path)
        all = False
        staged = False
        base = ""
        max_lines = 200
        front_lines = 160
        page_lines = 120
        repeat_limit = 6
        state_limit = 6
        style_limit = 8
        include_codex = True

    assert rel in codex_verify.changed_files(Args())
    data = codex_quality.analyze(Args())
    assert data["files"] == 1
