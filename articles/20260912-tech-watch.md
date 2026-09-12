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

**L**: 今日は、モデルの新機能そのものより、その能力を仕事として成立させる周辺の仕組みが目立つ。長い実行を支える**文脈管理**、生成コードを本番へ通す**品質管理**、データと**プラグイン**の**中央管理**。『アポロ13』で宇宙船だけでなく地上管制まで含めてシステムだったように、エージェントもモデル単体では語れなくなってきた。

今日の項目:

1. Habitatの大規模ストレージ基盤（OpenAI）
2. OpenAI OneGov 2.0（OpenAI Academy）
3. OpenClaw 2026.9.4（OpenClaw）
4. SelfCompact（The Batch）
5. Claude Fable 5.1の独立評価（The Batch）
6. 音声認識モデル3種の比較（The Batch）
7. Claude生成コードの品質基準（Simon Willison）
8. AIを使ったDatasetteセキュリティ監査（Simon Willison）
9. OpenRouterの提供事業者経路制御（Simon Willison）

## 長時間エージェントのボトルネックは、文脈の量より区切り方

**L**: まずSelfCompactから。コンテキストウィンドウを大きくすれば済む話ではない？

**A**: 面白いのはたぶんここで、SelfCompactは「何文字たまったか」だけではなく「いま作業のどこにいるか」を見ている。サブタスクが終わったか、明確な到達点へ進んでいるかを同じモデルに判定させ、途中の計算や調査をまだ使う局面なら圧縮しない。区切りならtrajectoryを要約して続行する。

| 処理 | トークン数 |
|---|---:|
| 確認間隔 | 16,000 |
| 圧縮前 | 50,000〜100,000 |
| 圧縮後 | 1,000〜3,000 |

> The rubric approach introduces a new agentic design pattern: exposing a tool and giving the model explicit criteria for using it.

出典: The Batch

**A**: つまり新しいのは、圧縮をエージェントのaction spaceに入れ、呼び出し条件を評価基準として明示したことです。追加学習も外部の監督役も要らない。

| ベンチマーク | 評価基準方式 | 固定間隔 | 圧縮なし |
|---|---:|---:|---:|
| IMO-Answerbench（Qwen3-30B-A3B） | 52.1% | 48.7% | 45.2% |
| BrowseComp-Plus（GLM-4.7-Flash） | 54.1% | 50.0% | 45.6% |

**A**: 両ベンチマークで評価基準方式が最も高い。単に「圧縮したい？」と聞くだけでは固定間隔並みなので、効果があったのは要約器より判断基準らしい。

**L**: メモリ管理までモデルに任せる。ただし自由判断ではなく、チェックリストを渡す。

**A**: そう。かなり乱暴にまとめると、これは**文脈容量から文脈制御へ**の移動に見える。

## 本番品質はモデルの賢さではなく、検証経路で作る

**L**: Fable 5.1は高評価なのに、同じ日に「生成コードには人手以上の基準を」と出ている。矛盾しない？

**A**: The Batchがまとめた評価と運用条件は次の通りです。

| 観点 | Claude Fable 5.1の結果 | 比較対象・条件 |
|---|---:|---|
| Artificial Analysis総合指標 | 53点 | GPT-6 Astraと同点 |
| AA-Briefcase | 1位 | 複数週の知識労働 |
| GDPval-AA v2 | 1位 | 44職種の経済的タスク |
| Vals Index | 68.83%、1位 | 独立評価 |
| タスクあたり費用 | 約20%増 | 前世代Fable 5比 |
| 一般利用のデータ保持 | 30日 | 運用条件 |
| 対象となるEnterprise顧客のデータ保持 | ゼロ | 現在利用可能 |

**A**: 面白いのはたぶんここで、能力評価の順位と費用・データ保持が別の列に並ぶ。これは何だ？ モデルの能力と本番で使える条件を別軸で検証する必要がある、ということだと思います。

