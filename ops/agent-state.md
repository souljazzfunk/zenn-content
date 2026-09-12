# ops/agent-state.md — Tech Watch レビューループの状態（書くのは main / Andy だけ）

## Last run

- 2026-09-12 23:06 JST / 20260910-tech-watch / Run 2 / pass
- check: PASS
- fact: Critical 0 / Must fix 0 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 5 / Nice 0
- writer: not called (confirmation review) / total writer calls 1 / chars 5561 → 5563

## Completed

- [ ] Phase 1 Manual: `/zenn-review <slug> max=0` を 1 回実行し、人が review JSON を読んで正誤を判定した
- [ ] Phase 2 Repeatable: 同じ記事に 2 回かけて Critical / Must fix がほぼ一致した
- [ ] Phase 3 Verifiable: `article-check.py` が過去 4 版で誤検知なし
- [ ] Phase 4 Delegated: writer を含む 3 反復以内で Critical 0 に収束し、文字数が増えなかった
- [ ] Phase 5 Scheduled: tech-watch ジョブに組み込み（手動で 3 日連続クリーンが条件）

## Needs human decision

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

- なし（20260910-tech-watch は公開可。公開は人が指示する）

## Human read

- （通読の記録。日付 / slug / 感想の要点 / harness に反映したもの）
