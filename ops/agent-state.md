# ops/agent-state.md — Tech Watch レビューループの状態（書くのは main / Andy だけ）

## Last run

- 2026-09-09 23:29 JST / 20260907-tech-watch / Run 4 / stop
- check: FAIL (末尾 URL 照合: 別記事の既読 URL 31件を要求)
- fact: Critical 0 / Must fix 6 / Nice 0 / unreachable 0
- style: Critical 0 / Must fix 3 / Nice 0
- writer: not run（max=3 reached）

## Completed

- [ ] Phase 1 Manual: `/zenn-review <slug> max=0` を 1 回実行し、人が review JSON を読んで正誤を判定した
- [ ] Phase 2 Repeatable: 同じ記事に 2 回かけて Critical / Must fix がほぼ一致した
- [ ] Phase 3 Verifiable: `article-check.py` が過去 4 版で誤検知なし
- [ ] Phase 4 Delegated: writer を含む 3 反復以内で Critical 0 に収束し、文字数が増えなかった
- [ ] Phase 5 Scheduled: tech-watch ジョブに組み込み（手動で 3 日連続クリーンが条件）

## Needs human decision

- 20260906-tech-watch / Run 2
- Critical: F-01 VLM Run Gateway の MCP server / read_document / Claude Code・Codex・OpenCode 連携は末尾出典で確認できない
- Must fix: S-01/S-02/S-03 数字が本文に埋め込まれている、S-04 重要主張の引用不足、S-05/S-06 並列事実が段落内に詰まっている
- Reason: published: true かつ未解決の人間判断待ちがあるため writer には渡していない。人が review JSON を読み、修正するなら「公開済みでも直して」と明示する必要がある

- 20260908-tech-watch / Run 1
- Critical: F-01/F-02 は末尾一覧にない出典の記述、F-03 は出典で確認できないモデル名・価格などを含む
- Must fix: F-04〜F-12 は取得不能な出典に依存、S-01〜S-09 は構成・英語表現・数値提示の修正が必要
- Reason: 全指摘への対応には本文の40%以上の書き換えが必要として writer が停止（rewrite-too-large）

- 20260907-tech-watch / Run 4
- Critical: 0
- Must fix: F-01〜F-06 はデータ保持条件・独自解釈・出典外接続先など、S-01〜S-03 は導入構成・数字・キーワード強調
- Reason: writer 上限3回に到達。機械検査は共有 seen ファイル内の別記事 URL 31件との不一致が残る

## Next run

- 20260906-tech-watch、20260907-tech-watch、20260908-tech-watch は人判断待ち

## Human read

- （通読の記録。日付 / slug / 感想の要点 / harness に反映したもの）