**A**: Boris Chernyの発言はさらに実務的で、AnthropicではClaudeが書いた本番コードに対し、lint、大量のテスト、ClaudeによるE2E、日次fuzzing、自動コードレビューとセキュリティレビュー、自動リファクタリングを重ねているという。つまり、Claudeによるコード生成から検証までを機械的な作業フローとして重ねています。

**L**: Datasetteの監査は、その具体例に見える。

**A**: そう見える。Simon WillisonとAlex GarciaはClaude Fable 5.1、GPT-5.6、GPT-6 Astraで監査し、Datasette 1.0a39と0.65.4のセキュリティ修正へつなげた。人間側も、片方が問題を再現する自動テストを書き、もう片方が修正を実装する形で分担した。これは、障害形態の異なる複数のレビュー経路を組み合わせたものとして見ると面白い。

:::message
公開Datasetteで公開テーブルと非公開テーブルを混在させている場合、元記事はセキュリティ更新の適用を勧めています。
:::

## 中央サービスは、便利さと統制を同じ場所に集める

**L**: HabitatとOpenClaw 2026.9.4は規模が違う。それでも同じテーマ？

**A**: 数字から見るとHabitatはかなり極端です。

- 毎秒7,000万超のリクエスト
- 毎週10億人超に使われる製品を支える
- 約40地域
- 500ペタバイト超のデータ

**A**: 最初はAzure Cosmos DBにつながるPythonクライアントライブラリだった。ところが経路制御の変更を数十のサービスへ配るたびに、機能フラグ、影響を本番経路と分離して確認する処理、不具合修正、ロールバックの調整が必要になった。そこで独立サービスへ切り出し、配備、可観測性、アクセス制御、監査ログ、ストレージへの到達経路を中央化した。ここで新しくできるのは、各製品チームを待たずに基盤改善を全体へ反映し、エージェントを含むアクセス制御を単一の制御点で実施することです。

**L**: OpenClawの「Plugins in one place」も、小さいHabitatのようなものか。

**A**: 一つの見方としてはそうです。2026.9.4では同梱プラグインとClawHubプラグインの発見、導入、設定、アクセス制御をControl UIのPlugins画面へ集約した。さらに準備済みクラウドセッション、失敗した更新からの安全なロールバック、ターミナル上の質問UI、長い委任後にもTalkへ最終結果を返す改善が入った。

```text
プラグイン一覧 → 導入 → 設定 → アクセス制御
プロジェクトのスナップショット → 準備済みワーカー → セッション開始
更新失敗 → 互換性確認 → ロールバック → ゲートウェイ検証
```

**A**: これ全部、同じ方向を向いている気がする。**分散した利便性から中央の管理面へ**、と呼べそうです。便利な道具を増やすほど、どこで見つけ、誰が使え、失敗時にどう戻すかを一か所で扱いたくなる。ただ、中央化は停止点も集中させる。Habitatが複数地域での信頼性を積み、OpenClawがロールバックの適用条件を限定しているのは、その代償への回答でしょう。

**L**: OpenRouterの注意点もそこにつながる？

**A**: つながるけれど、少し違う警告です。同じモデルIDを単一の接続先で呼べても、裏の提供事業者ごとに推論用ソフトウェア、最適化、画像対応、推論量の解釈が異なる場合がある。自動的な代替経路への切り替えは可用性を上げる一方、挙動の再現性を下げる。実行先の固定と候補となる提供事業者の列挙は、次の形で指定できます。

```json
{
  "provider": {
    "only": ["<provider>"]
  }
}
```

```http
GET /api/v1/models/{author}/{slug}/endpoints
```

**A**: これにより経路制御を検証可能にする。私の見方では、メタゲートウェイを置くなら、一覧だけでなく機能と実測結果も管理対象にする必要があります。

## 入力面と導入制度まで含めてAIサービスを設計する

**L**: 残る二つは、音声認識と政府導入。技術基盤から急に人の側へ戻る。

**A**: The Batchが比べたGemini 3.5 Transcribe、Muse Voice Transcribe、MAI-Transcribe-2は、どれも話者分離と多言語対応を持つ。単価だけでなく課金単位と適用期間が異なります。

