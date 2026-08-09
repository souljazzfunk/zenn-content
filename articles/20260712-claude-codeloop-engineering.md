---
title: "Claude Codeで始めるLoop Engineering"
emoji: "🔁"
type: "tech"
topics:
  - "ClaudeCode"
  - "AIエージェント"
  - "自動化"
  - "GitHub"
  - "開発プロセス"
published: true
---

#### AIが書きました🤖
この記事は、AIが書いたものを人間が確認してから投稿しています。

Claude Codeを使って「loopを設計する」とは、具体的に何を、どのようなコマンドやファイルで実装することなのでしょうか？

# Loop Engineering

## プロンプトする人から、ループを設計する人へ

Claude Codeを単発の実装支援として使う段階から、発見、実行、検証、記録を反復する運用システムとして使う段階へ。

ここで設計するのは「次に何を聞くか」ではなく、「どの条件で、何を実行し、何をもって止めるか」です。

- 対象: Claude Code
- 用途: 実装、CI対応、PR保守、定期トリアージ
- 設計単位: 1つの検証可能な成果

## Executive Summary

:::message
Loop Engineeringは、AIエージェントに繰り返し指示を出す運用ではありません。

人が担っていた「仕事を見つける、優先順位を付ける、実行させる、確認する、次を決める」を、小さく安全な反復システムに置き換える設計です。
:::

**Prompt Engineering**は、一回の出力を改善します。

**Loop Engineering**は、継続的に成果を出す仕組みを改善します。

ループの基本構造は、次のとおりです。

```text
Discover
  ↓
Decide
  ↓
Execute
  ↓
Verify
  ↓
Escalate
  ↓
Remember
  └────────→ 次のDiscoverへ
```

| 段階 | 役割 |
|---|---|
| Discover | CI、Issue、PR、ログから次の仕事を見つける |
| Decide | 対象外を除き、1件の小さな作業に絞る |
| Execute | 計画し、実装し、変更を限定する |
| Verify | テスト、ビルド、Lint、レビューで確認する |
| Escalate | 自動で閉じられない問題を人のトリアージへ送る |
| Remember | 結果と次の作業を会話の外に残す |

## 最初に押さえるべき3つの原則

### 1. 目的ではなく、停止条件を書く

「認証を直す」ではなく、次のように書きます。

> 対象テストが成功し、Lintが通り、変更範囲が制約内にある。

良いループは、AIが何をしたかではなく、どの条件を満たしたら停止するかで決まります。

### 2. 作る人と確認する人を分ける

実装者の自己評価だけに依存しません。

検証用の別エージェント、Stop hook、または人のレビューを置きます。

### 3. 会話を状態管理に使わない

会話は永続的な状態管理には向きません。

完了、失敗、保留、次の一手は、Markdownやチケットに残します。

# ループを構成する「5つ＋記憶」

Addy Osmaniの整理を、Claude Codeで実装できる部品に変換すると、次のようになります。

| 要素 | 役割 | Claude Codeでの実装例 |
|---|---|---|
| Automation | いつ、何を再実行するか | `/loop`、Routines、Desktop scheduled tasks、GitHub Actions |
| Worktree | 並列作業を隔離する | Git worktree、subagentの`isolation: worktree` |
| Skills | 繰り返す手順を固定する | `.claude/skills/<skill-name>/SKILL.md` |
| Connectors | 実際の作業環境へ接続する | MCP、GitHub、DB、Slackなど |
| Subagents | 実装、調査、レビューを役割分担する | `.claude/agents/*.md` |
| Memory | 会話の外へ状態を残す | Markdown、Issue、Linearなど |

## 最小ファイル構成

```text
repo/
├── CLAUDE.md
├── .claude/
│   ├── loop.md
│   ├── skills/
│   │   └── release-check/
│   │       └── SKILL.md
│   └── agents/
│       ├── fixer.md
│       └── code-reviewer.md
├── ops/
│   └── agent-state.md
└── .github/
    └── workflows/
        └── nightly-triage.yml
```

