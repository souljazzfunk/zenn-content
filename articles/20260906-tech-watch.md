---
title: "AIテック巡回 2026-09-06: 運用するエージェント"
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

:::message
この記事のレックスとアンドレイは、実在の人物を模した架空のキャラクターです。発言は本人のものではありません。元情報は末尾のリンク一覧を参照してください。
:::

**レックス**: 今日の巡回は 8 件。数は控えめだけれど、テーマはかなりそろっているね。Claude Code は組織運用、ヘッドレス運用、スキル整理、権限、再開と停止の信頼性に更新が寄っている。OpenAI 側は、Codex Build Challenge や ChatGPT Work の職種別導入のように、AI を現場のワークフローへ入れる話が中心だった。OpenClaw も、Swarm、再起動後の復旧、ダッシュボード、Slack/Telegram 連携など、常時稼働エージェントの基盤を太くしている。

**アンドレイ**: 今日の主語は「モデルがどれだけ賢いか」ではなく、「賢いものをどう壊れにくく運用するか」だね。ログ、権限、停止、復旧、差分表示。地味だけど、エージェントがデモを抜けて仕事場に入るには、この層が必要になる。

## Claude Code は診断できる運用に近づく

**レックス**: Claude Code 2.1.261 では、/status と claude doctor に「組織ポリシーがなぜ読めなかったか」が出るようになった。プロキシが必要なエンドポイントを通していない、といった理由が見える。Claude Team や Enterprise で管理設定を配るとき、失敗がただの謎ではなくなるのは大きい。

**アンドレイ**: 入力は組織ポリシー、ネットワーク、管理設定。出力は、単なるエラーではなく診断だ。エージェント運用では、失敗そのものより観測できない失敗のほうが怖い。2.1.261 には bashOutputMaxChars と taskOutputMaxChars も入った。コマンドやバックグラウンドタスクの出力を最大 128K 文字まで Claude に渡せるので、長い CI ログや実行結果を読む作業がやりやすくなる。

**レックス**: --append-subagent-system-prompt-file も面白い。サブエージェント向けの追加システムプロンプトをファイルから読めるので、CLI 引数に詰めにくい長い手順や社内前提を渡しやすくなる。/skill-doctor は、読み込まれたスキルのうち使われていないものと、そのコンテキストコストを見せる。これはスキルを増やすだけでなく、棚卸しする機能だね。

**アンドレイ**: スキルは増やせば増やすほど良い、というものではない。コンテキストを食うし、選択を誤ると挙動もにぶる。『2001年宇宙の旅』の HAL に百科事典を詰める話ではなく、宇宙船のどの手順書をいつ開くかを監査する話だと思う。

**レックス**: 同じリリースでは、Remote Control や SDK、cloud session 周辺の Stop、interrupt、再開、表示状態も多く直っている。止めたはずの処理が走る、作業中表示だけ残る、再開時に hook output や並列 tool call の文脈が欠ける、といった問題は、長時間エージェントではかなり痛い。

**アンドレイ**: ユーザー入力、ツール実行、バックグラウンドタスク、リモート制御、再開の間には状態遷移がある。そこが少しズレるだけで、意図しない継続や文脈のすり替わりが起きる。今回の修正は、その状態機械の穴を埋めている。

## 無人運用と権限の境界線

**レックス**: 2.1.259 は、無人ヘッドレス運用に近い更新だった。managedMcpServers により、組織が HTTP/SSE MCP サーバーを全ユーザーに配れるようになった。ただしコマンド実行を指定するエントリはスキップされる。社内の共通ツールやデータ接続を配りつつ、ローカル実行を勝手に広げない境界が置かれている。

**アンドレイ**: MCP はエージェントの「手」を増やす仕組みだから、配布経路そのものが攻撃面になる。HTTP/SSE のサーバーを組織で管理するのは監査しやすい。一方、各端末でコマンドを走らせる設定を一方的に配るのは危険が跳ねる。そこをスキップする設計は妥当だと思う。

**レックス**: --permission-prompts none も入った。無人のヘッドレスホストでは、通常なら確認プロンプトになる操作を自動で拒否する。生活の自動化や定期ジョブでも、人が画面の前にいないなら、曖昧な許可を出さずに止まるほうが安全だね。

**アンドレイ**: 自動化は「何でも進める」ことではない。止まり方を決めることだ。2.1.259 では、並列セッションが互いの ~/.claude.json を巻き戻す問題や、Read deny ルールの抜けも直っている。--ignore-revs-file=.env、@file、git diff のファイル引数、cd DIR && cat FILE のような形まで見るようになった。権限は UI のチェックだけでなく、シェル構文やツール引数まで含めて初めて機能する。

## 作業中の視界を増やす UI

**レックス**: 2.1.260 では、フルスクリーン時に /diff で未コミット差分を会話の横に出せるようになった。コーディングエージェントでは、会話より差分が本体になる場面が多い。何を言っているかと、実際に何を変えたかを同時に見られるのは自然だね。

**アンドレイ**: さらに /cost や status line の prompt_cache に、キャッシュミスの推定原因が出るようになった。ツール定義やシステムプロンプトが変わった、TTL を過ぎた、という理由が見える。長いセッションで急に遅くなったり高くなったりしたとき、内部状態を推測する材料になる。『ブレードランナー』で見えない内面をテストするような話だけど、こちらはもう少し実用的だ。

