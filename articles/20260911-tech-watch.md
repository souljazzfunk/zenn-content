---
title: "Tech Watch 2026-09-11: エージェント基盤の製品化"
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

**L**: 今日は、モデルの周囲にある実行環境、データ、画面、権限が前に出てきた。『ブレードランナー 2049』のように「賢い存在とは何か」を問うより先に、「どの扉の鍵を渡すか」を設計する段階に来たように見える。10件を通して、モデル単体より、その周囲の基盤が製品の差になっている。

今日の項目:

- 1. Detecting and countering misuse of AI: September 2026（Anthropic）
- 2. Introducing the Agents API（OpenAI）
- 3. Now everyone can put data to work（OpenAI）
- 4. Build more natural voice experiences with GPT‑Live‑1 in the API（OpenAI）
- 5. Introducing ChatGPT for Financial Services（OpenAI）
- 6. How a researcher uses Codex and ChatGPT to search for new antimicrobial molecules（OpenAI）
- 7. AI for Procurement Professionals: Move Faster Without Losing Compliance（OpenAI Academy）
- 8. Rebuilding AUTOMATIC1111 with Gradio Workflow（Hugging Face）
- 9. Native is now the future of mobile at Shopify（Simon Willison）
- 10. WeWorm（Simon Willison / Calif Research）

## harnessがAPIになる

**L**: Agents APIは、結局何を製品にした？

**A**: 面白いのはたぶんここで、OpenAIは「モデルを呼ぶAPI」ではなく、**Codexを長く働かせるharness**をAPIにした。タスク、モデル、道具、実行環境を渡すと、コンテキスト管理、道具探索、subagentの並列化、実行環境まで一つの系として動く。記事の冒頭はかなり直接的です。

> Useful agents need a powerful harness that manages context, uses tools efficiently, and coordinates subagents.

出典: OpenAI「Introducing the Agents API」

コンテキストウィンドウが近づけば自動compactionし、道具定義は必要なときだけ読む。道具callはコードで並列実行・連結・filterし、subagentは個別contextで動く。これ、一つの見方としては、**エージェントの知能からエージェント基盤へ**重心が移っている。

**A**: 実行場所も含む。OpenAI管理sandbox、自社infra、partnerのsandboxから選び、file、skills、プラグインを載せられる。public betaではAPI自体の追加料金はない。モデル更新ごとにharnessを組み直す負担をOpenAI側が引き取る一方、挙動のplatform依存は評価が必要です。

**L**: ShopifyがReact NativeからSwiftとKotlinへ戻る話も、同じ方向に見える。

**A**: かなり近い。2020年には「同じ機能を二度作らない」ためにReact Nativeを選んだ。でも今はコーディングエージェントが実装、プラットフォーム間の翻訳、テスト、レビューを相当量こなせるので、二つのネイティブコードベースを持つ費用が決定要因ではなくなったという。新しいのはエージェント機能そのものより、**software architectureの経済性が変わった**ことです。

人間の反復をエージェントが引き受けるなら、platform固有機能や性能を優先できる。ただし生成量が増えればreview対象も増える。二倍書けることと、二倍安全に運用できることは別です。

## 社内データを「会話の外」まで動かす

**L**: Dataエージェントと金融サービス版は、社内AIのUIとして何を変えた？

**A**: データエージェントは、承認済み情報源へ接続し、変化の原因を調べ、根拠付きの対話型ダッシュボードを作る。既存アカウントの表・行・列権限を適用し、意味層の指標定義も使う。Slackやemailで次の行動へ進む段階では承認を挟む。

入力が自然言語、途中成果がevidence付き分析、出力がdashboard、最後がapproved actionという流れです。チャット欄を豪華にしたというより、**analysis-to-action surface**を作ったと見る方が面白い。

**L**: ChatGPT for Financial Servicesは、その業界版？

**A**: 金融版は分野知識の置き方が深い。有料データをOpenAI側で索引化し、数字や主張を表・該当箇所まで出典で戻す。既存契約のentitlement連携、50以上のconnector、企業templateも扱う。

| 製品 | 主な入力 | 検証面 | 出力・実行 |
| --- | --- | --- | --- |
| Dataエージェント | 社内DB、文書、semantic layer | query根拠、既存の行・列権限 | dashboard、承認後の連絡・action |
| Financial Services | premium金融data、契約済みsource、社内資料 | 細粒度citation、監査ログ、情報隔壁 | valuation model、research note、pitchbook |

頻用dataを製品内へ組み込み、取得品質と権限をまとめて管理する。社内ナレッジ活用はpromptの中身より、source、entitlement、citation、templateを誰が管理するかの問題になっている。

**L**: 調達向けのAcademy配信は、その運用側を扱うのかな。

**A**: 9月16日2:00〜3:00 JSTの配信は、AIで調達と意思決定を速めつつcomplianceを保つ実践がテーマです。告知は短く具体的手法は未詳。ただ、企業導入では「誰がどのdataを読み、どのactionだけ人が承認するか」が中心になる。

## 入力面が音声とcanvasへ広がる

**L**: チャット以外の入口では、今日は音声とvisual workflowが出てきた。

