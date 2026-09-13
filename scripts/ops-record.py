#!/usr/bin/env python3
"""ops-record.py — レビューループの記録（run-log.md、agent-state.md）と commit/push を 1 コマンドで行う。

使い方:
    python3 scripts/ops-record.py --slug S --run N --trigger cron --sha 02357e3ca963 --check PASS \
        --fact "0/0/0/0" --style "0/1/0" --writer "changed true / addressed [S-01] / chars 5044 → 4468" \
        --result stop --harness "なし" [--glossary "added [...] / fixed [...]"] [--decision-file PATH] [--commit "Review stop (run N): title"] [--no-push]

- run-log.md の末尾に Run ブロックを追記する（時刻は JST の現在時刻）
- agent-state.md の `## Last run` を書き換える。--decision-file があれば `## Needs human decision` の先頭にその内容を足す。
  `## Next run` は result=stop なら「<slug> は人判断待ち」、pass なら「なし（<slug> は公開可）」、continue なら「<slug> の次の Run」
- --commit があれば articles/<slug>.md と ops/ を add して commit し、--no-push が無ければ push する
- 最後の行に JSON 1 行: {"run_log": true, "agent_state": true, "committed": "<sha>|null", "pushed": bool, "error": "..."}
標準ライブラリのみ。
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
JST = datetime.timezone(datetime.timedelta(hours=9))
TRIGGER_LABEL = {
    "telegram": "telegram（人の指示）",
    "cron": "cron（isolated セッションで起動された）",
    "tech-watch": "tech-watch（毎朝ジョブ内）",
    "manual": "manual",
}


def replace_section(text, heading, body_lines):
    """`## <heading>` 節の本文を body_lines に置き換える。節が無ければ末尾に足す。"""
    lines = text.split("\n")
    start = next((i for i, l in enumerate(lines) if l.strip() == "## " + heading), None)
    if start is None:
        return text.rstrip("\n") + "\n\n## " + heading + "\n\n" + "\n".join(body_lines) + "\n"
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    new = lines[: start + 1] + [""] + body_lines + [""] + lines[end:]
    return "\n".join(new)


def prepend_to_section(text, heading, block_lines):
    lines = text.split("\n")
    start = next((i for i, l in enumerate(lines) if l.strip() == "## " + heading), None)
    if start is None:
        return replace_section(text, heading, block_lines)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    body = lines[start + 1:end]
    # 「（なし）」のプレースホルダーは消す
    body = [l for l in body if l.strip() not in ("- （なし）", "-（なし）")]
    new = lines[: start + 1] + [""] + block_lines + [""] + [l for l in body if l.strip() != ""] + [""] + lines[end:]
    return "\n".join(new)


def git(args, check=True):
    return subprocess.run(["git", "-C", str(REPO)] + args, capture_output=True, text=True, check=check)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--run", required=True, type=int)
    ap.add_argument("--trigger", required=True, choices=list(TRIGGER_LABEL))
    ap.add_argument("--sha", required=True, help="sha256sum の先頭 12 桁")
    ap.add_argument("--check", required=True, help='"PASS" または "FAIL (failures を , 区切り)"')
    ap.add_argument("--fact", required=True, help='"Critical/Must fix/Nice/unreachable" 例: 0/3/2/1。無効なら "無効: 理由"')
    ap.add_argument("--style", required=True, help='"Critical/Must fix/Nice" 例: 0/10/0。無効なら "無効: 理由"')
    ap.add_argument("--writer", default="呼んでいない")
    ap.add_argument("--autofix", default="", help='article-fix.py の要約 例: "glossary 36 / banned 1 / markdown 11 / applied [S-03]"')
    ap.add_argument("--result", required=True, choices=["pass", "continue", "stop"])
    ap.add_argument("--harness", default="なし")
    ap.add_argument("--glossary", default="", help='glossary-update.py の要約 例: "added [test suite→テストスイート] / fixed [] / skipped 2"')
    ap.add_argument("--decision-file", default=None)
    ap.add_argument("--commit", default=None)
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()

    out = {"run_log": False, "agent_state": False, "committed": None, "pushed": False}
    now = datetime.datetime.now(JST).strftime("%Y-%m-%d %H:%M JST")

    def fmt(label, v, names):
        if v.startswith("無効"):
            return f"{label}: {v}"
        parts = [x.strip() for x in v.split("/")]
        if len(parts) != len(names):
            return f"{label}: {v}"
        # "Critical 0 / Must fix 2" のようにラベル付きで渡されても二重にしない
        parts = [re.sub(r"^(Critical|Must fix|Nice|unreachable)\s*", "", x).strip() for x in parts]
        return f"{label}: " + " / ".join(f"{n} {x}" for n, x in zip(names, parts))

    fact_line = fmt("fact", args.fact, ["Critical", "Must fix", "Nice", "unreachable"])
    style_line = fmt("style", args.style, ["Critical", "Must fix", "Nice"])

    block = [
        f"## Run {args.run} ({now}) {args.slug}",
        f"- Trigger: {TRIGGER_LABEL[args.trigger]}",
        f"- article_sha: {args.sha}",
        f"- check: {args.check}",
    ]
    if args.autofix:
        block.append(f"- autofix: {args.autofix}")
    block += [f"- {fact_line}", f"- {style_line}"]
    if args.glossary:
        block.append(f"- glossary: {args.glossary}")
    block += [f"- writer: {args.writer}", f"- Result: {args.result}",
              f"- Harness change 候補: {args.harness}"]

    run_log = REPO / "ops" / "run-log.md"
    text = run_log.read_text(encoding="utf-8") if run_log.exists() else "# run-log\n"
    run_log.write_text(text.rstrip("\n") + "\n\n" + "\n".join(block) + "\n", encoding="utf-8")
    out["run_log"] = True

    state = REPO / "ops" / "agent-state.md"
    s = state.read_text(encoding="utf-8") if state.exists() else "# ops/agent-state.md\n"
    last = [f"- {now} / {args.slug} / Run {args.run} / {args.result}", f"- check: {args.check}",
            f"- {fact_line}", f"- {style_line}", f"- writer: {args.writer}"]
    s = replace_section(s, "Last run", last)
    if args.decision_file:
        dec = Path(args.decision_file).read_text(encoding="utf-8").rstrip("\n").split("\n")
        s = prepend_to_section(s, "Needs human decision", dec)
    nxt = {"stop": f"- {args.slug} は人判断待ち（Needs human decision を参照）",
           "pass": f"- なし（{args.slug} は公開可。公開は人が指示する）",
           "continue": f"- {args.slug} の Run {args.run + 1}（進行中）"}[args.result]
    s = replace_section(s, "Next run", [nxt])
    state.write_text(s, encoding="utf-8")
    out["agent_state"] = True

    if args.commit:
        try:
            git(["add", f"articles/{args.slug}.md", "ops/run-log.md", "ops/agent-state.md"])
            r = git(["commit", "-m", args.commit], check=False)
            if r.returncode != 0 and "nothing to commit" not in r.stdout + r.stderr:
                out["error"] = (r.stdout + r.stderr).strip()[-400:]
            else:
                out["committed"] = git(["rev-parse", "--short", "HEAD"]).stdout.strip()
                if not args.no_push:
                    r = git(["push"], check=False)
                    out["pushed"] = r.returncode == 0
                    if r.returncode != 0:
                        out["error"] = (r.stdout + r.stderr).strip()[-400:]
        except subprocess.CalledProcessError as e:
            out["error"] = (e.stdout + e.stderr).strip()[-400:]
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
