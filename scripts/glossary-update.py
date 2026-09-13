#!/usr/bin/env python3
"""glossary-update.py — style reviewer の JSON `glossary` から定訳辞書（writing-rules.md「## 定訳（自動置換）」節）を更新する。

    python3 scripts/glossary-update.py <style.json> [--rules PATH] [--dry-run] [--json-only]

`glossary` の各要素は {"en": "...", "ja": "...", "action": "add" | "fix", "reason": "..."}。
- add: 未登録なら節の末尾に `- en → ja` を追記。既登録・「英語のままにする語」・大文字始まり（固有名詞）・空はスキップ
- fix: 既登録の右辺を ja に置き換える。未登録ならスキップ
最後の行に JSON {"changed", "added", "fixed", "skipped"} を出す。skipped は {"en", "reason"} の配列。
辞書の正本は VPS の ~/.openclaw/shared/knowledge/writing-rules.md（Andy がこのスクリプト経由でだけ書き換える）。
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_RULES = Path(os.path.expanduser("~/.openclaw/shared/knowledge/writing-rules.md"))
GLOSSARY_HEADING = "定訳（"
KEEP_HEADING = "英語のままにする語"


def section_bounds(lines, heading):
    """`## <heading>` で始まる節の (開始行, 終了行) を返す。終了行は次の `## ` の行番号（無ければ len）。"""
    start = next((i for i, l in enumerate(lines) if l.startswith("## ") and l[3:].strip().startswith(heading)), None)
    if start is None:
        return None, None
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return start, end


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("review_json")
    ap.add_argument("--rules", default=str(DEFAULT_RULES))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json-only", action="store_true")
    args = ap.parse_args()

    out = {"changed": False, "added": [], "fixed": [], "skipped": []}
    rules = Path(args.rules)
    if not rules.exists():
        out["error"] = f"rules file not found: {rules}"
        print(json.dumps(out, ensure_ascii=False))
        return 2
    try:
        review = json.loads(Path(args.review_json).read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        out["error"] = f"review json unreadable: {e}"
        print(json.dumps(out, ensure_ascii=False))
        return 2
    entries = review.get("glossary") or []
    if not isinstance(entries, list):
        entries = []

    text = rules.read_text(encoding="utf-8")
    lines = text.split("\n")
    g_start, g_end = section_bounds(lines, GLOSSARY_HEADING)
    if g_start is None:
        out["error"] = f"'## {GLOSSARY_HEADING}' section not found"
        print(json.dumps(out, ensure_ascii=False))
        return 2
    k_start, k_end = section_bounds(lines, KEEP_HEADING)
    keep = set()
    if k_start is not None:
        keep = {l[2:].strip().lower() for l in lines[k_start:k_end] if l.startswith("- ")}

    def existing():
        """辞書節の {en.lower(): 行番号}"""
        d = {}
        for i in range(g_start, g_end):
            l = lines[i]
            if l.startswith("- ") and "→" in l:
                d[l[2:].split("→", 1)[0].strip().lower()] = i
        return d

    for e in entries:
        en = str(e.get("en", "")).strip()
        ja = str(e.get("ja", "")).strip()
        action = str(e.get("action", "")).strip()
        key = en.lower()
        if not en or not ja or action not in ("add", "fix"):
            out["skipped"].append({"en": en, "reason": "incomplete entry"})
            continue
        if re.search(r"[^\x00-\x7F]", en) or "→" in en or "→" in ja:
            out["skipped"].append({"en": en, "reason": "en must be ASCII; no arrows"})
            continue
        idx = existing()
        if action == "add":
            if key in idx:
                out["skipped"].append({"en": en, "reason": "already in glossary"})
            elif key in keep or any(w in keep for w in key.split()):
                out["skipped"].append({"en": en, "reason": "listed as keep-English"})
            elif en[:1].isupper():
                out["skipped"].append({"en": en, "reason": "capitalized (proper noun?)"})
            else:
                # 節末尾の空行の手前に入れる
                insert_at = g_end
                while insert_at > g_start + 1 and lines[insert_at - 1].strip() == "":
                    insert_at -= 1
                lines.insert(insert_at, f"- {en} → {ja}")
                g_end += 1
                out["added"].append(f"{en} → {ja}")
        else:  # fix
            if key not in idx:
                out["skipped"].append({"en": en, "reason": "not in glossary (use add)"})
            else:
                i = idx[key]
                old = lines[i][2:].split("→", 1)[1].strip()
                if old == ja:
                    out["skipped"].append({"en": en, "reason": "same translation"})
                else:
                    lines[i] = f"- {en} → {ja}"
                    out["fixed"].append(f"{en}: {old} → {ja}")

    new_text = "\n".join(lines)
    out["changed"] = new_text != text
    if out["changed"] and not args.dry_run:
        rules.write_text(new_text, encoding="utf-8")
    if not args.json_only:
        print(f"{'DRY ' if args.dry_run else ''}{'CHANGED' if out['changed'] else 'NO CHANGE'}  added={len(out['added'])} fixed={len(out['fixed'])} skipped={len(out['skipped'])}")
        for a in out["added"]:
            print(f"  + {a}")
        for f in out["fixed"]:
            print(f"  ~ {f}")
        for s in out["skipped"]:
            print(f"  - {s['en']}: {s['reason']}")
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
