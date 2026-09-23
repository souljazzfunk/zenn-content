#!/usr/bin/env python3
"""lint_post.py: mechanical checks for non-Tech-Watch Zenn articles.

Usage: python3 .claude/skills/zenn-post-review/scripts/lint_post.py <slug | path/to/file.md>

Word lists (banned, slang, hedges) are imported from scripts/article-check.py
so there is a single source of truth. Every hit is a suspect for a human or
agent to confirm, not an automatic failure. Exit 0 = no hits, 1 = hits, 2 = missing.
"""
import importlib.util
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]


def load_lists():
    spec = importlib.util.spec_from_file_location("article_check", REPO / "scripts" / "article-check.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.FALLBACK_BANNED, mod.FALLBACK_SLANG, mod.FALLBACK_HEDGES


# 「…」ように / 「…」の領域 / 「…」として: quoted phrase acting as a clause
QUOTE_CLAUSE = re.compile(r"「[^」]{6,}」(ように|ような|の領域|として|という形で)")
# quoted sentence followed by と述べて (long verbatim quote used as reported speech)
QUOTE_SPEECH = re.compile(r"「[^」]*[、。][^」]*」と(述べ|言っ|話し)")
GENERIC_SPEAKER = ["講演者", "発表者", "登壇者"]
VAGUE_FIX = re.compile(r"AIを直")
# unnatural coinages caught in past reviews -> natural wording
UNNATURAL = {"任せて並べる": "並列で任せる"}
# circled digits and keycap emoji: use plain "1." numbering
SPECIAL_NUM = re.compile(r"[\u2460-\u2473\u2776-\u277f]|[0-9]\ufe0f?\u20e3")
SPECS = Path(__file__).resolve().parents[1] / "specs"


def spec_path(article):
    """articles/<slug>.md -> specs/<slug>.spec; any other file -> sibling <stem>.spec."""
    if article.parent.name == "articles":
        return SPECS / f"{article.stem}.spec"
    return article.with_suffix(".spec")


def check_spec(text, spec_file):
    """Enforce the article's review-spec (a sidecar file, because Zenn renders
    HTML comments): key concepts must be repeated, introduced before the ideas
    that depend on them, and present in their section."""
    if not spec_file.exists():
        return [(0, "構造", f"review-spec missing: create {spec_file} (see SKILL.md section H)")]
    body = text
    body_lines = body.split("\n")
    offset = 0
    hits = []
    for raw in spec_file.read_text().strip().split("\n"):
        parts = raw.split()
        if not parts or parts[0] != "concept:" or len(parts) < 2:
            continue
        term, opts = parts[1], dict(p.split("=", 1) for p in parts[2:] if "=" in p)
        n = body.count(term)
        need = int(opts.get("min", 1))
        if n < need:
            hits.append((0, "構造", f"concept '{term}' appears {n}x, needs >= {need}"))
        dep = opts.get("before")
        if dep and dep in body:
            first_t, first_d = body.find(term), body.find(dep)
            if first_t == -1 or first_t > first_d:
                ln = offset + body[:first_d].count("\n") + 1
                hits.append((ln, "構造", f"'{dep}' appears before its premise '{term}'"))
        sec = opts.get("in")
        if sec:
            start = next((i for i, l in enumerate(body_lines) if l.startswith("# " + sec)), None)
            if start is None:
                hits.append((0, "構造", f"section '# {sec}' not found for concept '{term}'"))
            else:
                end = next((i for i in range(start + 1, len(body_lines)) if body_lines[i].startswith("# ")), len(body_lines))
                if term not in "\n".join(body_lines[start:end]):
                    hits.append((offset + start + 1, "構造", f"concept '{term}' missing from section '# {sec}'"))
    return hits


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    arg = sys.argv[1]
    path = Path(arg) if arg.endswith(".md") else REPO / "articles" / f"{arg}.md"
    if not path.exists():
        print(f"missing: {path}")
        return 2
    text = path.read_text()
    lines = text.split("\n")
    banned, slang, hedges = load_lists()
    hits = []

    fm = re.match(r"---\n(.*?)\n---\n", text, re.S)
    fm_text = fm.group(1) if fm else ""
    if re.search(r'^title:\s*"Tech Watch ', fm_text, re.M):
        print("Tech Watch article: use scripts/article-check.py instead")
        return 0
    if not re.search(r"^published:\s*false", fm_text, re.M):
        hits.append((0, "frontmatter", "published is not false"))
    if not re.search(r'^type:\s*"tech"', fm_text, re.M):
        hits.append((0, "frontmatter", "type is not \"tech\" (ok only if the user chose otherwise)"))
    if "#### AIが書きました🤖" not in text:
        hits.append((0, "frontmatter", "AI header missing"))
    if "[^1]" not in text:
        hits.append((0, "出典", "no footnote source"))

    hits += check_spec(text, spec_path(path))

    in_code = False
    for i, line in enumerate(lines, 1):
        if line.startswith("```"):
            in_code = not in_code
        if "—" in line or "–" in line:
            hits.append((i, "表記", "em/en dash"))
        if "<!--" in line and not in_code:
            hits.append((i, "視覚", "HTML comment: Zenn renders it as visible text"))
        if SPECIAL_NUM.search(line):
            hits.append((i, "表記", "special digit (①, 1️⃣); use plain 1. 2. 3."))
        if line.startswith(":::details"):
            hits.append((i, "視覚", ":::details toggle; make it a ### heading"))
        if re.match(r"\s*- \[[ x]\]", line):
            hits.append((i, "視覚", "task list; use a numbered list"))
        if in_code:
            if re.search(r'\{"[^"]{12,}"\}', line):
                hits.append((i, "視覚", "mermaid diamond with long label renders huge"))
            for w, fix in UNNATURAL.items():
                if w in line:
                    hits.append((i, "用語", f"unnatural '{w}'; use '{fix}'"))
            if VAGUE_FIX.search(line):
                hits.append((i, "用語", "diagram says AIを直す; name the real target (エージェントの誤り)"))
            continue
        for w in banned:
            if w in line:
                hits.append((i, "表記", f"banned word '{w}'"))
        for w in slang:
            if w in line:
                hits.append((i, "表記", f"slang '{w}'"))
        for w in hedges:
            if w in line:
                hits.append((i, "表記", f"hedge '{w}'"))
        for w in GENERIC_SPEAKER:
            if w in line:
                hits.append((i, "人名", f"generic label '{w}'; use the person's name"))
        for w, fix in UNNATURAL.items():
            if w in line:
                hits.append((i, "用語", f"unnatural '{w}'; use '{fix}'"))
        if VAGUE_FIX.search(line):
            hits.append((i, "用語", "AIを直す; name the real target (エージェントの誤り)"))
        for m in QUOTE_CLAUSE.finditer(line):
            hits.append((i, "文法", f"quote as clause: {m.group(0)[:40]}"))
        for m in QUOTE_SPEECH.finditer(line):
            hits.append((i, "文法", f"long quote as reported speech: {m.group(0)[:40]}"))

    for ln, cat, msg in hits:
        print(f"L{ln}\t{cat}\t{msg}")
    print(f"{len(hits)} hit(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
