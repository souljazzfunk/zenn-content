# Tech Watch harness 改善提案 — 2026-11-14

承認したメッセージの原文: 「承認 1,2」
対象レビュー: `~/.openclaw/workspace/performance/2026-11-14-review.md`

life-automation が正本です。この提案を取り込んで Deploy するまで VPS の規則ファイルには反映されません。記事本文・公開状態は変更しません。2件は別ファイルへの差分です。

## 1. fact 自動置換が出典と異なる人物に深刻度確認を割り当てた

- 現状の問題: 11/14 run 1 の fact:F-01 で、研究者が「深刻度を提案した」出典を、自動置換文が「提案された深刻度を確認した」に変えた。run 2 で Critical が再発し、追加レビューを要した。
- 原因: fact reviewer の手順 6 は `quote` と `replacement` の置換可能性を求めるが、置換文自体の主語・動作・対象・条件を出典と再照合する規則がない。
- 対策と効果: 手順 6 に再照合規則を追加し、照合できない場合は `replacement` を省く。自動置換由来の事実誤りを減らす。

対象ファイル（VPS）: `/home/ubuntu/.openclaw/workspace-zenn-fact-reviewer/AGENTS.md`

```diff
--- a/home/ubuntu/.openclaw/workspace-zenn-fact-reviewer/AGENTS.md
+++ b/home/ubuntu/.openclaw/workspace-zenn-fact-reviewer/AGENTS.md
@@ -38,2 +38,3 @@
 6. 1 文以内の言い換えや削除で直せる指摘は `replacement` に置換後の文（削除なら空文字ではなく、その文を除いた前後の文）を入れる。`quote` をそのまま `replacement` に置き換えて成り立つ形にする。段落の書き直しが要るものは `replacement` を入れない
+   - `replacement` の主語・動作・対象・条件を `problem` に引用した出典の文と再照合する。出典が支えない新しい主張を足さない。照合できないときは `replacement` を省き、`fix` に必要な修正点だけを書く
 7. `~/.openclaw/shared/schemas/review.schema.json` に準拠した JSON を出力先に `write` する。`reviewer` は `"fact"`、id は `F-01` から連番。最終応答は「fact: Critical n / Must fix n / Nice n / unreachable n」の 1 行だけ。JSON を最終応答に繰り返さない
```

回帰確認案: 11/14 run 1 の F-01 を再評価し、研究者が深刻度を提案した出典に忠実な文だけを `replacement` に許す。不明なら `replacement` を省く。Deploy 後の新稿3本で置換後の新規 Critical 件数を確認する（未実施）。

## 2. 初出の中心語・技術語が太字にならなかった

- 現状の問題: 初出の重要語の太字漏れが 11/09、11/12、11/14 の3記事で発生した。例: 11/12 の「MCP」。run 2 でも別語の漏れが生じた。
- 原因: 文体規則はあるが、tech-watch.md Step 2 に初稿保存前の確認がない。
- 対策と効果: 導入と本文の中心語・技術語の初出を保存前に通読し、既存規則どおりの太字を確認する。すべての名詞や再出には広げない。

対象ファイル（VPS）: `/home/ubuntu/.openclaw/workspace/tech-watch.md`

```diff
--- a/home/ubuntu/.openclaw/workspace/tech-watch.md
+++ b/home/ubuntu/.openclaw/workspace/tech-watch.md
@@ -71,2 +71,3 @@
 - `~/.openclaw/shared/knowledge/zenn-style.md` を読み、そこに書かれた 2 人のパーソナリティ・構成・文体・frontmatter に従って、Step 1 の掲載項目（全件）を紹介する対話記事を書く
+- 保存前に導入と本文を通読し、その記事の中心語・技術語の初出が zenn-style.md の規則どおり太字か確認する。すべての名詞や再出を太字にしない
 - 記事の冒頭（L の導入の直後）に `## 今日の N 件` の見出しを立て、Step 1 の 10 件をそのままの順で載せる。各項目の形は zenn-style.md の「記事の構成」節にある（番号・太字のタイトル・要約 2〜3 行・URL）。記事末尾には一覧を置かない
```

回帰確認案: Deploy 後の新稿3本で初回 style の太字漏れ Must fix と、run 2 で新たに現れる漏れを確認する（未実施）。

検証: 現在の VPS 写しの一時コピーへの `git apply --check` と `git apply`、各追加規則1回・既存規則の維持を確認する。これは適用可能性の検証であり、運用時の回帰確認ではありません。
