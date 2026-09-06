---
title: "OpenClawマルチエージェント設計 2026年9月版: Monica型ペルソナはまだ有効か"
emoji: "🦞"
type: "tech"
topics:
  - "OpenClaw"
  - "AIエージェント"
  - "マルチエージェント"
  - "自動化"
  - "設計"
published: false
---

#### AIが書きました🤖
この記事は、AIが書いたものを人間が確認してから投稿しています。

OpenClawでマルチエージェントを定義するとき、Shubham Sabooの「Monica」のように詳細なペルソナを作り込んで分業させる方法は、まだ有効なのでしょうか。どういうファイル階層で、どういうループを組み込むべきかを、いくつかの新しい実例を参考にしながら整理します。

# 結論

Monica型はまだ有効です。

ただし、2026年9月時点のOpenClawでは、**「詳細な人格を6人作る」こと自体より、人格、役割、権限、状態、評価ループを分離する設計**のほうが重要になっています。

Shubham Saboo本人の初期構成は、2026年2月時点では`SOUL.md`を中心にMonica、Dwight、Kelly、Rachel、Ross、Pamを作り、ファイルで受け渡す構成でした。特に「1 agent = 1つの退屈なくらい明確な仕事」「one writer, many readers」「Monicaが最終レビュー」という原則は、現在でもかなり良い設計です[^1]。

一方、その後Saboo自身も、Hermesをフロント、OpenClawを実行層、GBrainを共有知識層とする構成へ発展させています[^2]。つまり、**人格よりも共有コンテキストとオーケストレーションのほうへ重心が移っている**と見るのがよいです。

# まず、現在のOpenClawでは3種類を分けて考える

私はこの区別から設計します。

| 種類 | 用途 | Persona |
|---|---|---|
| Persistent agent | 長期担当者。独自memory、tool、権限、cronを持つ | 詳細に作る価値あり |
| Sub-agent | 1回限りの調査、実装、レビュー | 薄くてよい |
| Swarm worker | 大量並列処理 | ほぼ不要 |

OpenClawのconfigured agentはそれぞれ独立したworkspace、session store、auth、tool policyを持てます[^3]。つまり現在は、単なる「プロンプト上の役柄」ではなく、本当に別の実行主体として分離できます。

一方、sub-agentは一時的なisolated sessionです。OpenClawはこれをresearch、長時間処理、並列処理に使うことを想定しています[^4]。

大量の独立タスクならSwarmもあります。`Promise.all`や`while`など普通のJS、TSでfan-out、collect、判定を書く方式で、OpenClaw自身もSwarmでは深いagent階層よりflatなworker群を推奨しています[^5]。

なので、

```text
Monica → Dwight → Dwight-Junior → Search-Agent → Citation-Agent
```

のような組織図は、現在はあまり勧めません。

むしろ、次のくらいがよいです。

```text
                         User
                           │
                       Monica
                    Orchestrator
                           │
              ┌────────────┼────────────┐
              │            │            │
         Researcher     Builder      Reviewer
              │            │            │
           workers      workers       workers
              └────────────┼────────────┘
                           │
                        Monica
                        synthesis
                           │
                          User
```

# Monica型personaはどこまで作り込むべきか

SabooのDwightは単に「research agent」ではなく、

- Core Identity
- Role
- Principles
- 他agentとの関係
- decision framework
- output location

まで定義されていました。Sabooは`SOUL.md`を40から60行程度に抑えていました[^1]。

この考え方はまだ有効です。ただし私が現在作るなら、次のように分割します。

```text
SOUL.md
    Who am I?

AGENTS.md
    What am I responsible for?
    How do I work?
    What am I allowed to decide?

TOOLS.md
    How do I use my tools?

skills/
    How do I perform repeatable procedures?

MEMORY.md
    What have I learned?

shared/
    What does the rest of the team need?

performance/
    How am I doing?
```

ここがかなり重要です。

現在のOpenClawでは、通常sessionでは`SOUL.md`、`AGENTS.md`、`USER.md`、`IDENTITY.md`、`MEMORY.md`などがbootstrap contextになります[^6]。

しかしnative sub-agentはコンテキストが意図的に絞られており、現在のドキュメントでは`AGENTS.md`と`TOOLS.md`が中心です。親専用の`SOUL.md`、`USER.md`、`MEMORY.md`などはそのまま引き継ぎません[^7]。

したがって、

> 「Dwightの人格はSOUL.mdに全部書いてあるから、DwightをspawnすればDwightになる」

という設計は危険です。

:::message
**仕事を成立させる情報はAGENTS.mdまたはhandoff promptに置く。SOUL.mdは人格だけにする。**

これが現在版の重要な修正点です。
:::

# ファイル階層

Sabooの初期構成はこうでした[^1]。

