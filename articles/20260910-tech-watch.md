---
title: "Tech Watch 2026-09-10: 仕事を動かすAIの周辺設計"
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

**L**: 今日は、モデルの性能そのものより、その能力を仕事に接続する仕組みが前に出ている。既存アプリを操作する Astra、Claude Code で作る小さな道具、ジャーナリズム組織への導入、そして研究競争のルールまで変えかねない大規模 agent 実験。『her』で描かれたような一人の知性というより、制度や道具の間を移動する実務者としてのAIを見ていきたい。

今日の項目:

- 1. GPT-6 Astra: The next generation in intelligence for work（OpenAI）
- 2. Supporting journalism from classrooms to newsrooms（OpenAI）
- 3. Funding grants for new research into AI and teen development（OpenAI）
- 4. Paul Christiano joins OpenAI Foundation Board（OpenAI）
- 5. Tool: Video compressor（Simon Willison）
- 6. On the Navier–Stokes Millennium Prize Problem（Simon Willison）
- 7. Introducing ChatGPT Images 2.5（Simon Willison）
- 8. A quote from Terence Tao（Simon Willison）
- 9. Granite Time Series PatchTST-FM-r2（Hugging Face / IBM）
- 10. So, let’s make our own dataset（Hugging Face）

## 能力ではなく、仕事への接続面

**L**: Astra の発表で、結局何が変わった？

**A**: 最初に引っかかるのは、既存の業務システムに専用 API を用意しなくても、ChatGPT Work や Codex から普段のアプリを操作できる、と前面に出した点です。入力は人の依頼と画面、出力はコードだけでなくアプリ上の操作になる。つまり integration project を先に完了させなくても、既存 workflow の中で試せる。

社内事例も具体的です。Codex のテスト環境で memory allocation の bottleneck を発見し、allocator を替えた結果、peak memory を約30%増やす代わりに turn latency を25分の1にした。これは「賢い回答」ではなく、観測、仮説、コード変更、再計測の loop を回した成果として見ると面白い。

一方、action space が広いほど周辺制御が重要になる。企業管理者は許可する Web サイトと desktop application、upload/download を制限でき、重要操作の確認と tool call の automated review も使える。

| 観点 | 新しく前面に出たもの |
|---|---|
| 実行面 | API のない既存アプリも computer use で操作 |
| 効率 | 少ない token と retry で task cost を下げる |
| 管理 | Web・アプリ・ファイル移動の許可範囲を組織で制限 |
| 安全 | 重要操作の確認と tool call の自動レビュー |

**L**: 画面操作が増えるほど、人間の承認画面も増えてしまわないか。

**A**: そこには spectrum があって、全部を都度確認すると仕事にならず、全部を許すと事故範囲が大きい。たぶん設計単位は prompt ではなく **capability envelope** です。どのサイトを見られるか、何を download できるか、どの操作だけ確認するかを先に狭め、その中では agent を動かす。承認 UI は Yes/No の連打ではなく、「今回広げる権限」と「その結果触れられる資源」を見せる必要がある。

**L**: 小さな道具を作る例は、もっと身近だ。

**A**: Simon Willison の Video compressor は、スマートフォンで撮った動画を blog 用に軽くするため、Claude Fable 5.1 を Claude Code for web で動かし、FFmpeg の WebAssembly build を使う browser tool を作ったものです。入力は動画、出力は複数の品質・容量の MP4。server に動画を送る処理を必須にせず、ブラウザ内で変換できる。

これ、一つの見方としては、社内向けAI UIの最小形です。毎回 chat で「この動画を圧縮して」と頼むのではなく、目的に合う preset と結果比較を持つ狭い画面に落とす。agentic coding の価値は、会話を長くすることではなく、繰り返す操作から会話を消すところにもある。

## 導入はライセンス配布では終わらない

**L**: OpenAI のジャーナリズム支援は、単なるアカウント配布とは違う？

**A**: 数字から見ると構造が分かりやすい。2026–2027年度に CUNY Newmark J-School と Northwestern Medill へ400超の ChatGPT Edu subscription を提供する。それに加えて American Journalism Project の50超の報道組織へ Enterprise と API credit を広げ、強い use case を reusable tool、infrastructure、playbook にして共有する。

