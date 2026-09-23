---
name: zenn-post-review
description: Review a non-Tech-Watch Zenn article (articles/*.md whose title does not start with "Tech Watch") for structure, grammar, naming, source fidelity, visuals and style, then optionally apply fixes. Use when the user asks to review, check, proofread, or polish a Zenn post, 記事レビュー, 記事チェック, 校正, or before committing a non-Tech-Watch article. Not for Tech Watch articles (use scripts/article-check.py and the tech-watch review loop instead).
---

# Zenn post review (non-Tech-Watch)

Review one article in `articles/<slug>.md`. Tech Watch articles are out of scope: if the title starts with `Tech Watch `, stop and point to `scripts/article-check.py`.

The rules below come from real corrections on past posts. Each rule names the failure it prevents.

## Workflow

1. **Read everything first.** Read the whole article. If it is based on a source (transcript, PDF, artifact, URL), read that source too. You need the source for steps 2 and 5.
2. **Check or write the review-spec** (section H), `specs/<slug>.spec`. If it does not exist, derive it from the source: the key concepts, and the premises that later ideas depend on. Show the spec to the user before relying on it.
3. **Run the mechanical lint.**
   ```bash
   python3 .claude/skills/zenn-post-review/scripts/lint_post.py <slug>
   ```
   It reports review-spec violations, dashes, banned words, hedges, slang, `:::details` toggles, task lists, generic speaker labels, quote-clause suspects, and frontmatter problems. Treat every hit as a finding to confirm or dismiss, not as proof.
4. **Check the mermaid diagrams render.** Run `python3 .claude/skills/zenn-post-review/scripts/mermaid_page.py <slug> <scratchpad>`, serve the scratchpad directory with `python3 -m http.server` in the background, open the page in the browser pane, and read the tab title (`m0:ok | m1:ERR ...`). Then take one screenshot to catch layout problems (huge diamond nodes, unreadable fan-outs). Stop the server afterwards.
5. **Run the judgment checks** (sections A to G below) by reading the article.
6. **Report** the findings (format below). Change nothing unless the user asked for fixes.
7. **If asked to fix:** apply the fixes, re-run lint and the mermaid check, then show the user a before/after table. Only commit if the user asks. Run `git pull --rebase` before committing, commit only, and leave the push to the user.
8. **Learn from every user correction** (section I). This step is mandatory, not optional polish.

## A. Structure: recursive pyramid

- The **conclusion comes first** (`# 結論: ...`), in one sentence, ideally inside a blockquote.
- Directly below it, state **3 to 5 pillars** that support it, at the same level of abstraction and in a logical order (for example 直す → 確かめる → 保つ). Show the whole tree once as a diagram.
- **Every pillar opens with its own one-line conclusion** (a `:::message` box such as `**この柱の結論**: ...`). Its sub-sections (`## 1-1.`, `## 1-2.`) must support that line. Any sub-point that does not support its parent line is misplaced.
- The closing `# まとめ` restates the top conclusion and ends with one concrete first step.
- The title and the top conclusion must carry **the theme the user asked for** (for example "building more trust"), not a secondary point from the body.

## B. Japanese grammar

- **A quoted phrase must not act as a clause.** ❌ `Duneは「近道がそのまま正しい道になる」ように作った` / ❌ `「最も難しく、未解決」の領域` / ❌ `「秘密ではなく、大量の地道な作業だ」と述べています`. ✅ Unquote it and integrate it into the sentence: `近道がそのまま正しい道になるように設計された` / `Laurenによれば、〜`. Keep 「」 for true verbatim quotes, slide titles, and labels.
- In prose, **sentences have a subject and a consistent です/ます ending**. ❌ `AIが…書くのではなく、CLIを毎回使う。これで…なります。` ✅ `Laurenのチームでは、…CLIを毎回使います。` Fragments are fine only inside tables, bullets, diagram labels, and `:::message` taglines.
- Avoid `〜、と<人>は述べています` tacked onto a long sentence. Put the attribution first: `<人>によれば、〜`.
- Keep the style formal and scientific. Do not hide a conclusion behind literary phrasing.

## C. Precise wording

- **Name the real object of the action.** Correcting an agent's output is not "fixing the AI": ❌ `AIを直したくなったら` ✅ `エージェントの誤りを直すときは`. Check headings, the conclusion, まとめ, and diagram labels. The same wrong word often appears in all four.
- One concept, one term. Do not introduce a synonym for something already named.
- Use established Japanese, not literal coinages. ❌ `任せて並べる` ✅ `並列で任せる`. Add each new case to `UNNATURAL` in lint with a fixture.
- **Directional words must match the figures.** If the text says `上の段ほど確実`, step 1 must appear at the top of the diagram (use `flowchart BT` when the edges run from 5 to 1). The same applies to 左/右, 前/後, and numbered order.

## D. People and sources

- **Proper names and titles are capitalized correctly** (`Lauren Tan`, `I Shipped 2000 PRs Last Month`), even when the source writes them in lowercase.
- **Call the person by name** after the first full mention (`Lauren`). Do not use generic labels such as `講演者`, `発表者`, or `筆者` for someone else. Do not guess pronouns.
- **Keep the source's claims separate from the author's extrapolation.** Use a legend (`🔧 <Name>の話` / `💼 業務では`) and paired table columns. Every 🔧 claim must be traceable to the source. Anything the source does not say must be labeled as the author's reading, or cut.
- Put the source in a footnote with its URL (`[^1]: <Name>「<Title>」講演（NN分）: <URL>`).
- Quotes from the source stay short: a phrase, not a paragraph.

## E. Visuals: big pictures, few words

- Each section should lead with a **mermaid diagram** or a **comparison table**, followed by at most one or two short sentences or a single bolded takeaway.
- Encouraged: tables (★ ratings for strength), `:::message`, `:::message alert`, blockquotes (including `> ### ...` for the single key line), numbered lists, `---` between pillars, emoji markers, footnotes.
- **Not allowed:**
  - `:::details` toggles. Make them `###` headings with visible text.
  - `- [ ]` task lists (Zenn does not reliably render them). Use a numbered list.
  - HTML comments `<!-- -->`. Zenn renders them as visible text (lint rule + `html_comment` fixture).
- In mermaid:
  - Use `classDef` colors with explicit `color:`.
  - Keep node labels short (use `<br/>` for a second line).
  - Avoid `{}` diamond nodes with long labels, because they render huge. Use `()` or `[]` instead.
  - Stay under 2,000 characters per block.

## F. Style rules (hard)

- No em dash (—) or en dash (–) anywhere: in the article, in commit messages, or in your report to the user. Write ranges as `1〜5` or `1 to 5`.
- No banned words, slang, or hedge phrases (lint covers these through the lists in `scripts/article-check.py`).
- Do not answer a review finding by adding caveats. Fix the sentence or delete it.

## G. Frontmatter and repo rules

- Frontmatter: `type: "tech"` unless the user says otherwise, 1 to 5 `topics`, and `published: false`. Only the human flips `published`.
- The body starts with `#### AIが書きました🤖` and the standard disclosure line.
- Touch only the article under review. Never edit other articles, `books/`, or `.git/`.

## H. review-spec: make the article's logic machine-checkable

Plain lint cannot tell that a premise is missing, because it does not know which ideas the article depends on. The spec writes that knowledge down in the repo (Lauren's step 1: the codebase is the memory), so lint can enforce it (step 2).

The spec is a **sidecar file**, `.claude/skills/zenn-post-review/specs/<slug>.spec`. Never put it inside the article: Zenn renders HTML comments as visible text, and lint flags any `<!--` in an article.

```text
concept: 信頼 min=5 in=結論
concept: 近道 min=3 before=窮屈 in=③
```

- `concept: <term>`: a key concept of the article, written exactly as it appears in the body.
- `min=N`: the term must appear at least N times. A key idea mentioned once was probably dropped somewhere.
- `before=<term>`: this concept is the **premise** of `<term>` and must appear first. Example: agents take shortcuts (近道) is the reason Dune is strict (窮屈). Presenting 窮屈 without 近道 leaves the reader with a conclusion and no reason.
- `in=<heading prefix>`: the term must appear inside the section whose `# ` heading starts with this prefix (`結論`, `②`, `まとめ`).

How to write the spec: for each pillar, ask "what does the source say is the **reason** behind this recommendation?" That reason is a concept with a `before=` edge to the recommendation. Also add the top conclusion's key term with `in=結論` and `in=まとめ`.

## I. Learning loop: promote every correction up the ladder

Treat each user correction the way Lauren treats each agent correction. Do not just fix the sentence. Ask where on the five-step ladder the fix belongs, and put it at the **highest step that works**:

| Step | Where it goes in this skill | Example from past corrections |
|:-:|---|---|
| 1 | The article's spec file in `specs/` (structure that makes the mistake visible) | Premise 近道 dropped before 窮屈 |
| 2 | A lint rule in `lint_post.py`, **plus** a fixture in `tests/fixtures/` and an entry in `tests/expected.json` | Quote used as a clause, `:::details`, 講演者, AIを直す |
| 3 | A rule in sections A to G of this file | Title must carry the requested theme |
| 4 | A worked example in this file | Before/after tables in the report |
| 5 | Nothing written down: the user catches it again next time | Avoid ending here |

After changing lint, run the regression tests, which serve as the skill's CI. Every fixture must pass:

```bash
python3 .claude/skills/zenn-post-review/scripts/test_lint.py
```

Keep one paved path, as a gardener would: when a new lint rule makes a prose rule in A to G redundant, shorten the prose rule to a pointer to the lint rule instead of keeping both.

## Report format

Lead with a verdict in one line (`問題なし` / `要修正: N件`), then one table, most severe first:

| # | 行 | 分類 | 指摘 | 修正案 |
|---|---|---|---|---|
| 1 | L313 | 文法 | 引用句が節として機能している | 近道がそのまま正しい道になるように設計された、… |

Categories: 構造, 文法, 用語, 図と本文の不一致, 出典, 人名, 視覚, 表記, frontmatter. Put the lint output and the mermaid result in one line each under the table. When a fix is obvious, give the exact replacement text rather than a description.