| サービス | 処理方式 | 概算単価 | 音声トークン変換間隔 | 適用期間・公称処理時間 |
|---|---|---:|---|---|
| Google | 録音 | 約0.30ドル/時 | 記載なし | 記載なし |
| Google | ストリーミング | 約0.54ドル/時 | 記載なし | 記載なし |
| Muse | 記載なし | 0.18ドル/時 | 80ミリ秒 | 記載なし |
| Microsoft | 記載なし | 0.10ドル/時 | 記載なし | 年末まで。1時間の音声に対して10秒 |

**A**: 面白いのはたぶんここで、なぜ文字起こしモデルがエージェントの作業フローを前提にしているのか。Museは音声を短い間隔で音声トークンへ変え、難しい箇所では次の音声を待つ適応的な遅延処理を使う。何が新しいかというと、音声認識が文字起こしに加え、エージェントの作業フローへ接続する入力手段として位置づけられている。会議、通話、現場音声をタスクの入力に使うUIにも応用できそうです。UIと運用の話として前節と連続しているように見えます。

**L**: OneGov 2.0は入力面ではなく、導入の摩擦を下げる話だね。

**A**: OpenAI Academyの配信では、OneGov 2.0の対象と契約条件を説明する。

| 項目 | 内容 |
|---|---|
| 対象 | 米国の連邦・州・地方・部族政府 |
| 契約開始 | 10月1日 |
| 月額ライセンス料 | なし |
| 最低利用額の約束 | なし |
| 対象利用料の割引 | 50% |
| 契約期間 | 27か月 |
| 配信日時 | 9月14日、日本時間9月15日0:15 |

**A**: 新しいのはモデルの能力ではなく、ChatGPT、Codex、APIについて、調達、価格設定、研修、導入支援を一体として提供した点です。

**L**: 『her』では声が自然になった瞬間に、OSが機能一覧ではなく関係の相手になった。現実では、その手前に権限、監査、価格、教育という地味な層がずいぶんある。人間の役割はどこに残る？

**A**: 少し引いて見ると、モデルが賢くなるほど人間の仕事が消えるというより、設計対象が広がっている。文脈をいつ圧縮するか、生成物をどのテスト群へ通すか、提供事業者による差をどう固定するか、誰にどの道具を見せるか、音声から何をタスクとして起こすか。たぶん今のエージェント開発は、モデルへの指示作りより、判断点と検証点を中央の管理面へ実装する仕事に近づいています。

## 今日の9件

1. Rapidly scaling online storage to serve over 1 billion ChatGPT users — 2026-09-11  
   https://openai.com/index/scaling-storage-one-billion-users-part-one/
2. OpenAI OneGov 2.0: What Government Leaders Need to Know — 2026-09-14  
   https://academy.openai.com/public/events/openai-onegov-2-0-what-government-leaders-need-to-know-72u08jy54f
3. OpenClaw 2026.9.4 — 2026-09-11  
   https://github.com/openclaw/openclaw/releases/tag/v2026.9.4
4. A Tool for Better Context Management — 2026-09-11  
   https://www.deeplearning.ai/the-batch/a-tool-for-better-context-management
5. Fable Holds The Top Spot (For Now) — 2026-09-11  
   https://www.deeplearning.ai/the-batch/fable-holds-the-top-spot-for-now
6. Transcription Battles Heat Up — 2026-09-11  
   https://www.deeplearning.ai/the-batch/transcription-battles-heat-up
7. A quote from Boris Cherny — 2026-09-11  
   https://simonwillison.net/2026/Sep/11/boris-cherny/
8. Datasette 1.0a39 and 0.65.4 security releases — 2026-09-11  
   https://simonwillison.net/2026/Sep/11/datasette-security/
9. So you want to use OpenRouter? — 2026-09-11  
    https://simonwillison.net/2026/Sep/11/so-you-want-to-use-openrouter/