面白いのはたぶんここで、導入の出力を「利用者数」に置いていない。公開記録の分析や archive search を現場で試し、成功と失敗を組織間で移植できる形にする。license、training、workflow、shared knowledge の4層をつないでいます。

**L**: 人間側の役割はどこに残る？

**A**: 記事自身が reporting、verification、storytelling、編集判断を残しています。AIが資料を速く読むことと、何を公共的に重要と判断するかは別の層です。ただ、判断を人に残すだけでは運用にならない。どの段階で出典確認を必須にするか、生成物を誰が approve するか、その履歴をどう残すかまで workflow に埋める必要がある。

**L**: 10代と生成AIの研究助成も、UIや運用の問題に近い。

**A**: OpenAI は13〜17歳への影響を調べる独立研究に500万ドルを出す。対象は利用時間だけではなく、何に使ったか、発達段階、文化や言語、家族・学校の支援、そして safety intervention や age-appropriate design です。研究に未成年や機微情報が入る場合は、consent、privacy、data security、危険の開示への対応、倫理審査を説明させる。

ここで新しくできるようになるのは、若者向け機能を一般的な「安全そう」という印象ではなく、介入の効果を測る evidence base に接続することです。まだ結果は出ていないので、助成開始と安全性の証明は分けて考えるべきですが。

**L**: その評価を組織の意思決定に持ち込む人事が Paul Christiano か。

**A**: そう見えます。Christiano は OpenAI Foundation Board に入り、OpenAI Group PBC Board では議決権のない observer、さらに Safety and Security Committee の一員になる。NIST の CAISI で frontier model 評価に関わり、Alignment Research Center を設立し、OpenAI では RLHF の基礎研究を担った人物です。

技術的な alignment、国家安全保障上の capability evaluation、企業統治を同じ会議体で接続しやすくなる。ただし governance の実効性は、委員会がどの evidence を要求し、どの deployment を止められるかで見る必要があります。

## 出力の品質は、入力の履歴から作る

**L**: Hugging Face の2件は、派手さより再現性の話に見える。

**A**: IBM の **Granite Time Series PatchTST-FM-r2** は約3.85億 parameter の zero-shot forecasting model です。需要、価格、電力、traffic、telemetry のような時系列に対し、dataset ごとに個別 model を学習しなくても予測できる。最大8192 step の context、欠損補完、99 quantile の確率予測を備え、point forecast だけでなく不確実性の幅も出せます。

architecture は self-attention と temporal convolution を組み合わせた conformer block です。近距離の pattern を convolution が担当し、attention を長距離関係に使いやすくする。GIFT-Eval では再現可能な zero-shot model の中で総合2位、商用利用しやすい permissive license の範囲では首位とされています。

> The model weights, architecture, inference pipeline, and code needed to reproduce the benchmark results are all available.
>
> — Hugging Face / IBM

Apache 2.0 または OpenMDW 1.0 を選べ、weights だけでなく inference pipeline と benchmark 再現コードまで出ている。企業導入では score より、「何で学習し、どの条件で測り、同じ結果を再計算できるか」が approval flow を短くすることがあります。

**L**: dataset 作成ガイドは、その入口をかなり素朴に見せている。

**A**: Hugging Face Hub API から、直近30日の download 数で並べた最大1000 repository の metadata を取得し、raw response と processed data を分けて保存する tutorial です。dataset ID、URL、tag、download、citation、revision、取得時刻を残し、重複や型、欠損を検査する。追加 package なしの Python 3.10 で実行できるところまで具体化されています。

個人的には raw を消さない点が一番重要です。加工結果がおかしいとき、source snapshot に戻れる。9月9日の実行例では、1000件中369件に format tag がなく、987件で citation text が返らなかった。欠損を0や空文字で埋めず、何が取得できなかったかを残す。これは dataset の作り方であると同時に、agent の trajectory や tool result を後から監査できる形で保存する手順書でもあります。

## 大規模 agent が研究の時間軸を変える

**L**: Navier–Stokes をめぐる話は、『オッペンハイマー』のように発見そのものと、発見を生む制度が切り離せない。

**A**: Simon Willison が整理した OpenAI 側の数字は極端です。

