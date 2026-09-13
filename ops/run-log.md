# ops/run-log.md — Tech Watch レビューループの実行記録（書くのは main / Andy だけ）

1 回の `/zenn-review` 実行 = 1 エントリ。形式は skill `zenn-review` の REMEMBER 節のとおり。週次の `/zenn-perf-review` はこのログから harness の改善案を作る。

## Run 1 (2026-09-07 00:32 JST) 20260906-tech-watch
- Trigger: telegram
- check: FAIL (FAILURE_LENGTH: main text 7842 chars, expected 4000-7000)
- fact: Critical 1 / Must fix 0 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 5 / Nice 1
- writer: changed false / addressed [] / declined [F-01, S-01, S-02, S-03, S-04, S-05] / chars 7842 -> 7842 / stop_reason max=0 review-only; article already published
- Result: stop
- Harness change 候補: なし

## Run 2 (2026-09-07 00:40 JST) 20260906-tech-watch
- Trigger: telegram
- check: FAIL (FAILURE_LENGTH: main text 7842 chars, expected 4000-7000)
- fact: Critical 1 / Must fix 0 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 6 / Nice 1
- writer: changed false / addressed [] / declined [F-01, S-01, S-02, S-03, S-04, S-05, S-06] / chars 7842 -> 7842 / stop_reason review-only; article already published and unresolved human decision exists
- Result: stop
- Harness change 候補: なし

## Run 1 (2026-09-09 23:03 JST) 20260908-tech-watch
- Trigger: telegram
- check: FAIL (FAILURE_L_TOO_LONG: L average 146 chars > 120, FAILURE_BANNED_WORD: '効く' x2, FAILURE_BANNED_WORD: '効い' x1, FAILURE_LIST_VS_SEEN_MISSING: 31 seen URL(s) not in final list)
- fact: Critical 3 / Must fix 9 / Nice 0 / unreachable 4
- style: Critical 0 / Must fix 9 / Nice 0
- writer: changed false / addressed [] / declined [F-01–F-12, S-01–S-09] / chars 4887 → 4887 / stop_reason rewrite-too-large（全指摘への対応に本文の40%以上の書き換えが必要）
- Result: stop
- Harness change 候補: article-check.py の末尾 URL 照合が別日の既読 URL 31件を要求している可能性を確認する

## Run 1 (2026-09-09 22:52 JST) 20260907-tech-watch
- Trigger: telegram
- check: FAIL (FAILURE_BANNED_WORD: '効く' x1, FAILURE_BANNED_WORD: '効い' x1, FAILURE_LIST_VS_SEEN_MISSING: 31 seen URL(s) not in final list)
- fact: Critical 0 / Must fix 3 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 7 / Nice 0
- writer: changed true / addressed [F-01, F-02, F-03, S-01, S-02, S-03, S-04, S-05, S-06, S-07] / declined [FAILURE_LIST_VS_SEEN_MISSING] / chars 5538 → 5496 / stop_reason なし
- Result: continue
- Harness change 候補: article-check.py の末尾 URL 照合が別日の既読 URL 31件を要求している可能性を確認する

## Run 2 (2026-09-09 23:07 JST) 20260907-tech-watch
- Trigger: telegram
- check: FAIL (FAILURE_LIST_VS_SEEN_MISSING: 31 seen URL(s) not in final list)
- fact: Critical 1 / Must fix 3 / Nice 1 / unreachable 0
- style: Critical 0 / Must fix 4 / Nice 0
- writer: changed true / addressed [F-01, F-02, F-03, F-04, F-05, S-01, S-02, S-03, S-04] / declined [FAILURE_LIST_VS_SEEN_MISSING] / chars 5496 → 5539 / stop_reason なし
- Result: continue
- Harness change 候補: article-check.py の末尾 URL 照合が別日の既読 URL 31件を要求している可能性を確認する

## Run 3 (2026-09-09 23:17 JST) 20260907-tech-watch
- Trigger: telegram
- check: FAIL (FAILURE_LIST_VS_SEEN_MISSING: 31 seen URL(s) not in final list)
- fact: Critical 1 / Must fix 3 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 3 / Nice 0
- writer: changed true / addressed [F-01, F-02, F-03, F-04, S-01, S-02, S-03] / declined [FAILURE_LIST_VS_SEEN_MISSING] / chars 5539 → 5559 / stop_reason なし
- Result: continue
- Harness change 候補: article-check.py の末尾 URL 照合が別日の既読 URL 31件を要求している可能性を確認する

