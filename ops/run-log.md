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
