# zenn-content — AGENTS.md（このリポジトリで作業するすべてのエージェントの規約）

## Deliverable

- 公開物は `articles/*.md` だけ。Zenn は `articles/` と `books/` しか読まないので、`scripts/` と `ops/` は公開に影響しない
- Tech Watch 記事は `articles/YYYYMMDD-tech-watch.md`。文体・構成・frontmatter は `~/.openclaw/shared/knowledge/zenn-style.md` が正本

## 誰が何を書くか（one writer, many readers）

| パス | 書く | 読む |
|---|---|---|
| `articles/<slug>.md` | 初稿: tech-watch ジョブ（main）。修正: `zenn-writer` のみ | 全員 |
| `ops/agent-state.md`, `ops/run-log.md` | main（Andy）のみ | 全員 |
| `scripts/article-check.py`, この `AGENTS.md` | 人（Claude Code 経由）。週次レビューの承認後は main も可 | 全員 |

## Evidence policy

- 記事本文の主張は、末尾「今日の N 件」の URL に基づく。出典に書いていないことを事実として書かない
- 推測は「たぶん」「だと思う」「私の予想では」を付ける。確認できないことは削る。但し書きで残さない
- 本文中に URL を置くなら末尾一覧にあるものだけ

## Anti-bloat（ループが静かに壊すもの、のドキュメント版）

- レビュー指摘に応えるために注意書き・補足・ヘッジ語を足さない。直すか削る
- 修正で本文の文字数を増やさない。原則は同じかそれ以下（上限は修正前の 1.05 倍）
- 同じ概念に別の言い方を増やさない

## Safety

- `published` と `published_at` は人の Telegram 指示（zenn-publish ルール）でだけ変える。レビューループの中では触らない
- git の commit / push は main だけが行う。writer と reviewer は行わない
- 他人の所有パスを直さない。気付いたことは自分の出力（JSON の `notes`）に書いて main に渡す
- `articles/` の他の記事、`books/`、`.git/` を触らない

## 検査

- `python3 scripts/article-check.py <slug>` が外部シグナル。最後の行の JSON を使う。PASS でも reviewer の Critical があれば不合格
- 表現ルール（禁止語）は `~/.openclaw/shared/knowledge/writing-rules.md` が正本。ここに二重に書かない
