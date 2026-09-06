---
title: "Loop Engineeringで設計ドキュメントを作る: Agentic Orchestration Layer編（手順メモ）"
emoji: "🧭"
type: "tech"
topics:
  - "ClaudeCode"
  - "AIエージェント"
  - "設計"
  - "ドキュメント"
  - "開発プロセス"
published: false
---

#### AIが書きました🤖
この記事は、AIが書いたものを人間が確認してから投稿しています。

:::message
これは実施前の手順メモです。実際にループを回したあと、`ops/run-log.md`の記録をもとに本文へ書き換えます。
:::

# 何を作るのか

## 成果物

業務システムで使う**agentic orchestration layer**の設計ドキュメント。

このレイヤーは、次の3種類の知識源をAgentが横断的に使い、人間の監督下で高品質な成果物を作るための仕組みです。

- 既存のデータパイプライン
- ドメイン知識（まだ蓄積されていないものを含む）
- 必要に応じたWeb検索の調査結果

## ドキュメントのゴール

エンジニアにもビジネスメンバーにも、**誤解なく設計が伝わる**こと。

つまり、成果物の品質は「正しく書けているか」だけでなく、「2種類の読者が同じ理解に到達するか」で判定します。

## 今回の題材がLoop Engineeringに向いている理由

前回の記事ではCI失敗対応を最初の題材に勧めました。設計ドキュメントは一見それより曖昧ですが、次の点でループの題材になります。

- 成果物をセクション単位に分割できる（1回のループで1セクション）
- 読者が2種類いるため、「作る人と確認する人を分ける」原則をそのまま適用できる
- 「まだ蓄積されていないドメイン知識」があるため、Escalate（人への引き渡し）が必ず発生する

一方で、コードと違ってテストがありません。**ドキュメント向けの外部シグナルを自分で用意する**ことが、この実験の中心になります。

# 設計ドキュメントの目次（ターゲット）

ループの「Decide」で1件ずつ取り出す単位として、先に目次を固定します。

| # | セクション | 主な読者 | 完了に必要な根拠 |
|---|---|---|---|
| 1 | 目的とスコープ | ビジネス | 対象外を明記した境界 |
| 2 | 用語集 | 両方 | 本文で使う専門用語がすべて定義済み |
| 3 | 現状: 既存パイプラインと知識源 | 両方 | 実在するパイプラインへの参照（パス、テーブル名、ジョブ名） |
| 4 | 知識のギャップ: 未蓄積のドメイン知識 | 両方 | 「分かっていないこと」の一覧と、誰が埋めるか |
| 5 | 想定ユースケースと成果物の例 | ビジネス | 入力と出力の具体例 |
| 6 | アーキテクチャ概要 | エンジニア | Harness要素ごとの担当コンポーネント |
| 7 | 知識源への接続と信頼度 | エンジニア | パイプライン、知識ベース、Web検索それぞれの取得方法と信頼度ラベル |
| 8 | 人間の監督ポイント | 両方 | 誰が、どの時点で、何を承認するか |
| 9 | 品質基準と評価 | 両方 | 成果物の合否をどう判定するか |
| 10 | リスク、セキュリティ、コスト | ビジネス | 数値または上限 |
| 11 | 段階的導入計画 | 両方 | Phaseごとの出口条件 |
| 12 | 未決事項と意思決定記録 | 両方 | Needs human decisionの転記 |

6の「アーキテクチャ概要」は、前回の記事のHarness要素をそのまま設計の目次にします。

```text
Trigger / Scheduler / State / Agent / Judge /
Permissions / Retry & Stop / Human escalation / Observability
```

設計対象のorchestration layer自体がHarnessであり、それを作るためのループもHarnessである、という入れ子構造になります。

# 読者を2種類に分けるための書き方ルール

各セクションを次の固定構造にします。

```markdown
## N. セクション名

### この節が答える問い
（1〜2文）

### 要約
（非技術者向け。専門用語は用語集にあるものだけ）

### 詳細
（エンジニア向け。インターフェース、データ、制約）

### この節の根拠
（参照した既存資料のパス、Web調査の出典と取得日）

### 未決事項
（人の判断が必要なこと。なければ「なし」）
```

