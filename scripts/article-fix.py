#!/usr/bin/env python3
"""article-fix.py — Tech Watch 記事の決定的な自動修正（writer を呼ぶ前に機械で直せるものを直す）。

使い方:
    python3 scripts/article-fix.py <slug> [--reviews a.json b.json ...] [--rules PATH] [--dry-run] [--json-only]

やること（順番どおり。frontmatter、コードブロック、インラインコード、URL、`>` 引用行、`## 今日の N 件` の一覧節（冒頭。次の `## ` 見出しまで）は触らない）:
1. エスケープされたバッククォート（\\`）を戻す
2. 引用ブロック末尾の「空の > 行 + > 出典名」をブロック外の「出典: 名前」に移す
3. writing-rules.md「## 定訳（自動置換）」の `english → 日本語` を単語境界で置換（小文字表記の語だけ。大文字始まりは固有名詞とみなして触らない）
4. writing-rules.md「## 効く の言い換え（自動置換）」の対を書いてある順に置換
5. --reviews で渡した review JSON の指摘に `replacement` があり、`quote` が本文に 1 回だけ現れるものを置換

出力: 人が読める行のあと、最後の行に JSON 1 行。終了コードは常に 0（検査と同じく、結果は JSON で伝える）。
標準ライブラリのみ。ネットワークに出ない。
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_RULES = Path(os.path.expanduser("~/.openclaw/shared/knowledge/writing-rules.md"))
PROTECT_RE = re.compile(r"(`[^`\n]*`|https?://[^\s)>\]」』]+)")
FINAL_LIST_RE = re.compile(r"^## 今日の\s*\d+\s*件")


def read_pairs(rules_path, heading):
    """`## <heading>` 節の `- a → b` 行を [(a, b), ...] で返す（書いてある順）。"""
    if not rules_path or not Path(rules_path).exists():
        return []
    pairs, inside = [], False
    for line in Path(rules_path).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().startswith(heading)
            continue
        if inside and line.startswith("- ") and "→" in line:
            a, b = line[2:].split("→", 1)
            pairs.append((a.strip(), b.strip()))
    return pairs


def read_items(rules_path, heading):
    if not rules_path or not Path(rules_path).exists():
        return []
    items, inside = [], False
    for line in Path(rules_path).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().startswith(heading)
            continue
        if inside and line.startswith("- "):
            items.append(line[2:].strip())
    return items


LIST_SENTINEL = "<!-- `TECH-WATCH-LIST-SENTINEL` -->"  # 一覧節の位置を示す仮の行。インラインコードなので置換の対象外


def split_article(text):
    """frontmatter, 本文行, 一覧節（「## 今日の N 件」から次の `## ` 見出しの手前まで）に分ける。
    一覧節は冒頭（導入の直後）にあるので、本文行の中では LIST_SENTINEL 1 行で場所を示す。"""
    fm = ""
    body = text
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            fm, body = text[: end + 5], text[end + 5:]
    lines = body.split("\n")
    idx = next((i for i, l in enumerate(lines) if FINAL_LIST_RE.match(l)), None)
    if idx is None:
        return fm, lines, []
    end = next((i for i in range(idx + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return fm, lines[:idx] + [LIST_SENTINEL] + lines[end:], lines[idx:end]


def join_article(fm, main_lines, list_lines):
    if LIST_SENTINEL in main_lines:
        i = main_lines.index(LIST_SENTINEL)
        main_lines = main_lines[:i] + list_lines + main_lines[i + 1:]
    return fm + "\n".join(main_lines)


def count_chars(lines):
    text = "\n".join(lines)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return len(re.sub(r"\s+", "", text))


def unescape_backticks(lines):
    n = 0
    out = []
    for l in lines:
        if "\\`" in l:
            n += l.count("\\`")
            l = l.replace("\\`", "`")
        out.append(l)
    return out, n


def move_quote_sources(lines):
    """引用ブロックが `>`（空）+ `> 出典名` で終わっていたら、ブロック外の `出典: 名前` に移す。"""
    out, n, i = [], 0, 0
    while i < len(lines):
        if lines[i].startswith(">"):
            j = i
            while j < len(lines) and lines[j].startswith(">"):
                j += 1
            block = lines[i:j]
            if (len(block) >= 3 and block[-2].strip() == ">"
                    and re.match(r"^>\s*\S", block[-1])):
                name = re.sub(r"^(出典|Source)\s*[:：]\s*", "", block[-1][1:].strip())
                if len(name) <= 40 and not re.search(r"[。.!?！？]$", name):
                    out.extend(block[:-2])
                    out.append("")
                    out.append("出典: " + name)
                    n += 1
                    i = j
                    continue
            out.extend(block)
            i = j
        else:
            out.append(lines[i])
            i += 1
    return out, n


def transform_prose(lines, fn):
    """コードブロック、`>` 行、インラインコード、URL を除いた文章部分だけに fn を適用する。fn は (text) -> (text, count)。"""
    out, total, in_fence = [], 0, False
    for l in lines:
        if l.strip().startswith("```"):
            in_fence = not in_fence
            out.append(l)
            continue
        if in_fence or l.startswith(">"):
            out.append(l)
            continue
        pieces = PROTECT_RE.split(l)
        for k in range(0, len(pieces), 2):
            pieces[k], c = fn(pieces[k])
            total += c
        out.append("".join(pieces))
    return out, total


def glossary_fn(pairs, keep):
    keep_l = {k.lower() for k in keep}
    ordered = sorted(((a, b) for a, b in pairs if a.lower() not in keep_l), key=lambda p: -len(p[0]))
    compiled = [(re.compile(r"(?<![A-Za-z0-9_\-])" + re.escape(a) + r"(?![A-Za-z0-9_\-])"), b) for a, b in ordered]
    hits = {}

    def fn(text):
        c = 0
        for rx, b in compiled:
            text, k = rx.subn("\x00" + b + "\x01", text)
            if k:
                c += k
                hits[rx.pattern] = hits.get(rx.pattern, 0) + k
        # 置換した日本語と隣の英単語の間の空白は詰める（記事は「Pythonクライアント」のように空白を入れない）
        text = re.sub(r"(?<=[A-Za-z0-9\x01]) \x00", "\x00", text)
        text = re.sub(r"\x01 (?=[A-Za-z0-9\x00])", "\x01", text)
        text = re.sub(r"(?<=[^\x00-\x7F]) \x00", "\x00", text)
        text = re.sub(r"\x01 (?=[^\x00-\x7F])", "\x01", text)
        return text.replace("\x00", "").replace("\x01", ""), c
    return fn, hits


def banned_fn(pairs):
    def fn(text):
        c = 0
        for a, b in pairs:
            k = text.count(a)
            if k:
                text = text.replace(a, b)
                c += k
        return text, c
    return fn


def apply_reviews(main_text, review_paths):
    applied, skipped = [], []
    for p in review_paths:
        try:
            d = json.loads(Path(p).read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            skipped.append({"id": Path(p).name, "reason": "unreadable: %s" % e})
            continue
        for sev in ("critical", "must_fix"):
            for f in d.get(sev) or []:
                fid = f.get("id", "?")
                rep = f.get("replacement")
                quote = f.get("quote") or ""
                if not rep:
                    skipped.append({"id": fid, "reason": "no replacement"})
                    continue
                k = main_text.count(quote) if quote else 0
                if k == 0:
                    skipped.append({"id": fid, "reason": "quote not found"})
                elif k > 1:
                    skipped.append({"id": fid, "reason": "quote ambiguous"})
                else:
                    main_text = main_text.replace(quote, rep)
                    applied.append(fid)
    return main_text, applied, skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--reviews", nargs="*", default=[])
    ap.add_argument("--rules", default=str(DEFAULT_RULES))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json-only", action="store_true")
    args = ap.parse_args()

    path = REPO / "articles" / f"{args.slug}.md"
    if not path.exists():
        print(json.dumps({"changed": False, "error": f"file not found: {path}"}, ensure_ascii=False))
        return 2
    original = path.read_text(encoding="utf-8")
    fm, main_lines, list_lines = split_article(original)
    before = count_chars([l for l in main_lines if l != LIST_SENTINEL])
    result = {"changed": False, "glossary": 0, "banned": 0, "markdown": 0, "applied": [], "skipped": [],
              "chars_main_before": before, "chars_main_after": before}
    if not Path(args.rules).exists():
        result["warning"] = f"rules file not found ({args.rules}); glossary and banned-word steps skipped"

    main_lines, n1 = unescape_backticks(main_lines)
    main_lines, n2 = move_quote_sources(main_lines)
    result["markdown"] = n1 + n2

    gfn, ghits = glossary_fn(read_pairs(args.rules, "定訳（"), read_items(args.rules, "定訳を使わない語"))
    main_lines, result["glossary"] = transform_prose(main_lines, gfn)
    main_lines, result["banned"] = transform_prose(main_lines, banned_fn(read_pairs(args.rules, "効く")))

    main_text = "\n".join(main_lines)
    if args.reviews:
        main_text, result["applied"], result["skipped"] = apply_reviews(main_text, args.reviews)
    main_lines = main_text.split("\n")

    new_text = join_article(fm, main_lines, list_lines)
    result["chars_main_after"] = count_chars([l for l in main_lines if l != LIST_SENTINEL])
    result["changed"] = new_text != original
    if result["changed"] and not args.dry_run:
        path.write_text(new_text, encoding="utf-8")

    if not args.json_only:
        print(f"{'DRY ' if args.dry_run else ''}{'CHANGED' if result['changed'] else 'NO CHANGE'}  {args.slug}  "
              f"glossary={result['glossary']} banned={result['banned']} markdown={result['markdown']} "
              f"applied={result['applied']} chars={before}->{result['chars_main_after']}")
        for pat, k in sorted(ghits.items(), key=lambda kv: -kv[1]):
            word = re.sub(r"^\(\?<!.*?\)|\(\?!.*?\)$", "", pat).replace("\\", "")
            print(f"  glossary: {word} x{k}")
        for s in result["skipped"]:
            print(f"  skipped: {s['id']} ({s['reason']})")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