このうち、Claude Codeが規約や設定として読む対象は、主に次のファイルです。

- `CLAUDE.md`
- `.claude/loop.md`
- `.claude/skills/`
- `.claude/agents/`

`ops/agent-state.md`は、ループの状態を残すためにプロジェクト側で設けるファイルです。

# How to: 最小の検証ループを作る

## Step 1. 成果を1つに絞り、測定できる完了条件に変える

曖昧なTo Doを、そのままエージェントに渡しません。

良いループは「何をするか」より「何が確認できたら終わりか」で決まります。

完了条件には、次の要素を含めます。

- 実行するコマンド
- 期待する結果
- 変更範囲の制約
- 反復回数や時間の上限

```text
/goal npm test exits 0, npm run lint exits 0,
only files under src/auth and tests/auth are changed,
and stop after 12 turns
```

:::message alert
`/goal`の評価器は、独立してコマンドを実行するわけではありません。

Claudeが会話中で示したテスト結果やコマンド出力を材料に判定します。そのため、証拠を出力させる書き方が必要です。
:::

## Step 2. 変わりにくいルールを`CLAUDE.md`に置く

毎回必要な前提だけを、プロジェクトの常設コンテキストにします。

まず、プロジェクトのルートで`/init`を実行し、生成された`CLAUDE.md`を短く育てます。

ビルド、テスト、リポジトリ固有の制約だけを残します。

```markdown
# CLAUDE.md

## Commands

- Test: npm test
- Lint: npm run lint
- Typecheck: npm run typecheck

## Workflow

- For changes across multiple files, create a plan before editing.
- Run the narrowest relevant test first.
- Do not push, merge, deploy, or delete without explicit user approval.

## Repository rules

- Keep auth changes within src/auth and tests/auth unless the plan explains why.
- Update docs when public behavior changes.
```

`CLAUDE.md`は、長いプロンプトを保存する場所ではありません。

頻繁に変わらず、プロジェクト全体に適用されるルールだけを置きます。

## Step 3. 反復する手順をSkillにする

毎回説明している手順は、Skillにします。

Skillは次の場所に置きます。

```text
.claude/skills/<skill-name>/SKILL.md
```

ディレクトリ名がコマンド名になるため、次の例は`/release-check`で実行できます。

```markdown
---
name: release-check
description: Inspect a release PR and report actionable failures.
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash
---

1. Inspect the current PR and recent CI runs.
2. Run the relevant test and lint commands.
3. Classify findings as:
   - fix now
   - needs human decision
   - no action
4. Write a concise update to ops/agent-state.md.
5. Never push, merge, deploy, or delete.
```

デプロイ、送信、削除など、副作用がある手順には`disable-model-invocation: true`を付けます。

これにより、ClaudeがそのSkillを自動実行することを防ぎます。

## Step 4. 実装者とレビュー担当を分ける

「自分で書いたコードを、自分で採点する」構造を避けます。

Claude Codeのカスタムサブエージェントは、MarkdownとYAML front matterで定義します。

レビュー担当には編集権限を付けず、差分、テスト、リスクだけを評価させます。

```markdown
---
name: code-reviewer
description: Review changed code for correctness, security, and test evidence.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a strict reviewer.

1. Run git diff and inspect only changed files.
2. Check that the stated acceptance criteria have evidence.
3. Identify root-cause risks, security issues, and missing tests.
4. Return findings in this format:
   - Critical
   - Must fix
   - Nice to have
   - Evidence reviewed

Do not edit files. Do not approve based on claims alone.
```

実装用のサブエージェントは`Edit`を持てます。

並列で変更させる場合は、forkしたサブエージェントに`isolation: worktree`を設定し、作業ディレクトリを分離します。

## Step 5. 状態をMarkdownに残す

セッションの記憶ではなく、リポジトリの記録に次の仕事を渡します。