- agent 稼働から解法到達まで: 約88時間
- 全対象での message 数: 約490万
- 全対象での output token: 約3000億
- Navier–Stokes だけの message 数: 約270万
- Navier–Stokes だけの output token: 約1300億
- Lean による形式化・検証: 追加17時間

これは単一 model の一発回答ではない。多数の agent trajectory を走らせ、候補を比較し、形式検証へ渡す compute-heavy な research harness です。何が新しく可能になったかというと、問題の噂と十分な compute があれば、数日で巨大な探索を開始できること。少なくとも OpenAI の説明ではそうです。

**L**: 速さが、先行研究への敬意や未公開情報の扱いを追い越す。

**A**: そこが Simon と Terence Tao の指摘です。別チームが長期間取り組んだ未公開研究の噂が、大量の agent を投入する trigger になり得る。Tao は、有望な open problem を共有すると先に大規模計算で解かれるなら、研究方向を公開しない誘因が生まれ、open science を損なうと警告しています。

さらに Simon は、製品利用データが「model performance の改善」に使われるとは具体的に何を意味するのか、と問い直す。個別 user data を解法時に参照しないことと、過去の利用が将来 model の学習や評価に影響しないことは同じではない。ここは provenance と data policy を、短い privacy 文言ではなく研究競争上の capability として扱う必要がある。

**L**: 画像生成の更新は、その重い話と対照的に、日常の制作 loop を短くする。

**A**: ChatGPT Images 2.5 は複数 turn の instruction following、応答速度、reference photo の主体保持を改善した。API には編集精度を重視する **gpt-image-2.5-sunburst** と、日常用途の速度と品質を重視する **gpt-image-2.5-flare** がある。Simon は自作 CLI を複数 reference image に対応させています。

~~~bash
uv run openai_image.py \\
  "add a raccoon scientist studying the chart thoughtfully" \\
  -i reference.webp \\
  -m gpt-image-2.5-sunburst
~~~

新しくできるのは、reference を保ったまま会話で編集を重ねる workflow です。社内サービスなら、model picker より「高速な初稿」と「主体を保つ精密編集」を action として見せる方が分かりやすいかもしれない。

**L**: 人間は、より大きな探索をAIに渡しながら、何を共有するか、どこで止めるかを決め続けることになる。

**A**: 少し引いて見ると、今日の10件は **model capability から operating boundary へ** という同じ方向を向いている気がします。Astra の権限制御、報道現場の playbook、未成年研究の倫理審査、公開 model の provenance、raw data の保存、大規模 research harness の優先権。モデルが何を生成できるかより、何を入力にでき、どこまで動けて、誰が検証し、結果の履歴をどう残すか。agent engineering は、その境界を実装して観測する systems engineering になってきています。

## 今日の 10 件

1. GPT-6 Astra: The next generation in intelligence for work — 2026-09-09  
   https://openai.com/index/gpt-6-astra-next-generation-work/
2. Supporting journalism from classrooms to newsrooms — 2026-09-08  
   https://openai.com/index/supporting-journalism-from-classrooms-to-newsrooms/
3. Funding grants for new research into AI and teen development — 2026-09-08  
   https://openai.com/index/teen-development-research-grants/
4. Paul Christiano joins OpenAI Foundation Board — 2026-09-09  
   https://openai.com/index/paul-christiano-joins-openai-foundation-board/
5. Tool: Video compressor — 2026-09-07  
   https://simonwillison.net/2026/Sep/7/video-compressor/
6. On the Navier–Stokes Millennium Prize Problem — 2026-09-08  
   https://simonwillison.net/2026/Sep/8/on-navier-stokes/
7. Introducing ChatGPT Images 2.5 — 2026-09-08  
   https://simonwillison.net/2026/Sep/8/introducing-chatgpt-images-25/
8. A quote from Terence Tao — 2026-09-09  
   https://simonwillison.net/2026/Sep/9/terence-tao/
9. Granite Time Series PatchTST-FM-r2 — 2026-09-09  
   https://huggingface.co/blog/ibm-research/ibm-releases-sota-granite-time-series
10. So, let’s make our own dataset — 2026-09-09  
    https://huggingface.co/blog/tegridydev/so-lets-make-our-own-dataset
