# Tech Watch harness 改善提案 — 2026-10-24

承認したメッセージの原文: 「承認 1,2,3」
対象レビュー: `~/.openclaw/workspace/performance/2026-10-24-review.md`

life-automation が正本です。この提案を取り込んで Deploy するまで VPS の規則ファイルには反映されません。
記事本文・公開状態は変更しません。差分は番号順に適用します（2 は 1 の適用後を前提とします）。

## 1. 初稿の文字数余裕を確保

対象ファイル（VPS）: `/home/ubuntu/.openclaw/workspace/tech-watch.md`

```diff
--- a/home/ubuntu/.openclaw/workspace/tech-watch.md
+++ b/home/ubuntu/.openclaw/workspace/tech-watch.md
@@ -73,2 +73,3 @@
 - 要約だけでなく元ページの本文を読む。年代・数値・因果関係・機能・新規性・「従来は／今後は」の比較は、元ページに直接書かれている範囲だけを事実として扱う
+- 初稿は article-check.py の一覧節を除いた本文で 4,200〜5,500 字を目安にする。4,000 字ぎりぎりを狙わず、掲載項目ごとの観察・仕組み・意味を出典の範囲で掘る。字数合わせの但し書きや一般論は足さない
 - 出典にない解釈を加える場合は「A の見方」「A の仮説」だと明示し、出典にない具体的な年・割合・工程で補強しない。確認できない主張は削る
```

回帰確認: 次の新稿3本で、初回 stats.chars_main が4,000以上か確認する。増えた説明が元ページに支えられているか fact review の初回指摘と照合する。

## 2. A の人物像を保存前に確認

対象ファイル（VPS）: `/home/ubuntu/.openclaw/workspace/tech-watch.md`

```diff
--- a/home/ubuntu/.openclaw/workspace/tech-watch.md
+++ b/home/ubuntu/.openclaw/workspace/tech-watch.md
@@ -71,2 +71,3 @@
 - `~/.openclaw/shared/knowledge/zenn-style.md` を読み、そこに書かれた 2 人のパーソナリティ・構成・文体・frontmatter に従って、Step 1 の掲載項目（全件）を紹介する対話記事を書く
+- 保存前に A の発言を通読し、出典にある具体物から始めて原理へ進む説明、言った見積もりの具体的な自己訂正、複数項目を束ねる概念名、仕組みに根拠のある審美的評価・落ち着いた驚きが自然に現れているか確かめる。無い場合は事実に即して直し、定型句や出典外の感想を機械的に足さない
 - 記事の冒頭（L の導入の直後）に `## 今日の N 件` の見出しを立て、Step 1 の 10 件をそのままの順で載せる。各項目の形は zenn-style.md の「記事の構成」節にある（番号・太字のタイトル・要約 2〜3 行・URL）。記事末尾には一覧を置かない
```

回帰確認: 次の新稿3本について、初回の persona-A Must fix 件数と最終 Nice 残件を今回の7本と比較する。

## 3. fact 指摘の同根重複をまとめる

対象ファイル（VPS）: `/home/ubuntu/.openclaw/workspace-zenn-fact-reviewer/AGENTS.md`

```diff
--- a/home/ubuntu/.openclaw/workspace-zenn-fact-reviewer/AGENTS.md
+++ b/home/ubuntu/.openclaw/workspace-zenn-fact-reviewer/AGENTS.md
@@ -36,3 +36,3 @@
    - Nice to have: 出典に忠実だが、より正確な表現がある
-5. 各指摘に、本文からの引用（原文どおり）、問題（出典の該当箇所を短く引用する。writer はこれだけを見て直す）、直し方（削除でよければ「削除」）、根拠となる `source_url` を付ける
+5. 各指摘に、本文からの引用（原文どおり）、問題（出典の該当箇所を短く引用する。writer はこれだけを見て直す）、直し方（削除でよければ「削除」）、根拠となる `source_url` を付ける。同じ出典の同じ記述を同じ誤解で複数箇所に使った場合は 1 件にまとめ、`problem` に他の該当箇所も列挙する。異なる根拠・異なる誤りは分ける
 6. 1 文以内の言い換えや削除で直せる指摘は `replacement` に置換後の文（削除なら空文字ではなく、その文を除いた前後の文）を入れる。`quote` をそのまま `replacement` に置き換えて成り立つ形にする。段落の書き直しが要るものは `replacement` を入れない
```

回帰確認: 20261019-tech-watch の run 1 を代表例として、F-01〜F-03 相当が1件にまとまり、F-04〜F-05 相当は別件で残るか確認する。
