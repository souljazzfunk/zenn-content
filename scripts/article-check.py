#!/usr/bin/env python3
"""article-check.py — Tech Watch 記事の機械検査（外部シグナル）。

使い方:
    python3 scripts/article-check.py <slug> [--seen PATH] [--rules PATH] [--json-only]

- slug は articles/<slug>.md のファイル名（拡張子なし）
- Tech Watch 記事（title が "Tech Watch " で始まる）だけを検査する。それ以外は skipped=true, exit 0
- 検査項目は docs 化を兼ねて FAILURE_* / WARNING_* の定数名で読める
- 出力: 人が読める行のあと、最後の行に JSON 1 行
- 終了コード: pass なら 0、failures があれば 1、記事が無ければ 2

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
DEFAULT_SEEN = Path(os.path.expanduser("~/.openclaw/workspace/state/tech-watch-seen.json"))

# 閾値（変えるときは zenn-style.md と合わせる）
CHARS_MIN, CHARS_MAX = 4000, 7000
L_AVG_MAX = 120
H2_MIN, H2_MAX = 3, 5
HEDGE_PER_1000_MAX = 3.0
A_NUMBERED_LISTS_MAX = 1

FALLBACK_BANNED = ["片手落ち", "めくら判", "つんぼ桟敷", "気違い", "キチガイ", "精神分裂", "色盲的", "痴呆", "白痴", "外人",
                   "効く", "効い", "効き", "効か", "効け"]  # 末尾 5 つは動詞「効く」の活用形（効果・有効・効率には当たらない）
FALLBACK_SLANG = ["刺さる", "ハマる", "やばい", "ヤバい", "爆速", "秒で", "ぶっちゃけ", "ガチで", "マジで", "神機能", "一択", "知見", "いい感じ", "エモい", "ワンチャン", "ググる"]
FALLBACK_HEDGES = ["かもしれない", "場合によっては", "注意が必要", "補足すると", "一概には"]
OLD_NAMES = ["レックス", "アンドレイ", "架空のキャラクター", "架空の人物"]
AI_HEADER = "#### AIが書きました🤖"
# 英語の形容詞・副詞が述語になっている箇所（「interesting です」「robust だ」）。名詞＋です は拾わない
ENGLISH_ADJ = ["interesting", "robust", "obedient", "legit", "scalable", "cool", "nice", "crazy", "tricky", "elegant", "clever", "smart", "huge", "subtle", "weird", "fragile", "brittle", "naive", "safe", "unsafe", "fast", "slow", "cheap", "expensive", "powerful", "impressive", "boring", "exciting", "surprising", "reasonable", "obvious", "hard", "easy", "simple", "complex"]
ENGLISH_PREDICATE_RE = re.compile(r"\b(" + "|".join(ENGLISH_ADJ) + r")\s*(です|でした|ですね|ですよ|だ[。、とねな]|な[のん]?\b|に見え|すぎる|かな)")
SPEAKER_RE = re.compile(r"^\*\*([^*]+)\*\*:\s*(.*)$")
URL_RE = re.compile(r"https?://[^\s)>\]」』]+")


def parse_frontmatter(text):
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm_text, body = text[4:end], text[end + 5:]
    fm = {}
    key = None
    for line in fm_text.splitlines():
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val == "":
                fm[key] = []
            else:
                fm[key] = val.strip('"')
        elif key and re.match(r"^\s+-\s+", line):
            fm.setdefault(key, [])
            if isinstance(fm[key], list):
                fm[key].append(line.split("-", 1)[1].strip().strip('"'))
    return fm, body


def read_list_section(path, heading):
    """writing-rules.md の `## <heading>` 節の箇条書きを返す。無ければ None。"""
    if not path or not Path(path).exists():
        return None
    items, inside = [], False
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().startswith(heading)
            continue
        if inside and line.startswith("- "):
            items.append(line[2:].strip())
    return items or None


def split_turns(lines):
    """話者ラベル行から次のラベル行の直前までを 1 発言とする。"""
    turns, cur = [], None
    for line in lines:
        m = SPEAKER_RE.match(line)
        if m:
            if cur:
                turns.append(cur)
            cur = {"speaker": m.group(1), "text": m.group(2), "lines": [m.group(2)]}
        elif cur is not None:
            cur["lines"].append(line)
            cur["text"] += "\n" + line
    if cur:
        turns.append(cur)
    return turns


def count_chars(s):
    return len(re.sub(r"\s+", "", s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--seen", default=str(DEFAULT_SEEN), help="tech-watch-seen.json のパス（無ければ URL 照合を警告に格下げ）")
    ap.add_argument("--rules", default=str(DEFAULT_RULES), help="writing-rules.md のパス（無ければ内蔵リスト）")
    ap.add_argument("--json-only", action="store_true")
    args = ap.parse_args()

    path = REPO / "articles" / f"{args.slug}.md"
    if not path.exists():
        print(json.dumps({"pass": False, "skipped": False, "failures": [f"file not found: {path}"], "warnings": [], "stats": {}}, ensure_ascii=False))
        return 2

    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    title = fm.get("title", "") if isinstance(fm.get("title"), str) else ""
    if not title.startswith("Tech Watch "):
        out = {"pass": True, "skipped": True, "failures": [], "warnings": ["not a Tech Watch article; skipped"], "stats": {"title": title}}
        print(json.dumps(out, ensure_ascii=False))
        return 0

    failures, warnings, stats = [], [], {}
    banned = read_list_section(args.rules, "禁止語") or FALLBACK_BANNED
    hedges = read_list_section(args.rules, "ヘッジ語") or FALLBACK_HEDGES
    slang = read_list_section(args.rules, "避ける表現") or FALLBACK_SLANG
    if not Path(args.rules).exists():
        warnings.append(f"rules file not found ({args.rules}); using built-in lists")

    # --- frontmatter
    m = re.match(r"^Tech Watch (\d{4})-(\d{2})-(\d{2}): (.+)$", title)
    if not m:
        failures.append("FAILURE_TITLE_FORMAT: title must be 'Tech Watch YYYY-MM-DD: <主題>'")
    else:
        date_compact = m.group(1) + m.group(2) + m.group(3)
        if args.slug != f"{date_compact}-tech-watch":
            failures.append(f"FAILURE_SLUG_DATE: slug {args.slug} does not match title date {date_compact}")
        if count_chars(m.group(4)) > 20:
            warnings.append("WARNING_TITLE_SUBJECT_LONG: 主題は 20 字以内")
    if not re.match(r"^\d{8}-tech-watch$", args.slug):
        failures.append("FAILURE_SLUG_FORMAT: slug must be YYYYMMDD-tech-watch")
    if fm.get("emoji") != "🎙️":
        failures.append("FAILURE_FM_EMOJI: emoji must be 🎙️")
    if fm.get("type") != "idea":
        failures.append("FAILURE_FM_TYPE: type must be idea")
    if str(fm.get("published")).lower() != "false":
        warnings.append("WARNING_FM_PUBLISHED: published is not false (already published?)")
    topics = fm.get("topics") if isinstance(fm.get("topics"), list) else []
    if not topics or len(topics) > 5:
        failures.append("FAILURE_FM_TOPICS: topics must have 1-5 entries")

    # --- body split: main text vs final list
    lines = body.splitlines()
    list_idx = next((i for i, l in enumerate(lines) if re.match(r"^## 今日の\s*\d+\s*件", l)), None)
    if list_idx is None:
        failures.append("FAILURE_FINAL_LIST_MISSING: '## 今日の N 件' heading not found")
        main_lines, list_lines = lines, []
        declared_n = None
    else:
        main_lines, list_lines = lines[:list_idx], lines[list_idx + 1:]
        declared_n = int(re.search(r"(\d+)", lines[list_idx]).group(1))
    main_text = "\n".join(main_lines)

    if AI_HEADER not in main_text:
        failures.append(f"FAILURE_AI_HEADER: '{AI_HEADER}' missing")

    # --- length
    chars_main = count_chars(re.sub(r"```.*?```", "", main_text, flags=re.S))
    stats["chars_main"] = chars_main
    if chars_main < CHARS_MIN or chars_main > CHARS_MAX:
        failures.append(f"FAILURE_LENGTH: main text {chars_main} chars, expected {CHARS_MIN}-{CHARS_MAX}")

    # --- speakers
    turns = split_turns(main_lines)
    speakers = sorted({t["speaker"] for t in turns})
    bad_speakers = [s for s in speakers if s not in ("L", "A")]
    if bad_speakers:
        failures.append(f"FAILURE_SPEAKER_LABELS: unexpected labels {bad_speakers}")
    l_turns = [t for t in turns if t["speaker"] == "L"]
    a_turns = [t for t in turns if t["speaker"] == "A"]
    stats["turns_L"], stats["turns_A"] = len(l_turns), len(a_turns)
    if not l_turns or not a_turns:
        failures.append("FAILURE_DIALOGUE_MISSING: need both **L**: and **A**: turns")
    else:
        if len(l_turns) > len(a_turns):
            failures.append(f"FAILURE_L_TOO_TALKATIVE: L turns {len(l_turns)} > A turns {len(a_turns)}")
        l_avg = sum(count_chars(t["text"]) for t in l_turns) / len(l_turns)
        stats["L_avg_chars"] = round(l_avg, 1)
        if l_avg > L_AVG_MAX:
            failures.append(f"FAILURE_L_TOO_LONG: L average {l_avg:.0f} chars > {L_AVG_MAX}")
    for name in OLD_NAMES:
        if name in main_text:
            failures.append(f"FAILURE_OLD_NAME: '{name}' found")

    # --- structure
    h2 = [l for l in main_lines if l.startswith("## ")]
    deeper = [l for l in main_lines if re.match(r"^#{3,}\s", l) and not l.startswith(AI_HEADER)]
    stats["h2"] = len(h2)
    if not (H2_MIN <= len(h2) <= H2_MAX):
        failures.append(f"FAILURE_H2_COUNT: {len(h2)} '## ' headings in main text, expected {H2_MIN}-{H2_MAX}")
    if deeper:
        failures.append(f"FAILURE_HEADING_DEPTH: headings deeper than ## found ({len(deeper)})")
    first_h2 = next((i for i, l in enumerate(main_lines) if l.startswith("## ")), len(main_lines))
    intro_list = [l for l in main_lines[:first_h2] if re.match(r"^\s*(-|\d+\.)\s+", l)]
    if len(intro_list) < 3:
        failures.append("FAILURE_INTRO_LIST: 導入直後の項目一覧（3 行以上の箇条書き）が無い")

    # --- markdown sanity
    fences = [l for l in lines if l.strip().startswith("```")]
    if len(fences) % 2:
        failures.append("FAILURE_CODE_FENCE: unbalanced ``` fences")
    for l in fences:
        if l.strip() == "```" and fences.index(l) % 2 == 0:
            warnings.append("WARNING_CODE_LANG: code fence without language")
            break
    block, table_issues = [], 0
    for l in main_lines + [""]:
        if l.strip().startswith("|"):
            block.append(l)
        else:
            if len(block) >= 2:
                cols = {l.strip().strip("|").count("|") for l in block}
                if len(cols) > 1:
                    table_issues += 1
            block = []
    if table_issues:
        failures.append(f"FAILURE_TABLE_COLUMNS: {table_issues} table(s) with uneven columns")

    # --- banned words（禁止語は failure。動詞「効く」の活用形もここに含まれる）
    for w in banned:
        if w in body:
            failures.append(f"FAILURE_BANNED_WORD: '{w}' x{body.count(w)}")

    # --- English adjectives used as predicates（warning。style reviewer が Must fix として扱う）
    eng_hits = [m.group(0) for m in ENGLISH_PREDICATE_RE.finditer(main_text)]
    stats["english_predicates"] = len(eng_hits)
    if eng_hits:
        warnings.append(f"WARNING_ENGLISH_PREDICATE: {len(eng_hits)} hit(s): {eng_hits[:3]}")

    # --- engineer-blog slang（避ける表現は warning。style reviewer が Must fix として扱う）
    slang_hits = {w: main_text.count(w) for w in slang if w in main_text}
    stats["slang"] = sum(slang_hits.values())
    for w, n in slang_hits.items():
        warnings.append(f"WARNING_BLOG_SLANG: '{w}' x{n}")

    # --- degradation guards
    hedge_count = sum(main_text.count(h) for h in hedges)
    per_1000 = hedge_count * 1000 / max(chars_main, 1)
    stats["hedges"], stats["hedges_per_1000"] = hedge_count, round(per_1000, 2)
    if per_1000 > HEDGE_PER_1000_MAX:
        failures.append(f"FAILURE_HEDGE_PILEUP: {hedge_count} hedge phrases ({per_1000:.1f}/1000 chars) > {HEDGE_PER_1000_MAX}")
    a_numbered = 0
    for t in a_turns:
        if sum(1 for l in t["lines"] if re.match(r"^\s*\d+\.\s+", l)) >= 2:
            a_numbered += 1
    stats["A_numbered_lists"] = a_numbered
    if a_numbered > A_NUMBERED_LISTS_MAX:
        failures.append(f"FAILURE_A_NUMBERED_LISTS: {a_numbered} A turns use numbered lists (max {A_NUMBERED_LISTS_MAX})")

    # --- final list vs seen file, and URLs in main text
    list_urls = URL_RE.findall("\n".join(list_lines))
    list_items = [l for l in list_lines if re.match(r"^\s*\d+\.\s+", l)]
    stats["list_items"], stats["list_urls"] = len(list_items), len(list_urls)
    if declared_n is not None:
        if len(list_items) != declared_n:
            failures.append(f"FAILURE_LIST_COUNT: heading says {declared_n} but {len(list_items)} numbered items")
        if len(list_urls) < len(list_items):
            failures.append(f"FAILURE_LIST_URLS: {len(list_items)} items but {len(list_urls)} URLs")
    seen_path = Path(args.seen)
    if seen_path.exists():
        try:
            seen = json.loads(seen_path.read_text(encoding="utf-8"))
            missing = [u for u in seen if u not in list_urls]
            extra = [u for u in list_urls if u not in seen]
            if missing:
                failures.append(f"FAILURE_LIST_VS_SEEN_MISSING: {len(missing)} seen URL(s) not in final list")
            if extra:
                warnings.append(f"WARNING_LIST_VS_SEEN_EXTRA: {len(extra)} list URL(s) not in seen file")
        except Exception as e:  # noqa: BLE001
            warnings.append(f"WARNING_SEEN_UNREADABLE: {e}")
    else:
        warnings.append("WARNING_SEEN_MISSING: seen file not found; skipped list/seen comparison")
    main_urls = URL_RE.findall(main_text)
    stray = sorted({u for u in main_urls if u not in list_urls})
    if stray:
        failures.append(f"FAILURE_STRAY_URL: {len(stray)} URL(s) in main text not in final list: {stray[:3]}")

    ok = not failures
    result = {"pass": ok, "skipped": False, "slug": args.slug, "failures": failures, "warnings": warnings, "stats": stats}
    if not args.json_only:
        print(f"{'PASS' if ok else 'FAIL'}  {args.slug}  chars={chars_main} L={stats.get('turns_L')} A={stats.get('turns_A')} h2={stats.get('h2')} hedges={hedge_count}")
        for f in failures:
            print(f"  ✗ {f}")
        for w in warnings:
            print(f"  ! {w}")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