この構造にすると、後述するビジネス向けレビュアーは「要約」だけを、エンジニア向けレビュアーは「詳細」だけを重点的に見られます。

# ファイル構成

設計ドキュメント用に、別リポジトリ（または別ディレクトリ）を用意します。

```text
orchestration-design/
├── CLAUDE.md
├── .claude/
│   ├── skills/
│   │   ├── research/SKILL.md
│   │   ├── draft-section/SKILL.md
│   │   └── doc-check/SKILL.md
│   └── agents/
│       ├── researcher.md
│       ├── writer.md
│       ├── engineer-reviewer.md
│       └── business-reviewer.md
├── docs/
│   ├── design.md            # 成果物本体
│   ├── glossary.md          # 用語集（design.mdの2章と同期）
│   └── decisions.md         # 意思決定記録
├── research/
│   └── YYYY-MM-DD-<topic>.md  # Web調査と既存資料の読み取り結果
├── scripts/
│   └── doc-check.sh         # 機械的な検証
└── ops/
    ├── agent-state.md       # ループの状態
    └── run-log.md           # 記事化のための実験記録
```

`ops/run-log.md`は前回の記事にはなかったファイルです。**プロセス自体を記事にする**ため、各反復で「何を指示し、何が出て、何が失敗し、Harnessの何を変えたか」を残します。

# 手順

## Step 0. 完了条件を先に書く

ドキュメント全体のDefinition of Doneを、コマンドで確認できる形に落とします。

```text
Done means:
- docs/design.md に目次の12セクションがすべて存在する
- 各セクションが固定構造（問い、要約、詳細、根拠、未決事項）を持つ
- 本文中の専門用語がすべて docs/glossary.md に定義されている
- 既存パイプラインへの言及には、実在するパスまたは名前が付いている
- Web調査に基づく記述には、出典URLと取得日が付いている
- 未決事項が docs/decisions.md または ops/agent-state.md に転記されている
- scripts/doc-check.sh が exit 0 で終わる
- engineer-reviewer と business-reviewer の両方で Critical がゼロ
```

最後の2つ以外は、すべて`scripts/doc-check.sh`で機械的に確認します。

## Step 1. Manual Loop: 1セクションを人力で回す

自動化せずに、まず1セクション（推奨は「3. 現状」）をClaude Codeに書かせます。

```text
Write section 3 of docs/design.md.

Done means:
- the section follows the fixed structure in CLAUDE.md
- every pipeline mentioned has a real path or job name from the repo
- anything you could not confirm is listed under 未決事項, not stated as fact
- no files other than docs/design.md and research/ are changed
```

ここで確認したいことは、次の2点です。

- 「根拠のない記述」がどれくらい混ざるか
- ビジネス向け要約とエンジニア向け詳細を、同じ精度で書けるか

2〜3セクション回して、毎回同じ注意をしていることに気付いたら、Step 2へ進みます。

## Step 2. Repeatable Loop: ルールとSkillに移す

### CLAUDE.md

毎回伝えている制約を移します。ドキュメント版の「Error handling policy」に相当するのが、**根拠と用語のルール**です。

```markdown
# CLAUDE.md

## Deliverable

- The only deliverable is docs/design.md. Research notes go to research/.
- Every section uses the fixed structure: 問い, 要約, 詳細, 根拠, 未決事項.

## Two audiences

- 要約 must be readable by a business member with no engineering background.
- 詳細 must be specific enough for an engineer to start implementation.
- Use only terms defined in docs/glossary.md. If you need a new term,
  add it to the glossary in the same change.

## Evidence policy

- Never state something about the existing pipeline without a path,
  table name, or job name that exists in the repo.
- Never state something from web research without a URL and the date
  it was retrieved.
- If you cannot confirm a fact, write it under 未決事項 as a question.
  Do not guess and do not hedge it into the body text.

## Anti-bloat

- Prefer deleting or tightening text over adding caveats.
- Do not add "注意" or "補足" paragraphs to cover uncertainty. Use 未決事項.
- One concept, one term. Do not introduce synonyms.

## Safety

- Do not send anything to external services other than web search.
- Do not delete files. Do not modify research/ notes written in earlier runs.
```