```markdown
# ops/agent-state.md

## Last run

- 2026-06-20 09:00 JST
- Trigger: nightly triage
- Result: CI failure reproduced in tests/auth/session.test.ts

## Completed

- [x] Reproduced failure
- [x] Added regression test
- [x] Fixed token refresh path
- [x] npm test and npm run lint passed

## Needs human decision

- [ ] Confirm whether the session timeout should remain 30 minutes.

## Next run

- Check review comments on PR #123.
- Do not create another PR for this issue.
```

状態ファイルには、次の情報を残します。

- 何を試したか
- 何が通ったか
- 何を人に渡すか
- 次に何をするか

ファイル名は任意です。

重要なのは、状態を会話の外に置くことです。

## Step 6. 時間で回すものと、完了するまで回すものを分ける

同じ自動化でも、実行間隔と停止条件は別に設計します。

`/loop`は、開いているClaude Codeセッション中の短期ポーリングに向いています。

`/goal`は、証拠を伴う完了条件が満たされるまで、同一セッションを進めるために使います。

```text
# 今開いているセッションで、10分ごとにPRを確認する
/loop 10m /release-check

# 条件を満たすまで修正と検証を続ける
/goal npm test exits 0 and npm run lint exits 0,
then summarize the exact commands and outputs
```

:::message alert
`/loop`はセッションスコープです。

ターミナルを閉じれば動かず、定期タスクは作成から7日で失効します。

夜間トリアージや毎日のCI保守など、セッションに依存しない運用には、Routines、Desktop scheduled tasks、またはGitHub Actionsを選びます。
:::

# 実務で使える最小ループ

最初の対象としては、機能開発全体ではなく、CI失敗またはPR保守が適しています。

入力と検証の境界が明確で、AIに任せる範囲を限定しやすいためです。

## PR health loop

```text
定期実行
  ↓
PR、CI失敗、レビューコメントを収集
  ↓
release-check Skillが状態を分類
  ↓
修正可能な小さい問題だけworktreeで修正
  ↓
別のcode-reviewerが差分と証拠を検証
  ↓
人がPRを確認
  ↓
判断が必要なものは状態ファイルへ残す
```

具体的には、次の流れです。

1. 定期実行が、現在のPR、CI失敗、未解決レビューコメントを収集する。
2. `/release-check`が、証拠付きで状態ファイルを更新する。
3. 小さく再現可能な不具合だけを、隔離されたworktreeで修正する。
4. 実装者とは別の`code-reviewer`が、変更とテスト証拠を確認する。
5. テストが成功し、レビューでCriticalがなければ、人がPRを確認する。
6. 判断が必要なものは`Needs human decision`に残し、自動マージはしない。

## ループ設計チェックリスト

- [ ] 開始条件が明確である
- [ ] 1回のループで扱う変更範囲に上限がある
- [ ] 完了をテストやコマンド出力で示せる
- [ ] レビュー担当と実装担当の役割が分かれている
- [ ] push、merge、deploy、deleteの権限が別途ゲートされている
- [ ] 状態ファイルまたはチケットから、次の実行を再開できる

開始条件の例は、次のとおりです。

- CIが失敗した
- レビューコメントが追加された
- 指定ラベルのIssueが存在する

# アンチパターン

## 検証なき反復

「完了しました」という自己申告を、成功条件にしてはいけません。

テスト、ビルド、Lint、スクリーンショット比較など、外部から確認できるシグナルを置きます。

## 会話だけで進捗管理する

長いセッションに依存すると、コンテキスト圧迫と再開不能の原因になります。

状態は、ファイルまたはタスク管理ツールに残します。

## 自動処理を過信する

無監督でmergeやdeployまで進めるべきではありません。

ループの目的は、人の判断を消すことではありません。

人が判断すべき地点まで、安全に作業を運ぶことです。

# 導入順序

Loop Engineeringは、最初から複数のsubagent、worktree、MCP、定期実行を組み合わせるものではありません。

重要なのは、**まず1つの仕事を最後まで閉じられる小さなループを作り、そのループが安定してから自動化範囲を広げること**です。

理由は単純です。

ループが失敗したときに、