```text
workspace/
├── SOUL.md
├── AGENTS.md
├── MEMORY.md
├── HEARTBEAT.md
├── agents/
│   ├── dwight/
│   ├── kelly/
│   ├── ross/
│   └── ...
└── intel/
```

現在なら、OpenClawのagent isolationに合わせて一段明示的にします。

```text
agent-fleet/
│
├── openclaw.json
│
├── shared/
│   ├── knowledge/
│   │   ├── projects/
│   │   ├── companies/
│   │   └── concepts/
│   │
│   ├── artifacts/
│   │   ├── research/
│   │   ├── builds/
│   │   └── reviews/
│   │
│   └── schemas/
│       ├── research-brief.schema.json
│       └── review.schema.json
│
└── workspaces/
    │
    ├── monica/
    │   ├── SOUL.md
    │   ├── IDENTITY.md
    │   ├── AGENTS.md
    │   ├── USER.md
    │   ├── TOOLS.md
    │   ├── MEMORY.md
    │   ├── memory/
    │   │   └── YYYY-MM-DD.md
    │   ├── performance/
    │   └── skills/
    │
    ├── researcher/
    │   ├── SOUL.md
    │   ├── AGENTS.md
    │   ├── TOOLS.md
    │   ├── MEMORY.md
    │   ├── memory/
    │   └── skills/
    │       ├── web-research/
    │       │   └── SKILL.md
    │       └── source-verification/
    │           └── SKILL.md
    │
    ├── builder/
    │   ├── SOUL.md
    │   ├── AGENTS.md
    │   ├── TOOLS.md
    │   ├── MEMORY.md
    │   └── skills/
    │
    └── reviewer/
        ├── SOUL.md
        ├── AGENTS.md
        ├── TOOLS.md
        └── skills/
```

OpenClaw自身も、各agentに独立workspaceを持たせる構成を正式にサポートしています[^3]。

また最近のOpenClaw multi-agent templateでも、root orchestratorとteam capabilityを分離し、`SOUL.md`、`AGENTS.md`、`ORCHESTRATION_WORKFLOW.md`、`shared/`、`memory/`を別レイヤーとして扱う方向になっています[^8]。

# AGENTS.mdを一番重要なファイルにする

たとえばresearcherなら、私はSOULよりAGENTSを強くします。

```markdown
# Mission

Produce evidence-backed research briefs for Monica.

# Owns

- external research
- source verification
- competing hypotheses
- uncertainty assessment

# Does not own

- final recommendations
- implementation
- user-facing writing
- publishing

# Input contract

Every assignment must contain:

- Task
- Context
- Goal
- Constraints
- Expected output
- Stop condition

# Output contract

Return:

1. Executive finding
2. Evidence
3. Sources
4. Conflicting evidence
5. Confidence
6. Open questions

# Stop conditions

Stop and escalate when:

- authoritative sources disagree
- required data cannot be obtained
- answering requires an unsupported assumption

# Artifact ownership

Write:
shared/artifacts/research/<task-id>.md

Never modify:
shared/artifacts/builds/*
shared/artifacts/reviews/*
```

これは最近の実例ともかなり共通点があります。huaquanghanのtemplateでも、handoffを

> Task / Context / Goal / Constraints / Expected output / Stop condition

として明示しています[^9]。

こうしたcontractのほうが、personaより出力の品質に直結します。

# SOUL.mdは短くする

Researcherならこれくらいで十分です。

```markdown
# SOUL

You are Atlas, the research lead.

You are skeptical, evidence-first, and concise.

You prefer:
- primary sources over commentary
- uncertainty over false precision
- competing explanations over premature conclusions

You do not optimize for sounding confident.
You optimize for being correct and useful.

You are an internal specialist.
Monica owns the final recommendation.
```

TVキャラクターを使うなら、

```text
Think Dwight Schrute's intensity,
without the theatrics.
```

くらいはまだ有効です。

Sabooの「TVキャラクターはtraining dataにすでに豊富なbehavioral priorがあるので、短い表現で人格を圧縮できる」という考え方には合理性があります[^1]。

ただ、これは**behavior compression**として使うのがよくて、「架空の人物を精密に演じさせる」ことを目的にしないほうがよいです。

# 一番おすすめのループ

現在なら基本形はこれです。

```text
RECEIVE
   ↓
CLASSIFY
   ↓
PLAN
   ↓
DIRECT or DELEGATE
   ↓
EXECUTE
   ↓
VERIFY
   ↓
REVIEW
   ↓
SYNTHESIZE
   ↓
DELIVER
   ↓
LEARN
```

最近のOpenClaw templateも非常によく似た

```text
RECEIVE
→ ANALYZE
→ DECIDE DIRECT VS DELEGATE
→ REVIEW
→ INTEGRATE
→ DELIVER
```

を採用しています[^10]。