### Skills

繰り返す手順は3つです。

`/research <topic>`: 既存資料の読み取りとWeb検索を行い、`research/`に出典付きで保存する。本文は書かない。

```markdown
---
name: research
description: Gather evidence for one design topic from the repo and the web.
allowed-tools: Read Grep Glob Bash WebSearch WebFetch
---

1. Search the repo for existing pipeline code, schemas, and docs about $ARGUMENTS.
2. Search the web only for what the repo cannot answer.
3. Write research/<date>-<topic>.md with:
   - Findings (each with path or URL and retrieval date)
   - Confidence: confirmed / likely / unknown
   - Open questions for humans
4. Do not edit docs/design.md.
```

`/draft-section <n>`: `research/`だけを根拠にセクションを書く。

`/doc-check`: `scripts/doc-check.sh`を実行し、結果を`ops/agent-state.md`に書く。

## Step 3. Verifiable Loop: ドキュメント用の外部シグナルを作る

ここがこの実験の核心です。テストの代わりに、次を`scripts/doc-check.sh`で機械的に確認します。

| 検査 | 実装の目安 |
|---|---|
| 12セクションの存在 | 見出しのgrep |
| 固定構造の存在 | 各セクション内の小見出し5つをgrep |
| 用語集との整合 | 本文中のカタカナ語、英語術語を抽出し、`glossary.md`に無いものを列挙 |
| パイプライン参照の実在 | 本文中のパス、ジョブ名を抽出し、対象リポジトリに存在するか確認 |
| Web出典の形式 | URLの直後に取得日があるか |
| 未決事項の転記 | 各セクションの未決事項が`agent-state.md`にも存在するか |
| 肥大化の抑制 | セクションあたりの文字数上限、「注意」「補足」「場合によっては」の出現回数上限 |

最後の行が、前回の記事で扱った「ループが静かに壊すもの」のドキュメント版です。コードにおける防御的try-catchは、ドキュメントでは**ヘッジ表現と注意書きの積み上げ**として現れます。読めば読むほど慎重に見えるが、何も断言していない文書になります。

完了条件付きの反復は、次のように書きます。

```text
/goal scripts/doc-check.sh exits 0 for section 3,
the section stays under 1500 characters,
no new caveat paragraphs are added,
and every 未決事項 item is also written to ops/agent-state.md
```

## Step 4. Delegated Loop: 書き手と2種類の読み手を分ける

subagentを4つ用意します。編集できるのは`writer`だけです。

| Agent | tools | 役割 |
|---|---|---|
| researcher | Read, Grep, Glob, Bash, WebSearch, WebFetch | `research/`を書く。本文は書かない |
| writer | Read, Grep, Glob, Edit | `research/`だけを根拠に本文を書く |
| engineer-reviewer | Read, Grep, Glob, Bash | 詳細の実装可能性、曖昧さ、根拠を見る |
| business-reviewer | Read, Grep, Glob | 要約だけを読み、理解できるか、判断材料が揃うかを見る |

business-reviewerの定義例です。

```markdown
---
name: business-reviewer
description: Review the 要約 blocks as a business stakeholder.
tools: Read, Grep, Glob
model: inherit
---

You are a business stakeholder with no engineering background.
Read only the 要約 and 未決事項 blocks of the given section.

Report:
- Critical: a sentence you cannot understand, or a term missing from the glossary
- Must fix: information you would need to make a decision but cannot find
  (cost, risk, who approves, what changes for your team)
- Nice to have
- Evidence reviewed

Do not read the 詳細 block to fill gaps. If the 要約 does not stand alone,
that is a finding. Do not edit files.
```

engineer-reviewerには、前回の記事のcode-reviewerと同じく「劣化の検出」を明示的に持たせます。

```markdown
Also check for loop-induced degradation:
- Hedged sentences that avoid committing to a design
- Caveats added instead of resolving an open question
- Synonyms for a term that already exists in the glossary
Flag these as "Must fix" even if doc-check passes.
```

