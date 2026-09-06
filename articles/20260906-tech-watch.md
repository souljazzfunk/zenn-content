---
title: "Tech Watch 2026-09-06: エージェント運用基盤"
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

**L**: 今日の Tech Watch は、派手なモデル発表というより、エージェントを長く・複数・組織で動かすための足場が中心だった。Claude Code は 4 本続けて、診断、権限、スキル、headless 運用の細部を詰めている。OpenAI 側は社会セクターのデモイベント、OpenClaw は常時稼働エージェントの基盤強化。『ブレードランナー』の雨の街みたいに、表の光より配線のほうが気になる日だと思う。

今日の項目:

1. Claude Code v2.1.263 - Claude Code 変更履歴
2. Claude Code v2.1.261 - Claude Code 変更履歴
3. Claude Code v2.1.260 - Claude Code 変更履歴
4. Claude Code v2.1.259 - Claude Code 変更履歴
5. OpenAI Academy x GitLab Foundation: AI for Economic Opportunity Demo Day - OpenAI Forum / Academy
6. openclaw 2026.9.2 - OpenClaw Releases

## Claude Code は「運用中に見える」方向へ

**A**: まず Claude Code の v2.1.261 がいちばん Laiken 向き。目立つのは 4 つ。

- `/status` と `claude doctor` に **Organization policy** の行が追加された
- `bashOutputMaxChars` と `taskOutputMaxChars` で、インラインに載せる Bash / Task 出力を最大 128K 文字まで上げられる
- `--append-subagent-system-prompt-file` で、巨大な subagent system prompt をファイルから読める
- `/skill-doctor` で、読み込まれたスキルのうち未使用のものとコンテキストコストを見られる

これ、全部「エージェントを使う」ではなく「エージェントを運用する」機能なんだよね。

**L**: `/skill-doctor` は、社内ナレッジのスキル化に直撃している感じがする。

**A**: そう。スキルは増やすほど便利になる一方で、コンテキストを食う。しかも「使われていないスキル」は、単に無駄なだけではなく、誤作動の可能性も少し増やす。今回の `/skill-doctor` は、スキルを作るフェーズから、棚卸しして剪定するフェーズに入ったサインだと思う。

> Added `/skill-doctor` to show which loaded skills go unused and what they cost in context

出典: Claude Code v2.1.261

**A**: もうひとつ重要なのが、組織ポリシーが読めなかった理由を表示するところ。企業環境ではプロキシ、TLS インスペクション、IdP、管理設定のどれかで詰まることが多い。以前は「なぜ効いていないのか」が見えにくかった。今回の変更で、少なくとも診断の第一声が具体的になる。

```bash
claude doctor
/status
```

**L**: エージェントが賢くなる話ではなく、人間が運用で迷子にならない話だね。

**A**: まさに。v2.1.263 は「Bug fixes and reliability improvements」だけの小型リリースだけど、v2.1.261 の直後に出ているので、実運用で見つかった粗さを閉じた更新として見るのが自然。こういうリリースは記事映えしない。でも毎日使う CLI では一番効くことがある。映画でいえば、主役ではなく編集と音響。雑だと全部が台無しになる。

## Headless と権限境界が硬くなる

**L**: v2.1.260 と v2.1.259 は、どこが大きい？

**A**: v2.1.260 は観測と制御。フルスクリーン中に未コミット差分を横に出す `/diff`、prompt cache miss の理由表示、headless セッション向け `/reload-plugins`、そして `/advisor` のテキスト操作が入った。

| バージョン | 新しく見えるもの | 効く場面 |
| --- | --- | --- |
| v2.1.260 | `/diff`、prompt cache miss 原因、headless `/reload-plugins` | 長時間コーディング、SDK、リモート操作 |
| v2.1.259 | `managedMcpServers`、`--permission-prompts none`、`claude plugin validate --json` | 組織配布、無人ホスト、CI 的検査 |
| v2.1.263 | 信頼性改善 | 直近更新後の安定化 |

**A**: `/diff` は、エージェントが何を書き換えているかを横目で追える。prompt cache miss の原因表示は、長いコンテキストや固定プロンプトを運用するときにかなり助かる。キャッシュが外れる理由が「ツール定義が変わった」「system prompt が変わった」「TTL を過ぎた」あたりに分解されるなら、コストと待ち時間の説明がしやすくなる。

**L**: v2.1.259 の `--permission-prompts none` は強い名前だね。

**A**: 強い。無人 headless ホストで、通常なら質問になる操作を自動で拒否する。つまり、人間がいないのにプロンプト待ちで固まる状態を避ける設計。これは生活の自動化や定期ジョブにも近い。常時稼働エージェントは、成功だけでなく「安全に失敗する」経路を持たないといけない。

```bash
claude --permission-prompts none
```

**A**: `managedMcpServers` も企業向き。組織が HTTP/SSE MCP サーバーをユーザーへ配れる。ただし command を実行する種類はスキップされる。ここはいい制約で、中央配布したいけど端末で任意コマンドを動かすのは怖い、という現実に合わせている。

> organizations can provide HTTP/SSE MCP servers to every user

出典: Claude Code v2.1.259

**L**: 権限の見せ方と、承認しない設計が同時に進んでいる。

**A**: うん。社内 AI サービスの UI でも同じで、「承認ボタンを置く」だけでは足りない。何が拒否され、何が自動で許され、どこが組織管理なのかを、運用者があとから説明できる状態にする必要がある。

## AI 活用は社会セクターのデモへ

**L**: OpenAI Academy と GitLab Foundation の Demo Day は、技術というより社会実装寄り？