ここに私は`LEARN`を追加します。理由は後述の「Agent Improvement Loop」で説明します。

## 実例1: 調査系なら Research → Critic → Monica

たとえば「社内agent orchestrationの最新事例を調べて」と来た場合。

```text
User
 ↓
Monica
 ↓
Researcher
 ├─ vendor docs
 ├─ GitHub examples
 └─ practitioner cases
 ↓
Critic
 ↓
Monica
 ↓
final answer
```

Researcherが3方向を並列化するなら、native sub-agentでもSwarmでもよいです。

```text
Researcher
  ├── worker A: official docs
  ├── worker B: GitHub
  └── worker C: practitioner reports
```

そしてCriticには、

```text
Find:
- unsupported claims
- stale evidence
- contradictions
- missing alternatives
```

だけをやらせます。

**Writerを3人置いて多数決する必要はありません。**

## 実例2: コーディングなら Planner → Builder → Reviewer

```text
Monica
  ↓
Builder
  ├─ inspect
  ├─ implement
  ├─ test
  ↓
Reviewer
  ↓
Builder retry if necessary
  ↓
Monica
```

ここではpersonaより、

```text
Definition of Done
Tests
Allowed files
Forbidden actions
Rollback condition
```

が重要になります。

最近のOpenClawのsub-agent patternでも、implementation specialistには

- scopeを超えない
- verificationする
- risksを明示する
- destructiveになるならstopする

というcontractを持たせています[^9]。

## 実例3: 大量処理ならSwarm

100社について情報を集めるなら、次のようになります。

```text
Monica
 ↓
Plan
 ↓
Swarm
 ├ company 1
 ├ company 2
 ├ company 3
 ├ ...
 └ company 100
 ↓
aggregate
 ↓
review
```

こちらは人格不要です。

```javascript
const results = await Promise.all(
  companies.map(company =>
    agents.run(`Research ${company}`, {
      schema: researchSchema
    })
  )
);

return synthesize(results);
```

OpenClaw Swarm自身が、このようなflat collector patternを想定しています[^5]。

# もう1個、かなり重要なループ: Agent Improvement Loop

Saboo型の中で、今見ても一番重要なのは実はpersonaではなく、**Agent Improvement Loop**です。

AJ MorrisはSabooのパターンを半年運用した結果、agent definitionより**weekly performance reviewのほうが重要だった**としています[^11]。

毎週、

```text
daily logs
   ↓
recent outputs
   ↓
rubric evaluation
   ↓
performance review
   ↓
human feedback
   ↓
AGENTS.md / SOUL.md update
   ↓
next week
```

というループを回しています。品質、voice adherence、edge case処理、不確実性の扱いなどを評価し、`performance/YYYY-MM-DD-review.md`に残しています。

これはかなり良いです。私はさらに、

```text
OBSERVE
  ↓
GRADE
  ↓
DIAGNOSE
  ↓
PATCH HARNESS
  ↓
RETEST
```

と考えます。

:::message
**モデルを学習させるのではなく、harnessを学習させる。**

これはLoop Engineeringの考え方にもかなり近いです。
:::

# Memoryも3層にする

現在なら、

```text
1. task workspace
       ↓
2. agent memory
       ↓
3. shared durable knowledge
```

がおすすめです。

最近のOpenClaw templateでも、

- workspace = doing
- memory = continuity
- durable knowledge = lasting meaning

という3層になっています[^12]。

具体的には次のとおりです。

```text
memory/YYYY-MM-DD.md
    生ログ

MEMORY.md
    distilled lessons

shared/knowledge/
    agent横断で再利用する知識
```

Sabooの現在のGBrain構成も、ほぼこの3層目を強化したものです。Dwightが調べたcompany情報を、Rachel、Pam、Kellyが再利用する構成になっています[^2]。

# one writer, many readers は残す

これはSaboo型で今でも特に良い設計です。

```text
researcher
    WRITE
shared/research/latest.json

builder
    READ

writer
    READ

reviewer
    READ
```

複数agentに同じMarkdownを書かせない。

Saboo自身も、coordination conflictへの対策として`DAILY-INTEL.md`はDwightだけが書き、他は読むだけという設計を採用しています[^1]。

現在ならさらに、

```text
shared/artifacts/
    research/    owner = researcher
    builds/      owner = builder
    reviews/     owner = reviewer
```

とディレクトリ単位でownershipを決めます。

# OpenClaw configも役割を表現する

概念的にはこうします。

