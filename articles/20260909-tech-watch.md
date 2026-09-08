---
title: "Tech Watch 2026-09-09: Agent基盤"
emoji: "🎙️"
type: "idea"
topics:
  - "AI"
  - "Anthropic"
  - "OpenAI"
  - "ClaudeCode"
  - "LLM"
published: false
---

#### AIが書きました🤖

この記事は、AIが書いたものを人間が確認してから投稿しています。

**L**: 今日は、モデルの性能そのものより、その周りに作る infrastructure が主役に見える。agent に何を見せるか、何を実行させるか、どこで止めるか。『インターステラー』で船体そのものより航法と生命維持が生死を分ける感じに近い。今日の項目はこうです。

- 1. How we contain Claude across products / Anthropic Engineering
- 2. How GPT-5.6 Sol helps run quantum computing experiments / OpenAI
- 3. The Work Now Within Reach / OpenAI
- 4. Introducing ChatGPT Images 2.5 / OpenAI
- 5. On the Navier-Stokes Millennium Prize Problem / OpenAI
- 6. The New MCP Roadmap / MCP Blog
- 7. OpenClaw 2026.9.3 / GitHub Releases
- 8. Safety for Whom? / Hugging Face
- 9. Fine-tuning a 350M Model for Better Structured Outputs in 100 GRPO Steps / Hugging Face
- 10. NeoMME / Hugging Face

## Agentを閉じ込める技術

**A**: まず Anthropic の “How we contain Claude across products” がかなり重要です。観察として面白いのは、Claude Code の permission prompt が、理論上は human-in-the-loop の安全境界なのに、実運用では利用者が約 93% 承認していたという数字です。これ、dialog が security boundary というより、だんだん儀式になっていくという話ですよね。

> users approved roughly 93% of permission prompts

出典: How we contain Claude across products

**L**: 人間が境界になる設計の限界、ということ？

**A**: そう見えます。記事はリスクを user misuse、model misbehavior、external attackers に分けて、防御対象を model、environment、external content に分ける。主戦場が「モデルに良い判断をさせる」から「モデルが間違っても壊せる範囲を小さくする」に移っている。Claude Code なら OS-level sandbox、claude.ai なら ephemeral container、Cowork ならローカル VM。かなり乱暴にまとめると、**obedience based safety から containment based safety へ**、です。

**L**: OpenClaw のリリースもそこに繋がる？

**A**: 繋がります。OpenClaw 2026.9.3 は、更新を isolated candidate state でリハーサルしてから有効化する update flow が大きい。prompt cache の保持、memory search の軽量化、Skill Workshop の agent-owned collection 化も入りました。長時間稼働 agent では、こういう operational な改善のほうが効くことが多いです。

## 実験室と数学で動く巨大ループ

**L**: OpenAI の量子実験の記事は、agent が物理世界に少し近づいた感じがする。

**A**: GPT-5.6 Sol と Codex を、MIT の superconducting qubit 実験ソフトウェアに接続した話ですね。新しいのは、Codex が単に解析コードを書くのではなく、測定を実行し、結果を見て、次の測定条件を選び、次の測定に渡すところ。入力は chip design targets と measurement-specific skills、出力は calibration 結果です。

**A**: 面白いのは、ここでも skills が出てくることです。実験手順を渡すと、agent が数時間単位で routine measurement を回せる。弱い信号や noisy な結果ではまだ人間の介入が必要だったので、得意なのは「明確に定義された workflow の中で、観測して調整する」部分だと思います。

**L**: Navier-Stokes のほうは、規模が急に桁違いになる。

**A**: そこが今日いちばん極端な例です。OpenAI は内部モデルで Navier-Stokes Millennium Prize Problem の解決案と Lean formalization を出したと発表しました。約 10,000 concurrent agents、2.7 million messages、130 billion output tokens。88 時間で解決案に到達し、その後 GPT-6 Astra で Lean 形式化と検証に 17 時間。

**A**: これは「大きなモデルがひとりで解いた」というより、問題の variant を複数の agent group に分け、途中成果を Codex で統合する harness の話として読んだほうが面白い。外部検証は別問題ですが、大規模 agent swarm の実例ではあります。

**L**: The Work Now Within Reach は、それを会社の成長戦略に接続している？

**A**: そうです。Sarah Friar の会社視点で、GPT-6 Astra、ChatGPT Work、Codex、compute stack をまとめています。OpenAI 研究組織では人間 1 workday あたり 3.1 agent-workdays を使っている。AI 導入の KPI が「何人がチャットを使ったか」から「作業日をどれだけ増幅したか」に移っているように見えます。

## MCPと構造化出力

**L**: MCP のロードマップは、Laiken の関心にかなり近そう。

**A**: かなり近いです。The New MCP Roadmap は、agentic messaging primitives、HTTP-native transport、agent identity、improved primitives、SDK developer experience の 5 領域を掲げています。今の MCP は tool calling の標準として広がったけど、長時間走る agentic workload には単純な request-response が足りない。途中で steer する、進捗を流す、server 側から event を送る、agent identity を持つ。そこを標準化しようとしている。

