---
title: "Tech Watch 2026-09-12: エージェントを支える基盤"
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

**L**: 今日は、モデルの新機能そのものより、その能力を仕事として成立させる周辺の仕組みが目立つ。長い実行を支えるcontext管理、生成コードを本番へ通す品質管理、データとpluginの中央管理。『アポロ13』で宇宙船だけでなく地上管制まで含めてシステムだったように、agentもモデル単体では語れなくなってきた。

今日の項目:

1. Hands-on with Claude（Anthropic）
2. Habitatの大規模ストレージ基盤（OpenAI）
3. OpenAI OneGov 2.0（OpenAI Academy）
4. OpenClaw 2026.9.4（OpenClaw）
5. SelfCompact（The Batch）
6. Claude Fable 5.1の独立評価（The Batch）
7. 音声認識モデル3種の比較（The Batch）
8. Claude生成コードの品質基準（Simon Willison）
9. AIを使ったDatasetteセキュリティ監査（Simon Willison）
10. OpenRouterのprovider routing（Simon Willison）

## 長時間agentのボトルネックは、文脈の量より区切り方

**L**: まずSelfCompactから。context windowを大きくすれば済む話ではない？

**A**: 面白いのはたぶんここで、SelfCompactは「何文字たまったか」だけではなく「いま作業のどこにいるか」を見ている。16,000 tokensごとにprobeを差し込み、subtaskが終わったか、明確な到達点へ進んでいるかを同じモデルに判定させる。途中の計算や調査をまだ使う局面なら圧縮しない。区切りなら、50,000〜100,000 tokensのtrajectoryを1,000〜3,000 tokensへ要約して続行する。

> The rubric approach introduces a new agentic design pattern: exposing a tool and giving the model explicit criteria for using it.
>
> The Batch

**A**: つまり新しいのは**compactionをagentのaction spaceに入れ、呼び出し条件をrubricにしたこと**です。fine-tuningも外部supervisorも要らない。IMO-AnswerbenchではQwen3-30B-A3Bが52.1%で、固定間隔の48.7%、圧縮なしの45.2%を上回った。BrowseComp-PlusでもGLM-4.7-Flashが54.1%、固定間隔50.0%、圧縮なし45.6%。単に「圧縮したい？」と聞くだけだと固定間隔並みに落ちたので、効いたのは要約器より判断基準らしい。

**L**: memory管理までモデルに任せる。ただし自由判断ではなく、チェックリストを渡す。

**A**: そう。かなり乱暴にまとめると、これは**context capacityからcontext controlへ**の移動に見える。長時間agentのharnessでは、圧縮、checkpoint、retry、評価をいつ実行するかが同じ種類の問題になる。AnthropicのHands-on with Claudeも、9月11日のサンフランシスコ回で参加者が実プロジェクトを持ち込みClaude Codeを使う形式でした。新しい製品発表ではないけれど、「一般論を聞く」から「自分のtaskとloopをその場で組む」へ学習の単位が変わっている。

## 本番品質はモデルの賢さではなく、検証経路で作る

**L**: Fable 5.1は高評価なのに、同じ日に「生成コードには人手以上の基準を」と出ている。矛盾しない？

**A**: むしろ整合している。The Batchの整理ではClaude Fable 5.1は、Artificial Analysisの総合指標でGPT-6 Astraと53点で並び、複数週のknowledge workを測るAA-Briefcaseや、44職種の経済的taskを扱うGDPval-AA v2で首位だった。Vals Indexでも68.83%で1位。ただしcost per taskは前世代Fable 5より約20%増え、一般利用では30日data retentionも残る。benchmark上の能力と、企業が運用できる条件は別軸です。

**A**: Boris Chernyの発言はさらに実務的で、AnthropicではClaudeが書いたproduction codeに対し、lint、大量のtest、Claude-driven E2E、日次fuzzing、自動code reviewとsecurity review、自動refactoringを重ねているという。新しくできるのは「Claudeに本番コードを書かせること」ではなく、**生成から検証までを連続したmachine workflowにすること**です。

**L**: Datasetteの監査は、その具体例に見える。

**A**: そう見える。Simon WillisonとAlex GarciaはClaude Fable 5.1、GPT-5.6、GPT-6 Astraで監査し、Datasette 1.0a39と0.65.4のsecurity fixesへつなげた。人間側も、片方が問題を再現するautomated testを書き、もう片方がfixを実装する形で分担した。二人の人間と異なるmodelのcoding agentが同じ問題を別経路で見る。これは「AIがレビューした」より、failure modeを重ねない**異種レビューharness**として見ると面白い。

:::message
公開Datasetteでpublic tableとprivate tableを混在させている場合、元記事はsecurity updateの適用を勧めています。
:::

## 中央サービスは、便利さと統制を同じ場所に集める

**L**: HabitatとOpenClaw 2026.9.4は規模が違う。それでも同じテーマ？

**A**: 数字から見るとHabitatはかなり極端です。

- 毎秒70 million超のrequest
- 週1 billion超の利用者
- ほぼ40の地域
- 500 petabytes超のdata

**A**: 最初はAzure Cosmos DBにつながるPython client libraryだった。ところがrouting変更を数十serviceへ配るたびに、feature flag、shadowing、bug fix、rollbackの調整が必要になった。そこで独立serviceへ切り出し、deployment、observability、access control、audit log、storageへの到達経路を中央化した。ここで新しくできるのは、各product teamを待たずに基盤改善を全体へ反映し、agent actorを含むアクセス制御を一つのchokepointで実施することです。