- 指示が悪かったのか
- 完了条件が曖昧だったのか
- Claudeの実装が悪かったのか
- テストが不十分だったのか
- subagent間の受け渡しが悪かったのか
- 自動実行のタイミングが悪かったのか

が分からなくなるためです。

最初から複雑なAgentic Workflowを作ると、AIが高度に動いているようには見えても、実際には「どこで品質が壊れているのか分からないシステム」になりやすくなります。

そのため、導入順序は機能ベースではなく、**ループの成熟度**で考えます。

```text
Manual
  ↓
Repeatable
  ↓
Verifiable
  ↓
Delegated
  ↓
Scheduled
  ↓
Autonomous
```

## Phase 1. Manual Loop

### まず、人間がループ全体を動かす

最初は自動化しません。

Claude Codeに1つの具体的な仕事を渡し、人間が開始、確認、再指示、停止を行います。

この段階で確認したいのは、Claude Codeの性能そのものではなく、

> この仕事には、明確な開始条件と完了条件を定義できるか

という点です。

例えば、次のような依頼です。

```text
Fix the failing authentication test.

Done means:
- tests/auth/session.test.ts passes
- npm run lint passes
- no files outside src/auth and tests/auth are changed
```

ここでは、まだ`/loop`もsubagentも必要ありません。

Claudeに実装させ、テスト結果を確認し、人間が完了判定します。

### この段階で得たいもの

仕事を何回か繰り返すうちに、

- 毎回伝えている制約
- 毎回実行しているコマンド
- よく起こる失敗
- 完了判定に必要な証拠

が見えてきます。

それが次のフェーズでルール化する材料になります。

### 次へ進む条件

同じ種類の仕事を2回から3回実行して、

> ほぼ同じ説明と確認手順を使っている

状態になったら、次へ進みます。

## Phase 2. Repeatable Loop

### 繰り返し部分を`CLAUDE.md`とSkillへ移す

Manual Loopを数回回すと、毎回同じことをClaudeに説明していることに気付きます。

例えば、

```text
Run npm test before finishing.
Do not modify migration files.
Do not push automatically.
```

と毎回伝えているのであれば、それはプロンプトではなくプロジェクトルールです。

`CLAUDE.md`へ移します。

```markdown
# CLAUDE.md

## Commands

- Test: npm test
- Lint: npm run lint

## Safety

- Never push or merge automatically.
- Do not modify database migrations unless explicitly requested.
```

一方、毎回同じ順番で行う作業はSkillにします。

例えばCI失敗調査なら、

```text
.claude/skills/ci-triage/SKILL.md
```

を作ります。

```markdown
---
name: ci-triage
description: Investigate the current CI failure.
allowed-tools: Read Grep Glob Bash
---

1. Inspect the failing job.
2. Reproduce the failure locally.
3. Identify the smallest likely root cause.
4. Run the relevant tests.
5. Report the result and evidence.
```

これで、

```text
/ci-triage
```

という短い指示だけで、同じ手順を再現できます。

### なぜこの段階が必要なのか

Agentic Workflowでは、モデル性能以上に**再現性**が重要になります。

毎回自由なプロンプトを書くと、同じ仕事でもプロセスが毎回変わります。

Skillにすることで、

```text
人間の頭の中の手順
        ↓
明示された手順
        ↓
再利用可能なWorkflow
```

に変わります。

### 次へ進む条件

同じSkillを何回か実行して、

- 手順が大きく変わらない
- 誤ったファイルを触らない
- 必要な証拠を毎回出せる

状態になったら、次へ進みます。

## Phase 3. Verifiable Loop

### 「Claudeが完了と言った」を完了条件にしない

ここからLoop Engineeringらしくなります。

人間が毎回結果を読んで判断する代わりに、**機械的に確認できる完了条件**を増やします。

例えば、

```text
npm test
npm run lint
npm run typecheck
```

がすべて成功することを完了条件にします。

```text
/goal npm test exits 0,
npm run lint exits 0,
and npm run typecheck exits 0
```

重要なのは、

```text
Claude says "done"
```

ではなく、

