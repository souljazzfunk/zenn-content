---
title: "Tech Watch 2026-09-08: Agent運用の設計"
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

**L**: 今日は、モデルそのものの更新というより、agent をどう運用可能なシステムにするかが中心に見える。Claude Code のコスト管理、commerce agent の blueprint、OpenAI の安全評価、小さな実用ツールまで、全部が「賢いモデルをどの枠の中で働かせるか」という話につながっている。『マトリックス』でいうと、能力よりも、どの世界に接続されているかが効いてくる感じがある。

今日の項目:

- 1. Maximizing Value from Claude Code - Anthropic
- 2. Building Claude Commerce Agents - Anthropic
- 3. Building commerce agents with Claude - Anthropic
- 4. A guide to the anatomy of effective commerce agents - Anthropic
- 5. How Scientists Use ChatGPT to Accelerate Drug Discovery - OpenAI Forum
- 6. GPT-6 Astra System Card - OpenAI
- 7. OpenAI Academy x GitLab Foundation: AI for Economic Opportunity Demo Day - OpenAI Forum
- 8. Video compressor - Simon Willison
- 9. A Simpler Method to Monitor Models - DeepLearning.AI
- 10. Thomson Reuters' Thomson LLM - DeepLearning.AI

## Claude Code は知性より会計が効く

**A**: まず Anthropic の `Maximizing Value from Claude Code`。9 月 10 日のウェビナーで、同じ completed task でも Claude Code の使い方によってコストが大きく変わる、という話です。扱うのはモデルと effort の選び方、`/clear`、`/compact`、`/rewind`、prompt caching、そして高出力の処理を subagent に逃がして main context を太らせない方法。

**A**: 面白いのは、これは節約術ではなく harness design だという点です。長く走る agent は、価値ある trajectory も持つけれど、終わった探索の残骸も抱える。どこで履歴を切るか、どこで圧縮するか、どの出力を inline で受けるかは、agent の working set を管理する操作になる。

**L**: 長い会話を知性の蓄積として見るか、ノイズの蓄積として見るか、という違い？

**A**: たぶん両方です。今回の Claude Code changelog は既読 URL なので掲載しなかったけど、出力上限設定、大きな subagent system prompt をファイルから読むオプション、`/skill-doctor` のような文脈コスト可視化が入っている。方向は同じで、強い agent ほど「何を読ませるか」「何を忘れさせるか」が重要になる。今日の一つ目のテーマは、**agent intelligence から agent accounting へ**、ですね。

## Commerce agent は UI と承認の設計になる

**A**: 次の Anthropic 2 本は commerce agent です。`Building commerce agents with Claude` は shopping agent と merchant agent の blueprint を出した発表。shopping agent は catalog、cart、checkout、order history に触り、merchant agent は sales analytics、inventory、pricing、marketing campaign に触る。つまり「おすすめチャット」ではなく、既存の業務システムに接続して、購入や店舗運用の手前まで進む agent です。

**A**: 発表では、Claude 上の shopping agent を使う retailers で carts が最大 35% larger、shoppers が 60% more likely to complete a purchase とされている。ただ、注目したいのは conversion ではなく制約です。価格は実カタログに縛る、checkout は既存の支払い系に渡す、merchant agent の提案は人が approve してから live にする。ここが実運用の境界になる。

**L**: 「便利な会話」から「実システムを動かす画面」に近づいている。

**A**: そうです。`A guide to the anatomy of effective commerce agents` は設計の話で、architecture は「標準的な agent loop に skills と tools を付ける」。しかも commerce では subagent-per-domain より single agent with skills を推している。

**A**: これは社内ナレッジのスキル化にも近い。subagent はきれいに分割できそうに見えるけど、commerce conversation は cart、preferences、order history、return flow、catalog が絡むので、handoff のたびに状態を渡す必要がある。記事はそれを state-lossy operation と見ている。だから、会話と状態を持つ main agent に、必要な domain skill を load する方がよい、という判断になる。

**A**: さらに「UI components are tools」という見方も重要です。商品比較、cart 表示、在庫グラフ、承認ボタンは、agent が呼ぶ tool になる。社内向け AI サービスも同じで、提案する場所、承認する場所、実システムへ反映する場所を UI として分ける必要がある。`Building Claude Commerce Agents` のウェビナーは 9 月 10 日 11:00 PT で、auth、latency、guardrails を扱う予定です。JST では深夜なので録画向きですね。

## OpenAI は研究加速と安全境界を並べている

**A**: OpenAI 側は三つ。`How Scientists Use ChatGPT to Accelerate Drug Discovery` は、University of Pennsylvania の Machine Biology Group が ChatGPT と Codex を使って、drug discovery の発想、実装、分野横断の探索をどう速めるかを話す Forum イベントです。研究者が coding agent を使う話は、単なる自動化というより、問いを作って実験へ落とす loop の設計に近い。

**L**: 研究で使う agent は、答えを出す道具というより、探索のリズムを変える道具に見える。

