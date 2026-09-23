#!/usr/bin/env python3
"""test_lint.py: regression tests for lint_post.py (the skill's CI).

Every past review correction that lint can catch has a fixture in tests/fixtures.
A fixture must produce exactly the expected hit categories. When you add a lint
rule, add a fixture and an entry in tests/expected.json in the same change.

Usage: python3 .claude/skills/zenn-post-review/scripts/test_lint.py
"""
import json
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
LINT = SKILL / "scripts" / "lint_post.py"


def categories(path):
    out = subprocess.run([sys.executable, str(LINT), str(path)], capture_output=True, text=True).stdout
    return sorted({l.split("\t")[1] for l in out.splitlines() if l.startswith("L") and "\t" in l})


def main():
    expected = json.loads((SKILL / "tests" / "expected.json").read_text())
    fixtures = {p.stem for p in (SKILL / "tests" / "fixtures").glob("*.md")}
    failed = 0
    for name in sorted(fixtures | set(expected)):
        if name not in fixtures or name not in expected:
            print(f"FAIL {name}: fixture and expected.json out of sync")
            failed += 1
            continue
        got, want = categories(SKILL / "tests" / "fixtures" / f"{name}.md"), sorted(set(expected[name]))
        ok = got == want
        failed += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {name}: got {got}, want {want}")
    print(f"{len(fixtures) - failed}/{len(fixtures)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