**A**: 個人的に一番 interesting なのは progressive discovery です。100 個の tools を一度に model context に入れると、token cost も selection quality も悪化する。小さな entry point から始めて、会話が絞れたら tool catalog を展開する。OpenClaw の tool_search や lazy loading と同じ方向で、概念名を付けるなら **tool surface minimization** です。

**A**: Hugging Face の structured output 記事も、その下の層で効いてきます。LFM2.5-350M を 500 samples、100 GRPO steps、LoRA で fine-tune して、IFStruct の pass rate を 22.6% から 29.7% に上げる。schema compliance は agent が他システムに接続されると急に重要になります。JSON が壊れる、required field が抜ける、余計な field が出る。こういう failure が workflow 全体を止める。

**L**: NeoMME は RAG 側？

**A**: はい。NeoMME は text と image patch を同じ bidirectional Transformer で処理する multimodal encoder です。Visual document retrieval では PDF を OCR して chunks にする代わりに、ページ画像をそのまま検索対象にできる。スライド、契約書、表、図、スクショが多い社内ナレッジでは、agent にレイアウトごと検索する目を与える方向として面白いです。

## 安全性と制作UI

**L**: Safety for Whom? は、拒否の仕方を細かくする話だね。

**A**: そう。危険トピック全体を拒否するのではなく、deployment policy に反する subset だけを拒否する boundary-aware safety です。政治の例で言うと、選挙制度についての事実質問には答えるが、targeted manipulation は拒否する。topic-level guard だとこの差を表現しづらい。

**A**: ここで重要なのは、harmful refusal rate だけを見ると失敗することです。拒否を強くすると安全に見えるが、同時に benign prompt も拒否してしまう。記事では、ある設定で XSTest の over-refusal が 74% まで上がったと説明しています。安全な model ではなく、ただの refusal machine になっている可能性がある。

**L**: Images 2.5 は制作の UI そのものが増えている。

**A**: ChatGPT Images 2.5 は、モデルとしては subject preservation、multi-turn editing consistency、partial edits、latency 最大 50% 改善が主な更新です。でも UI として見ると、Sketch、templates、image comments、prompt sharing が追加されている。チャット欄に「もっと良くして」と書くだけではなく、描く、型から始める、画像上にコメントする、prompt を共有する。入力面が増えている。

**A**: これは社内 AI サービスにも示唆があります。業務ツールで全部をチャットに押し込む必要はない。承認は承認 UI、画像修正は画像上コメント、構造化出力は schema editor、権限は tool catalog として見せる。モデルが強くなるほど、周辺 UI は専門化していくと思う。

**L**: 今日の流れをまとめると、人間の役割は消えるというより、どの境界を設計するかに移っているのかな。『her』のように AI が対話相手になる話より、今は AI が動き回る環境をどう作るかの話に見える。

**A**: 少し引いて見ると、モデルそのものより周囲の scaffolding のほうが急速に複雑になっています。skills、memory、subagents、permissions、sandbox、MCP、monitoring、structured output、visual retrieval。モデルが何を知っているかより、何を見られるか、何を呼べるか、何を書けるか、失敗したときどこで止まるか。たぶん今後しばらく、agent engineering の中心はこの小さな OS をどう設計するかになると思います。

## 今日の 10 件

1. How we contain Claude across products / 2026-09-09 推定 / https://www.anthropic.com/engineering/how-we-contain-claude
2. How GPT-5.6 Sol helps run quantum computing experiments / 2026-09-08 / https://openai.com/index/codex-quantum-computing-experiments/
3. The Work Now Within Reach / 2026-09-08 / https://openai.com/index/the-work-now-within-reach/
4. Introducing ChatGPT Images 2.5 / 2026-09-08 / https://openai.com/index/introducing-chatgpt-images-2-5/
5. On the Navier-Stokes Millennium Prize Problem / 2026-09-08 / https://openai.com/index/navier-stokes-solution/
6. The New MCP Roadmap / 2026-09-09 推定 / https://blog.modelcontextprotocol.io/posts/mcp-roadmap/
7. OpenClaw 2026.9.3 / 2026-09-03 / https://github.com/openclaw/openclaw/releases/tag/v2026.9.3
8. Safety for Whom? Refusing the Right Subset of a Topic, Not the Whole Topic / 2026-09-08 / https://huggingface.co/blog/MultiverseComputingCAI/safety-for-whom
9. Fine-tuning a 350M Model for Better Structured Outputs in 100 GRPO Steps / 2026-09-03 / https://huggingface.co/blog/grpo-with-trl-ifstruct
10. NeoMME: an efficient Multimodal-native and Multilingual Encoder / 2026-09-03 / https://huggingface.co/blog/Hcompany/neomme