**L**: OpenClawの「Plugins in one place」も、小さいHabitatのようなものか。

**A**: 一つの見方としてはそうです。2026.9.4ではbundled pluginとClawHub pluginの発見、install、setup、settings、accessをControl UIのPlugins workspaceへ集約した。さらにprepared cloud sessions、失敗したupdateからの安全なrollback、terminal上の質問UI、長いdelegation後にもTalkへ最終結果を返す改善が入った。

\`\`\`text
plugin catalog → install → settings → access control
project snapshot → prepared worker → session start
update failure → compatibility check → rollback → gateway verification
\`\`\`

**A**: これ全部、同じ方向を向いている気がする。**distributed convenienceからcentralized control planeへ**です。便利なtoolを増やすほど、どこで見つけ、誰が使え、失敗時にどう戻すかを一か所で扱いたくなる。ただ、中央化は停止点も集中させる。Habitatがmulti-region reliabilityを積み、OpenClawがrollbackの適用条件を限定しているのは、その代償への回答でしょう。

**L**: OpenRouterの注意点もそこにつながる？

**A**: つながるけれど、少し違う警告です。同じmodel IDを単一endpointで呼べても、裏のproviderごとにserving software、最適化、vision対応、reasoning effortの解釈が異なる場合がある。自動fallbackは可用性を上げる一方、挙動の再現性を下げる。新しくできるのは \`provider.only\` で実行先を限定し、\`/endpoints\` で候補providerを列挙して、routingを検証可能にすること。meta-gatewayを置くならcatalogだけでなく、capabilityと実測結果も管理対象になる。

## 入力面と導入制度まで含めてAIサービスを設計する

**L**: 残る二つは、音声認識と政府導入。技術基盤から急に人の側へ戻る。

**A**: でもUIと運用の話としては連続しています。The Batchが比べたGemini 3.5 Transcribe、Muse Voice Transcribe、MAI-Transcribe-2は、どれも話者分離と多言語対応を持つ。価格はそれぞれ課金単位が違うけれど、概算ではGoogleが録音で約0.30ドル/時、streamingで約0.54ドル/時、Museが0.18ドル/時、Microsoftが年末まで0.10ドル/時。Microsoftは1時間の音声を10秒で処理できるとしている。

**A**: 何が新しいかというと、speech-to-textが単なる文字起こしから、agent workflowの**常時入力adapter**になってきた。Museは80msごとに音声をsoft tokenへ変え、難しい箇所では次の音声を待つadaptive delayを使う。チャット欄に人が整形済みpromptを書く前提ではなく、会議、通話、現場音声からtaskを起こすUIを設計しやすくなる。

**L**: OneGov 2.0は入力面ではなく、導入の摩擦を下げる話だね。

**A**: 9月14日のOpenAI Academy配信では、10月1日から対象となる米国の連邦・州・地方・部族政府に、ChatGPT、Codex、APIを月額license feeなし、最低commitmentなし、対象usage costの50%割引で提供する27か月契約を説明する。新しいのはmodel capabilityではなく、procurement、pricing、training、onboardingをpackageにした点です。日本時間では9月15日0:15開始なので、平日夜の視聴枠にも一応入る。

**L**: 『her』では声が自然になった瞬間に、OSが機能一覧ではなく関係の相手になった。現実では、その手前に権限、監査、価格、教育という地味な層がずいぶんある。人間の役割はどこに残る？

**A**: 少し引いて見ると、modelが賢くなるほど人間の仕事が消えるというより、設計対象が広がっている。contextをいつ圧縮するか、生成物をどのtest群へ通すか、provider差をどう固定するか、誰にどのtoolを見せるか、音声から何をtaskとして起こすか。たぶん今のagent engineeringは、modelへの指示作りより、**判断点と検証点をcontrol planeへ実装する仕事**に近づいています。

## 今日の10件

1. Hands-on with Claude — 2026-09-11  
   https://www.anthropic.com/events/build-with-claude
2. Rapidly scaling online storage to serve over 1 billion ChatGPT users — 2026-09-11  
   https://openai.com/index/scaling-storage-one-billion-users-part-one/
3. OpenAI OneGov 2.0: What Government Leaders Need to Know — 2026-09-14  
   https://academy.openai.com/public/events/openai-onegov-2-0-what-government-leaders-need-to-know-72u08jy54f
4. OpenClaw 2026.9.4 — 2026-09-11  
   https://github.com/openclaw/openclaw/releases/tag/v2026.9.4
5. A Tool for Better Context Management — 2026-09-11  
   https://www.deeplearning.ai/the-batch/a-tool-for-better-context-management
6. Fable Holds The Top Spot (For Now) — 2026-09-11  
   https://www.deeplearning.ai/the-batch/fable-holds-the-top-spot-for-now
7. Transcription Battles Heat Up — 2026-09-11  
   https://www.deeplearning.ai/the-batch/transcription-battles-heat-up
8. A quote from Boris Cherny — 2026-09-11  
   https://simonwillison.net/2026/Sep/11/boris-cherny/
9. Datasette 1.0a39 and 0.65.4 security releases — 2026-09-11  
   https://simonwillison.net/2026/Sep/11/datasette-security/
10. So you want to use OpenRouter? — 2026-09-11  
    https://simonwillison.net/2026/Sep/11/so-you-want-to-use-openrouter/