## Run 4 (2026-09-09 23:29 JST) 20260907-tech-watch
- Trigger: telegram
- check: FAIL (FAILURE_LIST_VS_SEEN_MISSING: 31 seen URL(s) not in final list)
- fact: Critical 0 / Must fix 6 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 3 / Nice 0
- writer: changed false / addressed [] / declined [F-01, F-02, F-03, F-04, F-05, F-06, S-01, S-02, S-03, FAILURE_LIST_VS_SEEN_MISSING] / chars 5559 → 5559 / stop_reason max=3 reached
- Result: stop
- Harness change 候補: article-check.py の末尾 URL 照合が別日の既読 URL 31件を要求している可能性を確認する

## Run 2 (2026-09-09 23:52 JST) 20260908-tech-watch
- Trigger: telegram
- check: FAIL (FAILURE_L_TOO_LONG: L average 146 chars > 120, FAILURE_BANNED_WORD: '効く' x2, FAILURE_BANNED_WORD: '効い' x1, FAILURE_LIST_VS_SEEN_MISSING: 31 seen URL(s) not in final list)
- fact: Critical 3 / Must fix 9 / Nice 0 / unreachable 4
- style: Critical 0 / Must fix 10 / Nice 0
- writer: changed true / addressed [F-01〜F-12, S-01〜S-10] / declined [FAILURE_LIST_VS_SEEN_MISSING] / chars 4887 → 4057 / stop_reason なし（40%以上の改稿を人が許可）
- Result: continue
- Harness change 候補: article-check.py の末尾 URL 照合が別日の既読 URL を要求している可能性を確認する

## Run 3 (2026-09-10 00:08 JST) 20260908-tech-watch
- Trigger: telegram
- check: FAIL (FAILURE_LIST_VS_SEEN_MISSING: 35 seen URL(s) not in final list)
- fact: Critical 1 / Must fix 2 / Nice 1 / unreachable 0
- style: Critical 0 / Must fix 6 / Nice 0
- writer: changed true / addressed [F-01, F-02, F-03, F-04, S-01, S-02, S-03, S-04, S-05, S-06] / declined [FAILURE_LIST_VS_SEEN_MISSING] / chars 4057 → 4064 / stop_reason なし
- Result: continue
- Harness change 候補: article-check.py の末尾 URL 照合が別日の既読 URL 35件を要求している可能性を確認する

## Run 4 (2026-09-10 00:22 JST) 20260908-tech-watch
- Trigger: telegram
- check: FAIL (FAILURE_LIST_VS_SEEN_MISSING: 35 seen URL(s) not in final list)
- fact: Critical 0 / Must fix 0 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 2 / Nice 0
- writer: changed true / addressed [S-01, S-02] / declined [] / chars 4064 → 4207 / stop_reason なし
- Result: continue
- Harness change 候補: article-check.py の末尾 URL 照合が別日の既読 URL 35件を要求している可能性を確認する

## Run 5 (2026-09-10 00:35 JST) 20260908-tech-watch
- Trigger: telegram
- check: FAIL (FAILURE_LIST_VS_SEEN_MISSING: 35 seen URL(s) not in final list)
- fact: Critical 0 / Must fix 1 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 1 / Nice 0
- writer: changed false / addressed [] / declined [F-01, S-01, FAILURE_LIST_VS_SEEN_MISSING] / chars 4207 → 4207 / stop_reason max=3 reached after rewrite override
- Result: stop
- Harness change 候補: article-check.py の末尾 URL 照合が当日一覧ではなく累積 seen URL を要求する不具合を確認する

## Run 4 (2026-09-12 18:22 JST) 20260912-tech-watch
- Trigger: cron（isolated セッションで起動された）
- article_sha: 02357e3ca963
- check: PASS
- fact: Critical 0 / Must fix 0 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 1 / Nice 0
- writer: changed true / addressed [F-01, F-02, F-03, F-04, F-05, S-01〜S-11, FAILURE_BANNED_WORD] / declined [run-4 S-01] / chars 5044 → 4468 / stop_reason writer 上限3回に到達
- Result: stop
- Harness change 候補: 定訳のある一般名詞の英語混在を article-check.py で検出できるか検討する