```text
Test = PASS
Lint = PASS
Typecheck = PASS
```

という外部シグナルを使うことです。

### UI開発なら

完了条件はテストだけとは限りません。

例えば、

```text
Build passes
+
Screenshot comparison is acceptable
+
No console errors
```

でも構いません。

データパイプラインなら、

```text
Pipeline succeeds
+
row count is within expected range
+
schema has not changed
```

といった条件にできます。

### この段階の目的

人間が確認していた部分を、

> Claude自身ではなく、別の証拠で確認する

構造へ変えることです。

これはAgentic Workflowの品質を大きく左右します。

### 次へ進む条件

人間が成果物を見る前に、

> 成功か失敗かをかなり高い精度で判定できる

状態になったら、次へ進みます。

## Phase 4. Delegated Loop

### 実装と検証を別の役割に分ける

ここで初めてsubagentを導入します。

例えば、

```text
fixer
    ↓
code-reviewer
```

という構造です。

`fixer`はコードを変更できます。

```text
.claude/agents/fixer.md
```

一方、`code-reviewer`には編集権限を与えません。

```markdown
---
name: code-reviewer
description: Review changes and test evidence.
tools: Read, Grep, Glob, Bash
---

Review the current git diff.

Verify:
- acceptance criteria
- test evidence
- security issues
- unnecessary changes

Do not edit files.
```

するとループは、

```text
Task
 ↓
Fixer
 ↓
Tests
 ↓
Reviewer
 ↓
Pass / Fix again / Escalate
```

になります。

### なぜ最初からsubagentを使わないのか

subagentを増やすと、システムは強力になりますが、同時に、

- コンテキストの受け渡し
- 権限管理
- 責任範囲
- トークン消費
- 失敗原因

も増えます。

単一エージェントのループが安定する前に導入すると、問題の切り分けが難しくなります。

### worktreeを使うタイミング

複数のエージェントが同時にコードを変更し始めたら、Git worktreeを導入します。

```text
main repo
├── worktree/auth-fix
├── worktree/frontend-fix
└── worktree/docs
```

それぞれを独立した作業環境として扱います。

この段階で初めて、並列化のメリットが出てきます。

## Phase 5. Scheduled Loop

### 人が「Claudeを起動する」仕事を自動化する

ここまで安定したら、初めて時間ベースの自動実行を導入します。

例えば、

```text
毎朝9時
    ↓
Open PRを確認
    ↓
CI failureを検出
    ↓
ci-triage
    ↓
状態ファイルを更新
```

とします。

短時間の監視なら、

```text
/loop 10m /ci-triage
```

のようなClaude Code内のループを利用できます。

一方、

- 毎朝実行する
- 夜間に実行する
- セッションを閉じても動かす

といった用途では、GitHub Actionsや外部スケジューラを使います。

例えば、

```yaml
name: Nightly Agent Triage

on:
  schedule:
    - cron: "0 0 * * *"
```

からClaude Codeを含むWorkflowを起動する、といった構成です。

### なぜ自動実行を後回しにするのか

壊れたループを自動実行すると、

> 壊れた処理を、人間が見ていない場所で大量に実行する

ことになります。

そのため、

```text
Correct
↓
Repeatable
↓
Verifiable
↓
Automated
```

の順番を守ることが重要です。

## Phase 6. Autonomous Loop

### 人間は実行者ではなく、例外処理担当になる

最終段階では、人間は毎回ループに参加しません。

例えば、

```text
Issue発生
   ↓
Agentが分類
   ↓
安全な問題
   ↓
Worktree作成
   ↓
Fix
   ↓
Test
   ↓
Review
   ↓
PR作成
```

までは自動化します。

人間には、

```text
Needs human decision
```

だけを送ります。

例えば、

- API仕様を変えるか
- UXを変更するか
- 本番Deployしてよいか
- セキュリティ上のトレードオフを許容するか

といった判断です。

この状態になると、人間の役割は、

```text
Do the work
```

から、

```text
Design the system
Review exceptions
Improve the loop
```

へ変わります。