**A**: そうだね。OpenAI Academy、GitLab Foundation、The Annie E. Casey Foundation が、AI for Economic Opportunity Fund の採択団体を紹介するイベント。時間は 2026-09-03 19:00-21:30 GMT、JST では 2026-09-04 04:00-06:30。Laiken の「ライブ視聴は JST 平日夜か土曜」という条件からするとリアルタイム視聴向きではないけど、イベントとしては対象期間内。

**L**: 何が新しい？

**A**: 新しいのは、AI 活用を「プロダクト紹介」ではなく「助成先の現場デモ」として見せているところ。内容は、経済課題に取り組む団体が AI をどう使うかを、ピッチ、fireside chat、パネルで見せる構成。たぶん見どころは、モデル性能ではなく、現場のワークフローに AI をどこで挟むか。

**A**: 社内導入でも同じで、AI の価値は単体のチャット性能だけでは決まらない。

- 既存業務のどこに入力面を置くか
- 誰が承認するか
- 出力をどのシステムへ戻すか
- 失敗時に誰へ戻すか

**A**: このイベントは社会セクター版の「業務フローへの AI 組み込み」の観察対象として見るといい。華やかなユースケース紹介より、助成プログラムが何を成果として見ているかのほうが重要だと思う。

## OpenClaw は常時稼働の足場を太くする

**L**: OpenClaw 2026.9.2 は量が多い。どこを見る？

**A**: まずハイライトは、チャット、ダッシュボード、セッション操作の応答性改善。長い transcript やディスク使用量の処理を Gateway のイベントループから逃がす方向で、直接ダッシュボード参照や durable history read が入っている。常時稼働エージェントでは、裏で重い履歴処理をしている間に表のチャットが詰まるのが一番つらい。

> keep chat, dashboards, and session interactions responsive while long transcripts and disk usage are processed

出典: openclaw 2026.9.2

**A**: 次に、Gateway 再起動後の返信復旧。active、queued、delegated replies を復元し、compaction と retry をまたいでも continuation instructions を保つ。これは cron、heartbeat、外部チャネル返信を混ぜる運用ではかなり重要。エージェントの品質は、モデルの賢さだけでなく「再起動後に話が飛ばないか」で決まる。

**L**: Swarm がデフォルト有効になったのも大きい？

**A**: 大きい。並行 sub-agent を構造化結果と live progress で扱う方向。マルチエージェントは、ただ人数を増やすとログが散らかる。必要なのは、誰が何をして、どの結果を親が採用したかを追えるハーネス。OpenClaw はそこに寄っている。

**A**: さらに GPT-6 Astra 対応、async tools、steering、`/think ultra`、Custom plugin UI、Slack rich replies、Telegram proxy media、cron jobs の final reply 保存などがある。並べるとこう。

| 領域 | 変更 | 何ができるようになるか |
| --- | --- | --- |
| モデル | GPT-6 Astra 対応 | OpenAI API-key / 対象アカウントで text・image・Responses tool calls を扱う |
| 並行実行 | Swarm デフォルト有効 | sub-agent の同時実行を標準の作業形にしやすい |
| UI | Custom plugin UI | プラグインが Control UI のページやパネルに出られる |
| 復旧 | replies survive restarts | 再起動をまたぐ返信・委任・キューの継続性が上がる |
| 運用 | settings without restart | agent、model、tool、channel などの設定反映が軽くなる |

**L**: チャット以外の UI 設計にもつながるね。パネル、ダッシュボード、承認、進捗。

**A**: そう。チャットだけで AI サービスを作る時期は終わりつつある。承認パネル、進捗カード、設定画面、セッション一覧、デバイス状態。そういう地味な UI が、長時間稼働エージェントの本体になる。『her』のような声だけの親密さとは別に、業務では配線図を見せる UI が必要になる。

## 小さな更新が示す次の形

**L**: 今日の 6 件を束ねるなら、テーマは「自律性」より「運用可能性」かな。

**A**: かなりそう。Claude Code は、スキル、MCP、権限、headless、診断の精度を上げている。OpenClaw は、再起動、長い履歴、複数エージェント、外部チャネル、UI パネルを整えている。OpenAI の Demo Day は、AI を社会セクターの実務へ埋め込む実例を見せている。

**A**: つまり今日の変化は「AI が答える」から「AI が組織の中で働き続ける」への移動。そのとき必要なのは、モデルの賢さだけではなく、境界、ログ、失敗時の戻り先、スキルの棚卸し、そして人間が納得できる UI。

**L**: 人間側の役割はどこに残る？

**A**: たぶん、目的を決めるところと、境界を設計するところ。エージェントが走るほど、人間はボタンを押す人ではなく、どこまで走らせるかを決める人になる。

## 今日の 6 件

1. Claude Code v2.1.263（2026-09-06・Claude Code 変更履歴）
https://github.com/anthropics/claude-code/releases/tag/v2.1.263

2. Claude Code v2.1.261（2026-09-05・Claude Code 変更履歴）
https://github.com/anthropics/claude-code/releases/tag/v2.1.261

3. Claude Code v2.1.260（2026-09-04・Claude Code 変更履歴）
https://github.com/anthropics/claude-code/releases/tag/v2.1.260

4. Claude Code v2.1.259（2026-09-03・Claude Code 変更履歴）
https://github.com/anthropics/claude-code/releases/tag/v2.1.259

5. OpenAI Academy x GitLab Foundation: AI for Economic Opportunity Demo Day（2026-09-04 JST・OpenAI Forum / Academy）
https://forum.openai.com/public/events/openai-academy-x-gitlab-foundation-ai-for-economic-opportunity-demo-day-6brhei2k0t

6. openclaw 2026.9.2（2026-09-06・OpenClaw Releases）
https://github.com/openclaw/openclaw/releases/tag/v2026.9.2
