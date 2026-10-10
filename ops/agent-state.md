# ops/agent-state.md — Tech Watch レビューループの状態（書くのは main / Andy だけ）

## Last run

- 2026-10-11 06:12 JST / 20261011-tech-watch / Run 3 / pass
- check: PASS
- fact: Critical 1 / Must fix 0 / Nice 1 / unreachable 0
- style: Critical 0 / Must fix 0 / Nice 1
- writer: not called / chars 4049 → 4030

## Completed

- [ ] Phase 1 Manual: `/zenn-review <slug> max=0` を 1 回実行し、人が review JSON を読んで正誤を判定した
- [ ] Phase 2 Repeatable: 同じ記事に 2 回かけて Critical / Must fix がほぼ一致した
- [ ] Phase 3 Verifiable: `article-check.py` が過去 4 版で誤検知なし
- [ ] Phase 4 Delegated: writer を含む 3 反復以内で Critical 0 に収束し、文字数が増えなかった
- [ ] Phase 5 Scheduled: tech-watch ジョブに組み込み（手動で 3 日連続クリーンが条件）

## Needs human decision

- 解決済み（2026-10-09 5%超の加筆を許可）

- 20261006-tech-watch / run 3 / article_sha: 184e67be2446 / 2026-10-06
  - 残 Critical 0 件
  - 残 Must fix 2 件
  - F-01: Graph Engineering の実行グラフ（ノード、遷移、共有状態、分岐、並列実行、人の承認、再開）の説明は、出典本文を取得できず確認できない
  - F-02: 最小限の創作状態の保持項目、5〜10回の試行、比較指標は、出典本文を取得できず確認できない
  - writer stop_reason: writer 上限2回に到達。文体要件を満たすため再追加した2項目が、事実レビューで未確認となった
  - 質問: 未確認の2件を掲載対象から外して8件にする / 読める出典本文を提供して再レビューする / Must fixを残したまま公開可にする / このままにする、のどれにしますか
- 20260930-tech-watch / run 3 / article_sha: f5eab27286ca / 2026-09-30
  - 前回の判断「全部直して」は解決済み（2026-09-30）
  - 残 Critical 0 件
  - 残 Must fix 1 件
  - S-01: 本文で初出の技術キーワード6語（Software 3.0、Software 1.0、情報経路のアクセス制御、状態機械、march of nines、実演から運用への距離）が太字になっていない
  - writer stop_reason: 既定の writer 上限2回に到達。新たに出た事実指摘2件は自動修正済み
  - 質問: writer 上限を1回増やしてS-01を直す / Must fixを残したまま公開可にする / このままにする、のどれにしますか
- 20260930-tech-watch / run 1 / article_sha: e630afb29e9d / 2026-09-30
  - 残 Critical 0 件
  - 残 Must fix 3 件
  - S-01: A の説明が「新しいのは」「これで」の定型反復になり、項目を順番に読み上げる構成になっている
  - S-02: L の発言が短すぎ、自分の見方と具体的な問いを置く人物像から外れている
  - S-03: Anthropic Frontier Red Team の重要な原文引用と出典名が本文にない
  - writer stop_reason: needs-unsupported-fact（S-03 の引用原文が提供資料に含まれず、出典外の文を補う必要があるため変更なし）
  - 質問: 元記事の原文引用を取得して3件すべて直す / S-01とS-02だけ直してS-03を残す / Must fixを残したまま公開可にする / このままにする、のどれにしますか
- 20260925-tech-watch / run 2 / article_sha: 0126d75d9257 / 2026-09-25
  - 前回の判断「Writer Approved」は解決済み（2026-09-25）
  - 残 Critical 0 件
  - 残 Must fix 1 件
  - S-02: 下書きモデル、対象モデル、比率の三つの値を文中ではなく表へ移す必要がある
  - writer 失敗: prepared model runtime publication was superseded
  - 質問: writer の実行基盤エラー後に、もう一度実行を許可しますか。
  - 選択肢: writer をもう1回許可 / Must fix を残したまま公開可 / このままにする