## Run 1 (2026-09-12 22:07 JST) 20260911-tech-watch
- Trigger: cron（isolated セッションで起動された）
- article_sha: 2aa08b141c90
- check: FAIL (FAILURE_L_TOO_TALKATIVE, FAILURE_STRAY_URL)
- autofix: glossary 23 / banned 0 / markdown 1 / applied [S-01,S-02,S-03,S-12]
- fact: Critical 0 / Must fix 0 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 12 / Nice 0
- writer: changed true / addressed [S-04,S-05,S-06,S-07,S-08,S-09,S-10,S-11,FAILURE_L_TOO_TALKATIVE,FAILURE_STRAY_URL] / declined [] / chars 4628 → 4554 / stop_reason なし
- Result: continue
- Harness change 候補: 英語一般名詞の混在を article-check.py または定訳辞書で検出・置換できるか検討する

## Run 2 (2026-09-12 22:10 JST) 20260911-tech-watch
- Trigger: cron（isolated セッションで起動された）
- article_sha: 6ebb2049a0e9
- check: PASS
- autofix: glossary 0 / banned 0 / markdown 0 / applied [S-02]
- fact: Critical 0 / Must fix 0 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 12 / Nice 0
- writer: not called (confirmation review) / total writer calls 1 / chars 4554 → 4545
- Result: pass
- Harness change 候補: 英語一般名詞の定訳候補を定訳辞書へ追加し article-check.py で混在を検出できるか検討する

## Run 4 (2026-09-12 22:26 JST) 20260912-tech-watch
- Trigger: telegram（人の指示）
- article_sha: af5e6849bd91
- check: PASS
- autofix: glossary 0 / banned 0 / markdown 0 / applied []
- fact: Critical 0 / Must fix 0 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 1 / Nice 0
- writer: changed true / addressed [S-01] / declined [] / chars 4468 → 4461 / stop_reason なし / human decision: writer をもう1回許可
- Result: continue
- Harness change 候補: 定訳のある一般名詞の英語混在を article-check.py で検出できるか検討する

## Run 5 (2026-09-12 22:28 JST) 20260912-tech-watch
- Trigger: telegram（人の指示）
- article_sha: af5e6849bd91
- check: PASS
- autofix: glossary 0 / banned 0 / markdown 0 / applied []
- fact: Critical 0 / Must fix 0 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 0 / Nice 0
- writer: not called (confirmation review) / total writer calls 1 / chars 4468 → 4461
- Result: pass
- Harness change 候補: 定訳のある一般名詞の英語混在を article-check.py で検出できるか検討する

## Run 1 (2026-09-12 23:04 JST) 20260910-tech-watch
- Trigger: telegram（人の指示）
- article_sha: 03be91e4aa4f
- check: PASS
- autofix: glossary 55 / banned 0 / markdown 1 / applied [F-01,F-04,F-03,F-05]
- fact: Critical 2 / Must fix 2 / Nice 1 / unreachable 0
- style: Critical 0 / Must fix 4 / Nice 0
- writer: changed true / addressed [S-01,S-02,S-03,S-04,FAILURE_L_TOO_TALKATIVE] / declined [] / chars 6075 → 5561 / stop_reason none
- Result: continue
- Harness change 候補: 未登録英語の定訳候補が多数あり、定訳辞書の拡充候補

## Run 2 (2026-09-12 23:06 JST) 20260910-tech-watch
- Trigger: telegram（人の指示）
- article_sha: a649e0e0876c
- check: PASS
- autofix: glossary 0 / banned 0 / markdown 0 / applied [S-01,S-03]
- fact: Critical 0 / Must fix 0 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 5 / Nice 0
- writer: not called (confirmation review) / total writer calls 1 / chars 5561 → 5563
- Result: pass
- Harness change 候補: 自動置換が出典タイトル内で語を連結しない保護と、3つ以上の値を検出する検査の追加候補

## Run 1 (2026-09-13 10:34 JST) 20260913-tech-watch
- Trigger: cron（isolated セッションで起動された）
- article_sha: 6136266c9a51
- check: PASS
- autofix: glossary 0 / banned 0 / markdown 0 / applied [F-01,S-02,S-03,S-07]
- fact: Critical Critical 0 / Must fix Must fix 0 / Nice Nice 0 / unreachable unreachable 0
- style: Critical Critical 0 / Must fix Must fix 5 / Nice Nice 0
- writer: not called (autofix confirmation review) / total writer calls 0 / chars 4622 -> 4625
- Result: continue
- Harness change 候補: 英語一般名詞の定訳候補を定訳辞書へ追加し article-check.py で混在を検出できるか検討する

