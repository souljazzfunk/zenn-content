# Tech Watch harness 改善提案 — 2026-11-07

承認したメッセージの原文: 「承認 1,2」
対象レビュー: `~/.openclaw/workspace/performance/2026-11-07-review.md`

life-automation が正本です。この提案を取り込んで Deploy するまで VPS の規則ファイルには反映されません。記事本文・公開状態は変更しません。2件は別ファイルへの差分です。

## 1. L・A の連続発話を機械検査で検出

対象ファイル（VPS）: `/home/ubuntu/zenn-content/scripts/article-check.py`

```diff
--- a/home/ubuntu/zenn-content/scripts/article-check.py
+++ b/home/ubuntu/zenn-content/scripts/article-check.py
@@ -293,2 +293,12 @@
     turns = split_turns(main_lines)
+    consecutive = [
+        (a["speaker"], b["speaker"])
+        for a, b in zip(turns, turns[1:])
+        if a["speaker"] in ("L", "A") and a["speaker"] == b["speaker"]
+    ]
+    if consecutive:
+        failures.append(
+            f"FAILURE_SPEAKER_ALTERNATION: {len(consecutive)} consecutive same-speaker turn(s); "
+            "alternate **L**: and **A**:"
+        )
     speakers = sorted({t["speaker"] for t in turns})
```

回帰確認案: 11/01 run 1 相当の A→A と 11/03 run 2 相当の L→L を FAIL にする。交互の発話間に見出しやコードブロックがある既存合格記事は PASS にする。発話数の均等は検査しない。Deploy 後の新稿で確認する（未実施）。

## 2. 設定キー・値の説明にコードブロックを確認

対象ファイル（VPS）: `/home/ubuntu/.openclaw/workspace/tech-watch.md`

```diff
--- a/home/ubuntu/.openclaw/workspace/tech-watch.md
+++ b/home/ubuntu/.openclaw/workspace/tech-watch.md
@@ -71,2 +71,3 @@
 - `~/.openclaw/shared/knowledge/zenn-style.md` を読み、そこに書かれた 2 人のパーソナリティ・構成・文体・frontmatter に従って、Step 1 の掲載項目（全件）を紹介する対話記事を書く
+- 保存前に、設定キーと値そのものを説明の中心にした箇所を確認し、あれば言語指定付きコードブロックで最小の設定例を示す。識別子への単なる言及には適用しない
 - 記事の冒頭（L の導入の直後）に `## 今日の N 件` の見出しを立て、Step 1 の 10 件をそのままの順で載せる。各項目の形は zenn-style.md の「記事の構成」節にある（番号・太字のタイトル・要約 2〜3 行・URL）。記事末尾には一覧を置かない
```

回帰確認案: 11/01・11/04 の初稿相当で設定例の漏れを確認し、単なる API 名への言及ではコードブロックを要求しないことを確認する。Deploy 後の新稿で確認する（未実施）。

検証済み: 現在の VPS 写しの一時コピーに対して、各差分を `git apply --check` → `git apply` できた。要求された規則は各1回だけ現れ、他の規則に変更はない。変更後の `article-check.py` は構文コンパイル済み。これは差分の適用可能性の検証であり、運用時の回帰確認ではありません。
