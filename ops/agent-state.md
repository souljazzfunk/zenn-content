# ops/agent-state.md — Tech Watch レビューループの状態（書くのは main / Andy だけ）

## Last run

- 2026-09-07 00:32 JST / 20260906-tech-watch / Run 1 / stop
- check: FAIL (FAILURE_LENGTH: main text 7842 chars, expected 4000-7000)
- fact: Critical 1 / Must fix 0 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 5 / Nice 1
- writer: not run (max=0 review-only; article already published)

## Completed

- [ ] Phase 1 Manual: `/zenn-review <slug> max=0` を 1 回実行し、人が review JSON を読んで正誤を判定した
- [ ] Phase 2 Repeatable: 同じ記事に 2 回かけて Critical / Must fix がほぼ一致した
- [ ] Phase 3 Verifiable: `article-check.py` が過去 4 版で誤検知なし
- [ ] Phase 4 Delegated: writer を含む 3 反復以内で Critical 0 に収束し、文字数が増えなかった
- [ ] Phase 5 Scheduled: tech-watch ジョブに組み込み（手動で 3 日連続クリーンが条件）

## Needs human decision

- 20260906-tech-watch / Run 1
- Critical: F-01 VLM Run Gateway の MCP server / read_document / Claude Code・Codex・OpenCode 連携は末尾出典で確認できない
- Must fix: S-01/S-02 数字が本文に埋め込まれている、S-03 重要主張の引用不足、S-04/S-05 並列事実が段落内に詰まっている
- Reason: max=0 かつ published: true のため writer には渡していない。人が review JSON を読み、修正するなら「公開済みでも直して」と明示する必要がある

## Next run

- 20260906-tech-watch の人判断待ち。解消後に次の記事で `/zenn-review <slug> max=0`

## Human read

- （通読の記録。日付 / slug / 感想の要点 / harness に反映したもの）