## Run 2 (2026-09-13 10:37 JST) 20260913-tech-watch
- Trigger: cron（isolated セッションで起動された）
- article_sha: 3ff403db95fe
- check: PASS
- autofix: glossary 0 / banned 0 / markdown 0 / applied [run1:F-01,S-02,S-03,S-07; run2:F-01,F-02]
- fact: Critical Critical 0 / Must fix Must fix 0 / Nice Nice 0 / unreachable unreachable 0
- style: Critical Critical 0 / Must fix Must fix 6 / Nice Nice 0
- writer: not called (confirmation review) / total writer calls 0 / chars 4622 -> 4635
- Result: pass
- Harness change 候補: 英語一般名詞の定訳候補を定訳辞書へ追加し article-check.py で混在を検出できるか検討する

## Run 3 (2026-09-13 11:24 JST) 20260913-tech-watch
- Trigger: cron（isolated セッションで起動された）
- article_sha: 033b394ca294
- check: FAIL (FAILURE_GLUED_TRANSLATION)
- autofix: glossary 18 / banned 0 / markdown 0 / applied []
- fact: Critical 0 / Must fix 0 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 5 / Nice 1
- glossary: added [action space → 行動空間, build process → ビルド処理, cost limit → 費用上限, method call → メソッド呼び出し, human intervention → 人の介入, model selection → モデル選択, code generator → コード生成器] / fixed [] / skipped 0
- writer: changed true / addressed [S-01,S-02,S-03,S-04,S-05,S-06,FAILURE_GLUED_TRANSLATION] / declined [] / chars 4532 → 4104 / stop_reason なし
- Result: continue
- Harness change 候補: 定訳置換が codingエージェント等の連結語を生成するため、article-fix.py の単語境界処理を改善する候補

## Run 4 (2026-09-13 11:28 JST) 20260913-tech-watch
- Trigger: cron（isolated セッションで起動された）
- article_sha: 6d4031db8ae4
- check: PASS
- autofix: glossary 0 / banned 0 / markdown 0 / applied []
- fact: Critical 0 / Must fix 0 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 1 / Nice 0
- writer: changed true / addressed [S-01] / declined [] / chars 4104 → 4092 / stop_reason なし
- Result: continue
- Harness change 候補: 英語一般名詞句の警告を本文と一覧で区別して検出する article-check.py 改善候補

## Run 5 (2026-09-13 11:31 JST) 20260913-tech-watch
- Trigger: cron（isolated セッションで起動された）
- article_sha: 586e7ee688f0
- check: PASS
- autofix: glossary 0 / banned 0 / markdown 0 / applied []
- fact: Critical 0 / Must fix 0 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 1 / Nice 0
- writer: changed true / addressed [S-01] / declined [] / chars 4092 → 4097 / stop_reason なし
- Result: continue
- Harness change 候補: 英語略語（VM/PR/OS/Human-in-the-Loop）を article-check.py で検出する候補

## Run 6 (2026-09-13 11:34 JST) 20260913-tech-watch
- Trigger: cron（isolated セッションで起動された）
- article_sha: 0b2401e0dffb
- check: PASS
- autofix: glossary 0 / banned 0 / markdown 0 / applied [F-01]
- fact: Critical 1 / Must fix 0 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 1 / Nice 0
- glossary: added [action space → 行動空間, build process → ビルド処理, cost limit → 費用上限, method call → メソッド呼び出し, human intervention → 人の介入, model selection → モデル選択, code generator → コード生成器] / fixed [] / skipped 0
- writer: not called (writer limit reached) / total writer calls 3 / chars 4097 → 4103 / stop_reason writer 上限3回に到達
- Result: stop
- Harness change 候補: 日本語置換後の助詞前空白を article-fix.py または article-check.py で自動修正・検出する候補

## Run 7 (2026-09-13 12:56 JST) 20260913-tech-watch
- Trigger: telegram（人の指示）
- article_sha: 8edc4c743a37
- check: PASS
- autofix: glossary 0 / banned 0 / markdown 0 / applied []
- fact: Critical 0 / Must fix 0 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 0 / Nice 0
- writer: human edit / addressed [F-01,S-01] / chars 4103 → 4103 / user chose このままにする
- Result: pass
- Harness change 候補: なし