これがLoop Engineeringの最終的な狙いです。

## 期間ではなくExit Criteriaで進める

実際には「1週間ごと」に区切る必要はありません。

期間よりも、**各フェーズのExit Criteriaを満たしたら次へ進む**方式のほうが実務的です。

| Phase | Exit Criteria |
|---|---|
| Manual | 完了条件を人間が明文化できる |
| Repeatable | 同じ手順をSkillで再現できる |
| Verifiable | 外部シグナルで成功判定できる |
| Delegated | 実装と検証を分離できる |
| Scheduled | 無人実行しても安全に停止できる |
| Autonomous | 人間が例外だけを処理できる |

つまり重要なのは、

> 「何週間経ったか」ではなく、「どこまで人間の判断を安全にシステムへ移せたか」

です。

## 最初に作るなら、このループから始める

最初の題材として、新機能開発全体を選ぶ必要はありません。

例えばCI失敗対応なら、

```text
CI failure
    ↓
原因を調査
    ↓
小さい修正
    ↓
Test
    ↓
Lint
    ↓
Reviewer
    ↓
Human approval
```

という小さなループから始められます。

このループが安定した後に、

```text
CI
↓
Review comments
↓
Issue triage
↓
Dependency updates
↓
Release preparation
```

と対象を広げていきます。

Loop Engineeringでは、最初から大きなAgentic Systemを設計するより、

> **1つのループを閉じる → 測る → 改善する → 次のループをつなぐ**

という進め方のほうが、結果として高度な自動化へ到達しやすくなります。

# ループが静かに壊すもの

ここまで「ループをどう作るか」を説明してきましたが、最後に「ループが何を壊しうるか」を押さえておきます。