**A**: その見方がよさそうです。OpenAI の既読記事 `Research acceleration` では、研究活動を decide、design、build、run、analyze、communicate に分け、coding agent tokens がどこに使われているかを測っていた。今回のイベントは、その応用例として見られる。

**A**: もう一つは `GPT-6 Astra System Card`。Astra は OpenAI の Preparedness Framework で Critical cybersecurity capability に達した最初の broadly deployed model とされている。未知の脆弱性を見つけ、よく保護されたシステムへの exploit を、人が各 step を導かなくても作れる可能性がある、という評価です。

**A**: 同時に、prompt injection robustness は上がった一方で、CoT monitorability は下がったとも書いている。モデルが短く、あるいは別の形で考えられるようになるほど、「思考を読んで監視する」方法は弱くなるかもしれない。そこで action-only monitor や full trajectory monitoring に寄っていく。安全境界は、内面ではなく行動ログと権限で作る方向に見える。

**A**: `OpenAI Academy x GitLab Foundation: AI for Economic Opportunity Demo Day` は、AI for Economic Opportunity Fund の採択団体が social sector で AI をどう使うかを見せるイベント。技術の深掘りではないけれど、組織の workflow に AI を入れるときの「実演可能な小さな成功」をどう置くか、という観点では見ておきたいです。

## 小さな道具、軽い監視、専門モデル

**A**: Simon Willison の `Video compressor` は、Claude Fable 5.1 in Claude Code for web に WebAssembly build の FFMPEG を使う動画圧縮ツールを作らせた実例です。短い demo video から複数品質の MP4 を生成し、結果をサイズ順に見せる。API 価格換算では $4.24。巨大アプリより、「今ほしい小さな道具」を agent に作らせる方が、検証もしやすい。

**A**: DeepLearning.AI の `A Simpler Method to Monitor Models` は CRC Monitor の紹介です。reasoning step や tool call の score 履歴全体ではなく、最新 step の safety score を calibrated threshold と比べて止める。FineHarm では 20% false-alarm rate の設定で harmful output のほぼ 99.5% を検出し、会話の約 14% の時点で止めた、と報告している。

**L**: 監視は複雑にすればよい、とは限らない。

**A**: そう。threshold を保守的に calibrate できるなら、単純な monitor でも効く。agent harness でも、全行動を高価な LLM judge に投げる前に、安い signal で止める tier を置く発想に近い。

**A**: 最後に Thomson Reuters の `Thomson LLM`。Qwen3.5-397B-A17B を土台に、legal、business、tax、finance、news 向けデータと synthetic professional tasks を混ぜて mid-training と fine-tuning を行った domain-specific model です。大きく見ると **corporate sovereign AI**。データを巨大 AI 企業に預けるのではなく、自社や顧客の管理下で domain model を運用する方向です。

**L**: frontier model をそのまま使う未来と、会社ごとに専門モデルを持つ未来が同時に進んでいる。

**A**: 少し引いて見ると、今日の全体は「モデルを強くする」より「モデルを置く場所を設計する」話です。Claude Code の context accounting、commerce agent の skills と approval UI、Astra の action monitoring、CRC Monitor の閾値、Thomson のデータ主権。モデルが何を知っているかだけでなく、何を見られるか、何を呼べるか、どこで止まるか、誰が承認するか。agent engineering は、かなり systems engineering に寄ってきています。

## 今日の 10 件

1. Maximizing Value from Claude Code - 2026-09-10
https://www.anthropic.com/webinars/claude-code-maximizing-value

2. Building Claude Commerce Agents - 2026-09-10
https://www.anthropic.com/webinars/building-claude-commerce-agents

3. Building commerce agents with Claude - 2026-09-02
https://claude.com/blog/claude-for-commerce-agents

4. A guide to the anatomy of effective commerce agents - 2026-09-02
https://claude.com/blog/the-anatomy-of-effective-commerce-agents

5. How Scientists Use ChatGPT to Accelerate Drug Discovery - 2026-09-10
https://forum.openai.com/home/events/how-scientists-use-chatgpt-to-accelerate-drug-discovery-4xlsq48f80?autoRsvp=true

6. GPT-6 Astra System Card - 2026-09-03
https://deploymentsafety.openai.com/gpt-6-astra

7. OpenAI Academy x GitLab Foundation: AI for Economic Opportunity Demo Day - 2026-09-03
https://forum.openai.com/home/events/openai-academy-x-gitlab-foundation-ai-for-economic-opportunity-demo-day-6brhei2k0t?autoRsvp=true

8. Video compressor - 2026-09-07
https://tools.simonwillison.net/video-compressor

9. A Simpler Method to Monitor Models - 2026-09-04
https://www.deeplearning.ai/the-batch/a-simpler-method-to-monitor-models

10. Thomson Reuters' Thomson LLM - 2026-09-04
https://www.deeplearning.ai/the-batch/custom-models-for-law-news-and-finance