```json5
{
  agents: {
    defaults: {
      subagents: {
        maxSpawnDepth: 2,
        maxChildrenPerAgent: 4,
        maxConcurrent: 6,
        runTimeoutSeconds: 900
      }
    },

    entries: {
      monica: {
        workspace: "~/agent-fleet/workspaces/monica",
        subagents: {
          allowAgents: [
            "researcher",
            "builder",
            "reviewer"
          ],
          requireAgentId: true
        }
      },

      researcher: {
        workspace: "~/agent-fleet/workspaces/researcher"
      },

      builder: {
        workspace: "~/agent-fleet/workspaces/builder",
        sandbox: {
          mode: "all"
        }
      },

      reviewer: {
        workspace: "~/agent-fleet/workspaces/reviewer"
      }
    }
  },

  tools: {
    agentToAgent: {
      enabled: false
    }
  },

  bindings: [
    {
      agentId: "monica",
      match: {
        channel: "telegram",
        accountId: "default"
      }
    }
  ]
}
```

`subagents.allowAgents`で、Monicaがspawnできるconfigured agentを限定できます。OpenClawはこのallowlistを正式に持っています[^13]。

agent-to-agentの自由な横通信はデフォルトで可能ですが、私は原則切ります。必要な経路だけorchestrator経由にしたほうがデバッグしやすいです。OpenClawでは`tools.agentToAgent`で制限できます[^14]。

# まとめ: Monica型を2026年9月版にアップデートする

## 残すもの

- Monicaのようなsingle front door
- 明確な専門職
- 短いが特徴的なpersona
- one agent, one boring job
- one writer, many readers
- daily memory + curated memory
- human feedback
- periodic performance review

## 弱めるもの

- 6人全員の過剰な人格設定
- agent同士の自由会話
- 深い組織階層
- 全agentの常駐化
- chat history依存
- 全員が全ファイルを読む構成

## 強めるもの

- handoff contract
- stop condition
- structured output
- tool permission
- sandbox
- artifact ownership
- review agent
- shared durable knowledge
- harness improvement loop

## 今から作るなら

私は次の4層程度から始めます。

```text
Monica
   Chief of Staff
   persistent, rich persona

Researcher
   persistent only if recurring
   medium persona

Builder
   persistent capability profile
   light persona

Reviewer
   persistent capability profile
   almost no persona

Workers
   ephemeral
   no persona
```

:::message
**「人格を持つAI社員を増やす」のではなく、「Monicaだけを人格として強くし、その下を能力、権限、状態、評価ループとして設計する」**のが、現在のOpenClawでは一番扱いやすい構成だと思います。
:::

[^1]: [How I Built an Autonomous AI Agent Team That Runs 24/7 (unwind ai)](https://www.theunwindai.com/p/how-i-built-an-autonomous-ai-agent-team-that-runs-24-7)
[^2]: [Shubham Saboo: I gave my Hermes and OpenClaw Agents a shared brain (LinkedIn)](https://www.linkedin.com/posts/shubhamsaboo_i-gave-my-hermes-and-openclaw-agents-a-shared-activity-7463420156019359744-Fmgh)
[^3]: [openclaw/docs/concepts/multi-agent.md (GitHub)](https://github.com/openclaw/openclaw/blob/main/docs/concepts/multi-agent.md)
[^4]: [openclaw/docs/tools/subagents.md (GitHub)](https://github.com/openclaw/openclaw/blob/main/docs/tools/subagents.md)
[^5]: [Swarm (OpenClaw Docs)](https://docs.openclaw.ai/tools/swarm)
[^6]: [Agent runtime (OpenClaw Docs)](https://docs.openclaw.ai/concepts/agent)
[^7]: [サブエージェント (OpenClaw Docs)](https://docs.openclaw.ai/ja-JP/tools/subagents)
[^8]: [huaquanghan/openclaw-multi-agent-template (GitHub)](https://github.com/huaquanghan/openclaw-multi-agent-template)
[^9]: [openclaw-multi-agent-template/docs/SUBAGENT_CONTRACTS.md (GitHub)](https://github.com/huaquanghan/openclaw-multi-agent-template/blob/main/docs/SUBAGENT_CONTRACTS.md)
[^10]: [openclaw-multi-agent-template/ORCHESTRATION_WORKFLOW.md (GitHub)](https://github.com/huaquanghan/openclaw-multi-agent-template/blob/main/ORCHESTRATION_WORKFLOW.md)
[^11]: [Building a Chief of Staff Out of Markdown Files (AJ Morris)](https://ajmorris.me/blog/building-a-chief-of-staff-out-of-markdown-files/)
[^12]: [openclaw-multi-agent-template/docs/KNOWLEDGE_ROUTING.md (GitHub)](https://github.com/huaquanghan/openclaw-multi-agent-template/blob/main/docs/KNOWLEDGE_ROUTING.md)
[^13]: [Configuration: agents (OpenClaw Docs)](https://docs.openclaw.ai/gateway/config-agents)
[^14]: [Configuration: tools and custom providers (OpenClaw Docs)](https://docs.openclaw.ai/gateway/config-tools)
