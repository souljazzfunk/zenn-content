# Harness 改善提案 — 2026-11-21

承認したメッセージの原文: 「承認123」
対象レビュー: `~/.openclaw/workspace/performance/2026-11-21-review.md`

life-automation が正本です。この提案を取り込んで Deploy するまで VPS の規則・検査には反映されません。記事本文・公開状態は変更しません。3件は別ファイルへの差分です。

## 1. 反復する表現型の指摘を記事全文で直す

対象ファイル（VPS）: `/home/ubuntu/.openclaw/workspace-zenn-writer/AGENTS.md`

11/17 の A の三人称自己呼称は4 runs に残った。同じ型の表現を全文検索して一括修正・再確認する手順を追加する。

~~~~diff
--- a/home/ubuntu/.openclaw/workspace-zenn-writer/AGENTS.md
+++ b/home/ubuntu/.openclaw/workspace-zenn-writer/AGENTS.md
@@ -30,3 +30,3 @@
 1. 記事、文体定義、`~/.openclaw/shared/knowledge/writing-rules.md`、review JSON 2 つ、check JSON、writer-result schema を読む（`~/zenn-content/AGENTS.md` は読まなくてよい。要点は Constraints に書いてある）。記事は必ず全文を読む
-2. Task の「対象 id」の指摘だけを読む（それ以外の id は既に機械で解決済み）。Critical → 機械検査の failures → Must fix → Nice の順に対応を決める。指摘に `replacement` があればその文をそのまま使う
+2. Task の「対象 id」の指摘だけを読む（それ以外の id は既に機械で解決済み）。Critical → 機械検査の failures → Must fix → Nice の順に対応を決める。指摘に `replacement` があればその文をそのまま使う。反復する表現型の指摘（例: A の「Aの仮説」「Aの提案」「Aの見方」という三人称自己呼称）は、指摘の quote だけでなく記事全文で同じ型を探し、全箇所を一度に直して残存がないか確認する
 3. 直し方の優先順位: 削る ＞ 言い換える ＞ 書き足す。指摘に応えるために但し書き・注意書き・ヘッジ語を足さない
~~~~

回帰確認: 11/17 の指摘を入力して、複数の「Aの仮説」「Aの提案」等が一度の writer 呼び出しで解消するかを Deploy 後の新稿で確認する（未実施）。

## 2. 同一話者の連続発話を機械検査で検出する

対象ファイル（VPS）: `/home/ubuntu/zenn-content/scripts/article-check.py`

11/19 初稿には A→A が4箇所あったが機械検査は PASS。冒頭一覧を除いた本文の発話列で隣接話者を比較し、同一話者の連続を FAILURE にする。fenced code 内の例示ラベルは発話に数えない。

~~~~diff
--- a/home/ubuntu/zenn-content/scripts/article-check.py
+++ b/home/ubuntu/zenn-content/scripts/article-check.py
@@ -90,5 +90,17 @@
 def split_turns(lines):
-    """話者ラベル行から次のラベル行の直前までを 1 発言とする。"""
+    """コードブロック外の話者ラベル行から次のラベル行の直前までを 1 発言とする。"""
     turns, cur = [], None
+    in_fence = False
     for line in lines:
+        if line.lstrip().startswith("```"):
+            in_fence = not in_fence
+            if cur is not None:
+                cur["lines"].append(line)
+                cur["text"] += "\n" + line
+            continue
+        if in_fence:
+            if cur is not None:
+                cur["lines"].append(line)
+                cur["text"] += "\n" + line
+            continue
         m = SPEAKER_RE.match(line)
@@ -291,2 +303,9 @@
     turns = split_turns(main_lines)
+    repeated = [(turns[i]["speaker"], i + 1) for i in range(len(turns) - 1)
+                if turns[i]["speaker"] == turns[i + 1]["speaker"]]
+    stats["consecutive_same_speaker"] = len(repeated)
+    if repeated:
+        failures.append(
+            f"FAILURE_SPEAKER_ALTERNATION: {len(repeated)} consecutive same-speaker pair(s): {repeated[:5]}"
+        )
     speakers = sorted({t["speaker"] for t in turns})
~~~~

回帰確認: 一時コピーで A→A 4組を検出し、交互発話と fenced code 内の見かけ上のラベルを許容する。Deploy 後の実記事で誤検知の有無を確認する（未実施）。

## 3. 初稿前の出典照合を明記する

対象ファイル（VPS）: `/home/ubuntu/zenn-content/AGENTS.md`

5記事の初回 fact Critical は計7件。11/21 は取得できた要約にない数値「0.32・0.26」が入った。数値・方式・機能・因果を取得済みの出典と照合し、要約しか読めない場合は記述範囲を要約に限定する。

~~~~diff
--- a/home/ubuntu/zenn-content/AGENTS.md
+++ b/home/ubuntu/zenn-content/AGENTS.md
@@ -19,2 +19,3 @@
 - 記事本文の主張は、冒頭「## 今日の N 件」の URL に基づく。出典に書いていないことを事実として書かない
+- 初稿を書く前に、本文に入れる数値・方式・機能・因果の各主張を、実際に取得できた出典の記述に照合する。取得できたのが要約だけなら、要約にない具体的な数値・手順・実験条件は書かず、確認できた範囲だけで述べる
 - 推測は「たぶん」「だと思う」「私の予想では」を付ける。確認できないことは削る。但し書きで残さない
~~~~

回帰確認: Deploy 後の新稿で、要約にない数値・手順・条件が初稿に入らないか、初回 fact Critical 件数を確認する（未実施）。

検証: 現在の VPS 写しの一時コピーへの `git apply --check` と `git apply`、各規則の一意性・既存規則の維持を確認する。これは適用可能性の検証であり、運用時の回帰確認ではありません。