- 20260925-tech-watch / run 2 / article_sha: 0126d75d9257 / 2026-09-25
  - 残 Critical 0 件
  - 残 Must fix 1 件
  - S-02: 下書きモデル、対象モデル、比率の三つの値を文中ではなく表へ移す必要がある
  - writer 失敗: codex app-server request timed out / CODEX_APP_SERVER_LOCAL_REQUEST_CANCELLED
  - 質問: writer をもう一度許可して S-02 の表形式への修正を行いますか。それとも、Must fix を残したまま公開可にしますか。
  - 選択肢: writer をもう1回許可 / Must fix を残したまま公開可 / このままにする
- 20260921-tech-watch / run 4 / article_sha: 2766f4bcef37 / 2026-09-21
  - 残 Critical 0 件
  - 残 Must fix 6 件
  - F-02: voxium の証言から導いた「仕様と評価が制約になる」という分析を、筆者の推測として明示する必要がある
  - F-03: 防御側の情報分離と承認境界に関する段落を、筆者の提案として明示する必要がある
  - F-06: 認証状態の継続と作業再開の因果を、筆者の考察として明示する必要がある
  - F-07: 境界条件の修正が運用品質を作るという段落を、筆者の考察として明示する必要がある
  - F-08: 長期タスクの継続状態と再開設計に関する段落を、筆者の考察として明示する必要がある
  - S-01: datasette-explain の説明を削ると掲載項目を本文で扱う構成要件を満たせず、出典本文を取得できない事実レビューと文体要件が衝突している
  - writer 修正上限 3 回に到達
  - 質問: datasette-explain を掲載から外して別の項目に差し替え、残る分析箇所を推測表現に直すことを許可しますか。それとも、Must fix を残したまま公開可にしますか。
  - 選択肢: 差し替えと追加修正を許可 / Must fix を残したまま公開可 / このままにする
- 20260919-tech-watch / run 4 / article_sha: 5ae757c7f93a / 2026-09-19
  - 残 Critical 0 / 残 Must fix 1
  - S-01: 一覧10件目のZ.aiを本文で扱っておらず、全掲載項目に触れる構成要件を満たしていない
  - 機械検査: 本文3929字で下限4000字に71字不足
  - 停止理由: writer 3回の上限に到達
  - 質問: writerをもう1回許可してZ.aiへの言及と文字数不足を直す / Z.aiを一覧から外して9件構成にする / Must fixと文字数不足を残したまま公開可にする / このままにする
- 解決済み（2026-09-13 「人が修正した。このままにする。」）: 20260913-tech-watch / Run 6
  - 人が F-01 と S-01 を修正。追加の本文修正は行わない
- 解決済み（2026-09-12 「tech watch 09-12 をもう1回レビューして修正して」）: 20260912-tech-watch / Run 4
- article_sha: 02357e3ca963
- Critical: 0
- Must fix: S-01 「chokepoint」を定訳のある日本語「単一の制御点」へ置き換える
- Reason: writer 上限3回に到達
- Question: 追加修正を許可するか
- Options: writer をもう1回許可 / 人が1語を修正 / このままにする
- 20260906-tech-watch / Run 2
- Critical: F-01 VLM Run Gateway の MCP server / read_document / Claude Code・Codex・OpenCode 連携は末尾出典で確認できない
- Must fix: S-01/S-02/S-03 数字が本文に埋め込まれている、S-04 重要主張の引用不足、S-05/S-06 並列事実が段落内に詰まっている
- Reason: published: true かつ未解決の人間判断待ちがあるため writer には渡していない。人が review JSON を読み、修正するなら「公開済みでも直して」と明示する必要がある
- 20260908-tech-watch / Run 5
- Critical: 0
- Must fix: F-01 記事独自の評価を事実として断定、S-01 Video compressor・ChatGPT・Codex・AI for Economic Opportunity Demo Day の初出太字化
- Reason: 40%以上の改稿許可後の writer 上限3回に到達。機械検査は共有 seen ファイル内の別記事 URL 35件との不一致が残る
- 20260907-tech-watch / Run 4
- Critical: 0
- Must fix: F-01〜F-06 はデータ保持条件・独自解釈・出典外接続先など、S-01〜S-03 は導入構成・数字・キーワード強調
- Reason: writer 上限3回に到達。機械検査は共有 seen ファイル内の別記事 URL 31件との不一致が残る

## Next run

- なし（20261011-tech-watch はレビュー合格で公開処理をした。公開の確認は ops-record の live と zenn-live-watch）

## Human read

- （通読の記録。日付 / slug / 感想の要点 / harness に反映したもの）
