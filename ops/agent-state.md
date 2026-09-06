# ops/agent-state.md — Tech Watch レビューループの状態（書くのは main / Andy だけ）

## Last run

- （まだ実行していない）

## Completed

- [ ] Phase 1 Manual: `/zenn-review <slug> max=0` を 1 回実行し、人が review JSON を読んで正誤を判定した
- [ ] Phase 2 Repeatable: 同じ記事に 2 回かけて Critical / Must fix がほぼ一致した
- [ ] Phase 3 Verifiable: `article-check.py` が過去 4 版で誤検知なし
- [ ] Phase 4 Delegated: writer を含む 3 反復以内で Critical 0 に収束し、文字数が増えなかった
- [ ] Phase 5 Scheduled: tech-watch ジョブに組み込み（手動で 3 日連続クリーンが条件）

## Needs human decision

- （なし）

## Next run

- Phase 1: 今日の記事で `/zenn-review <slug> max=0`

## Human read

- （通読の記録。日付 / slug / 感想の要点 / harness に反映したもの）