出所は、Armin Ronacherの[The Coming Loop](https://lucumr.pocoo.org/2026/6/23/the-coming-loop/)です。

## テストは通るのに、理解可能性が失われる

Ronacherが指摘するのは、無監督のループが繰り返されるときに起こる、静かな劣化です。

LLMは例外やエラーを極端に嫌います。彼はKarpathyの「mortally terrified of exceptions（例外を死ぬほど恐れている）」という表現を引きながら、モデルは設計を直すのではなく、症状に防御的なパッチを当てる傾向があると述べます。

> If each iteration adds another small defense, the system slowly becomes less understandable while appearing more robust.
>
> （各反復が小さな防御を1つずつ追加していくと、システムは頑健に見えながら、徐々に理解しにくくなっていく）

不正な状態を「そもそも起こりえない設計」にするのが正しい修正である場面でも、ループは「あらゆる不正ケースをハンドリングするコード」を積み上げがちです。

ここで注意したいのは、この劣化が**本記事で推奨してきた検証シグナルをすべて通過する**ことです。

```text
Test = PASS
Lint = PASS
Typecheck = PASS

でも、コードは読めなくなっていく
```

防御的なtry-catch、不要なfallback、重複したnullチェックは、テストを壊しません。むしろテストを通りやすくします。Verifiable Loopの外部シグナルは、この種の劣化を検出できないのです。

## これから実装する人への示唆

この懸念は、Loop Engineeringをやめる理由ではありません。Ronacher自身も、移植、パフォーマンス調査、セキュリティスキャンなど、成果物に長い寿命を求めない領域ではループが有効だと認めています。

そのうえで、本記事のループ設計に次の要素を足すことを勧めます。

順番に意味があります。CLAUDE.mdで**予防**し、停止条件で**抑制**し、レビューで**検出**し、人間の読みで**監査**する、という多層防御です。

### 1. CLAUDE.mdで、防御的コードを生成段階から予防する

レビューでの検出は事後対応です。

CLAUDE.mdは実装担当を含む全エージェントが常に読む前提なので、防御的パッチをそもそも書かせないルールを置けます。

```markdown
## Error handling policy

- Fail fast. Do not catch exceptions just to keep the program running.
- Before handling an invalid state, first check whether the state
  can be prevented at its source. Prefer making invalid states
  impossible over handling them.
- Any new defensive branch must include a comment explaining why
  prevention at the source is not possible.

## Root cause rule

- When a test fails, fix the cause, not the symptom.
- Never modify a test, add a special case, or widen a type
  just to make a check pass.

## Simplicity

- Prefer deleting or simplifying code over adding it.
- If you duplicate logic, refactor instead of copying.
```

これは記事のStep 2の基準、つまり「頻繁に変わらず、プロジェクト全体に適用されるルール」そのものです。

### 2. 停止条件に「設計の劣化を防ぐ制約」を含める

「テストが通る」だけでは足りません。差分サイズの上限と、防御的パッチの禁止を明示します。

```text
/goal npm test exits 0, npm run lint exits 0,
the diff stays under 150 lines,
and no new try-catch or fallback branches are added
unless the plan explains why the invalid state cannot be prevented
```

### 3. code-reviewerに「理解可能性」を評価させる

Step 4のレビュー担当は、テスト証拠だけでなく、劣化の兆候を明示的に見る役割を持たせます。

```markdown
Also check for loop-induced degradation:
- Defensive patches that handle symptoms instead of fixing root causes
- New try-catch, fallback, or null-check branches without justification
- Duplicated logic or abstractions that paper over unclear design

Flag these as "Must fix" even if all tests pass.
```

### 4. 人間がコードを読む地点を、意図的に残す

Phase 6のAutonomous Loopでも、「人間は例外だけを見る」を「人間はコードを読まない」にしてはいけません。

Ronacherは、機械の参加を前提としないと保守できないコードベースが生まれることを警告し、最後にこう問いかけます。

> 判断を放棄しないためにどうするか。良いエンジニアリングの規範をどう保つか。責任ある人間が監督し続けられる状態を、どう維持するか。

ループの反復回数ではなく、時間や節目で「人間が差分ではなくコード全体を読む」レビューを定期的に入れます。これはEscalateの一種として、ループ設計そのものに組み込めます。

Loop Engineeringの目的が「人が判断すべき地点まで、安全に作業を運ぶこと」であるなら、**コードを理解する能力を人間の側に残しておくこと**は、その前提条件です。

# まとめ

Claude Codeでloopを設計するとは、単に同じプロンプトを繰り返すことではありません。

具体的には、次の要素を設計することです。

1. 何をきっかけに開始するか
2. どの作業を対象にするか
3. 何を自動実行するか
4. どの証拠で成功を判定するか
5. どの条件で停止するか
6. どの判断を人に渡すか
7. 次回のために何を記録するか

Claude Codeでは、それぞれを次の機能に対応させられます。

| 設計対象 | Claude Codeでの実装 |
|---|---|
| 常設ルール | `CLAUDE.md` |
| 反復手順 | Skills |
| 実装と検証の分離 | Subagents |
| 短期的な定期実行 | `/loop` |
| 完了条件付きの反復 | `/goal` |
| 並列作業の隔離 | Git worktree |
| 外部サービスとの接続 | MCP |
| セッションをまたぐ状態 | Markdown、Issue、タスク管理 |
| 継続的な自動実行 | Routines、Desktop scheduled tasks、GitHub Actions |

Loop Engineeringの中心は、AIに長時間働かせることではありません。

小さな仕事を、安全に発見し、限定された権限で実行し、証拠を使って検証し、必要な判断だけを人へ渡すことです。

# 参考資料

- [Addy Osmani: Loop Engineering](https://addyosmani.com/blog/loop-engineering/)
- [Armin Ronacher: The Coming Loop](https://lucumr.pocoo.org/2026/6/23/the-coming-loop/)
- [Claude Code Docs: Run prompts on a schedule](https://code.claude.com/docs/en/scheduled-tasks)
- [Claude Code Docs: Keep Claude working toward a goal](https://code.claude.com/docs/en/goal)
- [Claude Code Docs: Best practices](https://code.claude.com/docs/en/best-practices)
- [Claude Code Docs: Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Claude Code Docs: Create custom subagents](https://code.claude.com/docs/en/sub-agents)
