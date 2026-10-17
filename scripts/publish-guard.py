#!/usr/bin/env python3
"""publish-guard.py — 前日以前の日付の記事を公開する push を止める（~/zenn-content/.git/hooks/pre-push から呼ぶ）。

git の pre-push は標準入力に `<local ref> <local sha> <remote ref> <remote sha>` を 1 行ずつ渡す。
push する範囲で変わった articles/YYYYMMDD-*.md のうち、日付が今日（JST）より前で、push 後に `published: true` のものについて:
- push 前は published: true でなかった（新しく公開する）→ 止める
- push 前から published: true で、Zenn で読めない（上限で弾かれた記事の再公開）→ 止める
読める記事の修正と、published: false に戻す push は通す。決まりは ~/.openclaw/workspace/scripts/zenn-published.py の先頭。
止めたら理由を stderr に出して exit 1。
"""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ZP_PATH = Path(os.environ.get("ZENN_PUBLISHED", Path.home() / ".openclaw/workspace/scripts/zenn-published.py"))
ZERO = "0" * 40


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)


def show(rev, path):
    r = git("show", f"{rev}:{path}")
    return r.stdout if r.returncode == 0 else ""


def blocked(zp, local, remote, day, user):
    rng = [remote, local] if remote != ZERO else ["--root", local]
    names = git("diff-tree", "-r", "--name-only", "--no-commit-id", *rng, "--", "articles/").stdout.split()
    out = []
    for path in names:
        slug = Path(path).stem
        if not path.endswith(".md") or not zp.is_past_day(slug, day):
            continue
        pub, _, title = zp.front(show(local, path))
        if not pub:
            continue
        if not (remote != ZERO and zp.front(show(remote, path))[0]):
            out.append(f"{slug}: 前日以前の記事を新しく公開する push")
        elif user and zp.check(user, slug, title).get("published") is False:
            out.append(f"{slug}: Zenn で読めない前日以前の記事の再公開")
    return out


def main():
    spec = importlib.util.spec_from_file_location("zp", ZP_PATH)
    zp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(zp)
    try:
        user = zp.USER_FILE.read_text().strip()
    except OSError:
        user = None
    day = zp.today()
    bad = []
    for line in sys.stdin:
        parts = line.split()
        if len(parts) == 4 and parts[1] != ZERO:
            bad += blocked(zp, parts[1], parts[3], day, user)
    if bad:
        print("publish-guard: 前日以前の日付の記事は公開しない（当日公開の決まり）。push を止めた:", file=sys.stderr)
        for b in bad:
            print("  " + b, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