ループは次の形になります。

```text
Decide: 次のセクションを1つ選ぶ
  ↓
researcher → research/<topic>.md
  ↓
writer → docs/design.md の1セクション
  ↓
scripts/doc-check.sh
  ↓
engineer-reviewer + business-reviewer（並列）
  ↓
Critical あり → writer へ差し戻し（最大3回）
Critical なし → 人が要約を読んで承認
  ↓
未決事項を ops/agent-state.md へ
```

2つのレビュアーは同じ差分を見るので、worktreeは不要です。writerが同時に複数セクションを書き始めたら、そのときにセクション単位でworktreeを分けます。

## Step 5. Escalate: 「まだ蓄積されていないドメイン知識」の扱い

この題材で最も重要なEscalateです。

researcherが`unknown`と分類したものは、writerが本文に書いてはいけません。代わりに次の3つに振り分けます。

| 分類 | 行き先 | 誰が埋めるか |
|---|---|---|
| 既存資料を探せば分かる | `ops/agent-state.md`のNext run | 次回のresearcher |
| 人に聞けば分かる | `ops/agent-state.md`のNeeds human decision | 人（ドメイン担当者） |
| まだ誰にも分からない | `docs/design.md`の4章「知識のギャップ」 | 設計上の前提として明記し、orchestration layerが将来取り込む対象にする |

3つ目が設計ドキュメントの内容そのものになる点が、この題材の面白いところです。「知らないこと」を隠さず設計に組み込むことで、ビジネスメンバーにも「この部分は今は決められない」ことが伝わります。

## Step 6. 人間が全文を読む地点を残す

セクション単位のループでは、セクション間の矛盾（用語の揺れ、スコープのずれ）を検出できません。

次の節目で、人間が差分ではなく`docs/design.md`全体を通読します。

- 1〜5章（ビジネス向けが多い前半）が揃ったとき
- 6〜9章（エンジニア向けが多い後半）が揃ったとき
- 12章まで揃ったとき

通読で見つかった構造的な問題は、`CLAUDE.md`か`doc-check.sh`に戻します。個別に直すのではなく、Harnessを直します。

## Step 7. Scheduled / Autonomous は今回は適用しない

このタスクは有限（12セクション）で、人の判断が頻繁に必要です。時間ベースの自動実行を入れる理由がありません。

前回の記事のExit Criteriaで言えば、**Delegatedまでで止める**のが正しい判断です。これも記事に書く価値のある結論として残します。

## Step 8. run-logから記事を書く

各反復のあとに`ops/run-log.md`へ追記します。

```markdown
## Run 7 (2026-08-30 10:15 JST) section 6

- Prompt: /draft-section 6
- doc-check: FAIL (glossary: "オーケストレータ" undefined)
- engineer-reviewer: Must fix 2 (Judge の担当が未定)
- business-reviewer: Critical 1 (要約が詳細を前提にしている)
- Harness change: CLAUDE.md に「要約は詳細を読まなくても成立すること」を追記
- Human decision: Judge を別モデルにするかは保留
```

記事の本文は、このログから次を抽出して作ります。

1. 最初のManual Loopで、根拠のない記述がどれくらい混ざったか
2. どのルールをCLAUDE.mdへ移したか、その順番
3. doc-check.shの検査項目が、どの失敗から生まれたか
4. business-reviewerが見つけた誤解の具体例
5. 「知識のギャップ」が設計にどう反映されたか
6. Delegatedで止めた理由

# チェックリスト

- [ ] 12セクションの目次と、各セクションの完了根拠が決まっている
- [ ] 固定構造（問い、要約、詳細、根拠、未決事項）がCLAUDE.mdに書かれている
- [ ] `scripts/doc-check.sh`が用語集、根拠、肥大化を検査する
- [ ] researcher / writer / 2種類のreviewerで、編集権限はwriterだけ
- [ ] `unknown`な知識の3分類と行き先が決まっている
- [ ] 人間が全文を通読する節目が3つ決まっている
- [ ] `ops/run-log.md`に毎回の結果とHarness変更を残している