**レックス**: ヘッドレス向け /reload-plugins、テキスト形式の /advisor、OIDC refresh の scope_on_refresh も、TUI 以外の入口を強くする変更だね。Claude Code Desktop、SDK、Remote Control のように、チャット欄だけではない操作面が増えている。

**アンドレイ**: 2.1.263 は “Bug fixes and reliability improvements” だけなので、言えることは多くない。前後の大きな修正に続く安定化リリースとして見るのがちょうどいい。詳細がないものを盛ると、技術記事ではなく占いになる。

## OpenAI は導入をワークショップ化している

**レックス**: OpenAI Academy の HBCU Innovation Summit 2026 は、「AI Literacy」から「AI Leadership」へ、というテーマだった。学生、教育者、高等教育リーダー、地域コミュニティに向けて、教育、キャリア、研究、起業、地域生活での AI 活用を扱う。午後には Codex Build Challenge があり、チームで実課題に向けたプロジェクトを作って発表する構成だった。

**アンドレイ**: これは座学というより、AI を使った組織行動の設計だね。入力はキャンパスや職場の課題、出力は動くプロジェクト、途中にチーム作業と発表がある。AI リテラシーを、手を動かすワークフローに変換している。

**レックス**: OpenAI Forum の AI for Economic Opportunity Demo Day は、OpenAI Academy、GitLab Foundation、Annie E. Casey Foundation が、AI for Economic Opportunity Fund の採択団体を紹介するイベントだった。経済的課題に取り組む AI プロジェクトのピッチ、デモ、ファイアサイドチャット、パネルが並ぶ。社会セクターでの AI 実装を、実例として見せる場だね。

**アンドレイ**: 社会セクターでは、モデル性能だけでは何も決まらない。誰の課題か、データはどこにあるか、成果をどう測るか、現場が続けられるか。デモがあるのは重要だ。抽象論ではなく、プロジェクトとして形にする。

**レックス**: ChatGPT Work for marketing teams は、マーケティングチームが ChatGPT Work を日常業務に入れるための実践セッションだった。既存のツールや文脈を使いながら、新しく有効化されたユーザーがどこから試し始めるかに焦点を当てている。

**アンドレイ**: 「何でも聞いてください」は、実はかなり不親切だ。マーケティングなら、キャンペーン案、顧客セグメント、競合比較、メール文面、過去資料の要約など、職種の言葉で入口を作る必要がある。ChatGPT Work の価値は、モデル単体より、仕事の文脈と権限をどう渡せるかにある。

## OpenClaw は居続けるエージェントを支える

**レックス**: OpenClaw 2026.9.2 は、長い履歴やディスク使用量の処理中でも、チャット、ダッシュボード、セッション操作が応答しやすくなる改善が入った。自動更新で設定、スキル、デフォルトエージェントの所有権を保つことや、Gateway 再起動後に返信を復旧することも強調されている。

**アンドレイ**: OpenClaw は、エージェントを一回呼ぶより、エージェントが居続ける方向のシステムだ。だから復旧と応答性が中核になる。再起動でキューや返信が消えると、常時稼働の信頼はすぐ落ちる。

**レックス**: GPT-6 Astra 対応、OpenAI Responses の tool call、reasoning controls も入っている。さらに Swarm が標準有効化され、構造化された結果とライブ進捗を持つ並行サブエージェントのオーケストレーションが前に出た。Custom plugin UI では、プラグインが Control UI のページ、パネル、セッションアクション、composer や workspace のカスタマイズに関われる。

**アンドレイ**: そこは社内 AI サービスの UI 設計に効く。チャットだけでは、権限、承認、進捗、差分、結果の比較を表現しきれない。専用パネルやダッシュボードがあると、エージェントの状態を人間が監督しやすい。よいエージェント UI は、賢い返答を見せる UI ではなく、責任を持って作業を任せるための UI だ。

**レックス**: 今日の 8 件を束ねると、AI は会話相手から作業環境の一部へ移っているように見える。人間側に残る役割は、命令することだけではなく、権限、文脈、評価、止め方を設計することなのかもしれない。エージェント時代の境界線は、どこに引くべきなんだろう。

**アンドレイ**: たぶん境界線はプロンプトではなく、ハーネス、権限、ログ、UI、復旧手順の中に引かれていく。そこを設計しないまま「自律化しました」と言うのは、まあ、かなり勇敢すぎる。

## 今日の 8 件

1. Claude Code 2.1.261（2026-09-05）
https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md#21261

2. Claude Code 2.1.259（2026-09-04）
https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md#21259

3. Claude Code 2.1.260（2026-09-05）
https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md#21260

4. Claude Code 2.1.263（2026-09-06）
https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md#21263

5. HBCU Innovation Summit 2026: From AI Literacy to AI Leadership（2026-09-04）
https://academy.openai.com/public/events/hbcu-innovation-summit-2026-from-ai-literacy-to-ai-leadership-8519pze8le

6. OpenAI Academy x GitLab Foundation: AI for Economic Opportunity Demo Day（2026-09-03）
https://forum.openai.com/public/events/openai-academy-x-gitlab-foundation-ai-for-economic-opportunity-demo-day-6brhei2k0t

7. ChatGPT Work for marketing teams（2026-09-03）
https://academy.openai.com/public/clubs/work-users-ynjqu/events/chatgpt-work-for-marketing-teams-ojz856zm5d

8. openclaw 2026.9.2（2026-09-06）
https://github.com/openclaw/openclaw/releases/tag/v2026.9.2