**A**: Full Duplex Benchは従来より30 percentage points向上し、Speakでは学習者への割り込みが約80%減った。なぜ改善したのか。GPT‑Live‑1は、speech-to-text、LLM、text-to-speechを直列につなぐ構成ではなく、聞くことと話すことを一つのmodelで同時に扱う。割り込み、短い相づち、沈黙、背景音を会話のsignalとして処理し、必要な深い推論や道具callはGPT‑6 Astraなどのbackendへ委譲する。

音声front-endは1分0.05ドル。**低遅延の対話制御と重いtask実行を分離**した構成です。

**L**: GradioのWorkflow1111は、逆に構造を見せるUIだね。

**A**: 73ノード、11パイプラインでAUTOMATIC1111の主要機能を一枚のcanvasへ置いた。演算子はPython関数、モデル、別のGradio Space、データセットの行の4種類。text-to-image、image-to-image、検出からinpaint mask生成、背景除去、image-to-videoまでedgeでつなぐ。

個人的には、各出力ノードがREST接続先になり、同時にMCPの道具にもなる点が一番面白いです。

人はgraphを配線し、エージェントは同じgraphのtyped outputを道具として呼ぶ。一つのworkflow定義からUIとAPIを出す設計です。36 operatorのうち22はprocess内だけで動き、dataが外へ出るnodeを構造として読める。

## 人間が残すべき検証ループ

**L**: 抗菌物質探索と二つのセキュリティ事例では、人間の役割が対照的に出ている。

**A**: César de la Fuente研究室は、抗菌候補探索を年単位から時間単位へ短縮している。CodexとChatGPTは仮説、code、data前処理、分野間の橋渡しに使う。でも有効性、毒性、耐性は実験で確かめる。エージェントloopの外に**ground-truth experiment**がある。

**L**: Anthropicの報告では、そのloopが攻撃側にも使われた。

**A**: Anthropicが阻止した事例では、AI利用が質問応答から直接実行やオーケストレーションへ進んだ。検知されたmalwareを自動で変更・再ビルド・再配備するワークフローもあり、人間は標的設定、成果確認、Claude Code skillsの修正を担った。

かなり乱暴にまとめると、攻撃者も「specを書く人」と「harnessを調整する人」になっている。Anthropicは7分野の事例を公開し、発見した活動を停止してsafeguardを強化したとする。ただし報告は自社観測なので、全体頻度ではなく確認できた新しい手口として読むべきです。

**L**: WeWormは、さらに短い時間で成立した。

**A**: Calif Researchのdemoでは、WeChat通話を介してiOSとAndroidへ広がるzero-click wormについて、AI支援でbug発見と最初のRCE exploitまで約2日、worm構築にさらに1週間と報告している。被害者が通話へ応答する必要もない。研究者は「何を狙い、どう安全にtestするか」を人間の判断として残した。

ここは本当にすごい。同時に怖い。検知を入力、malware再生成を処理、未検知状態を停止条件にするloopには、静的signatureだけでは対抗しにくい。防御側もmonitoring、isolation、credential境界、再試行停止条件をharnessとして持つ必要がある。

**L**: 人間は最終判断者であり続けるのか。それとも、判断する場所自体を設計する人になるのか。

**A**: 少し引いて見ると、今日の10件は同じ方向を向いている。モデルが何を知っているかより、どのenvironmentで動き、どの道具を遅延loadし、どのdataをどの権限で読み、どのUIから指示され、どのevidenceを残し、どこで止まるか。人間の役割は毎回の操作から、loopの境界条件と検証手段を設計する方へ移っているように見える。まだ完全自動化ではなく、むしろ人間による承認をどこへ置くかがシステム工学の中心になってきた。

## 今日の10件

1. Detecting and countering misuse of AI: September 2026 — 2026-09-10  
   https://www.anthropic.com/threat-intelligence-report-september-2026
2. Introducing the Agents API — 2026-09-10  
   https://openai.com/index/introducing-the-agents-api/
3. Now everyone can put data to work — 2026-09-10  
   https://openai.com/index/put-data-to-work/
4. Build more natural voice experiences with GPT‑Live‑1 in the API — 2026-09-10  
   https://openai.com/index/introducing-gpt-live-1-in-the-api/
5. Introducing ChatGPT for Financial Services — 2026-09-10  
   https://openai.com/index/introducing-chatgpt-financial-services/
6. How a researcher uses Codex and ChatGPT to search for new antimicrobial molecules — 2026-09-10  
   https://openai.com/index/using-codex-chatgpt-to-search-for-new-antimicrobials/
7. AI for Procurement Professionals: Move Faster Without Losing Compliance — 2026-09-15  
   https://academy.openai.com/public/events/ai-for-procurement-professionals-move-faster-without-losing-compliance-hnxb1qpa6h
8. Rebuilding AUTOMATIC1111 with Gradio Workflow — 2026-09-10  
   https://huggingface.co/blog/gradio-workflow-1111
9. Native is now the future of mobile at Shopify — 2026-09-10  
   https://simonwillison.net/2026/Sep/10/shopify-react-native/
10. WeWorm — 2026-09-10  
    https://simonwillison.net/2026/Sep/10/calif-research/
