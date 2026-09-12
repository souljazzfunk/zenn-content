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
published: true
---

#### AIが書きました🤖

この記事は、AIが書いたものを人間が確認してから投稿しています。

**L**: 今日は、モデルの性能そのものより、その能力を仕事に接続する仕組みが前に出ている。既存アプリを操作する Astra、Claude Code で作る小さな道具、ジャーナリズム組織への導入、そして研究競争のルールまで変えかねない大規模エージェント実験。『her』で描かれたような一人の知性というより、制度や道具の間を移動する実務者としてのAIを見ていきたい。

今日の項目:

- 1. GPT-6 Astra: The next generation in知能for work（OpenAI）
- 2. Supporting journalism from classrooms to newsrooms（OpenAI）
- 3. Funding grants for new research into AI and teen development（OpenAI）
- 4. Paul Christiano joins OpenAI Foundation Board（OpenAI）
- 5. Tool: Video compressor（Simon Willison）
- 6. On the Navier–Stokes Millennium Prize Problem（Simon Willison）
- 7. Introducing ChatGPT Images 2.5（Simon Willison）
- 8. A quote from Terence Tao（Simon Willison）
- 9. Granite Time Series PatchTST-FM-r2（Hugging Face / IBM）
- 10. So, let’s make our ownデータセット（Hugging Face）

**A**: 10件を仕組みで追うと、共通しているのはモデルの外側にある実行条件です。

## 能力ではなく、仕事への接続面

**L**: Astra の発表で、結局何が変わった？

**A**: 最初に引っかかるのは、既存の業務システムに専用 API を用意しなくても、ChatGPT Work や Codex から普段のアプリを操作できる、と前面に出した点です。API を不要にする、いや、正確には API 統合を先送りしたまま既存画面で試せる、という変化です。入力は人の依頼と画面、出力はコードだけでなくアプリ上の操作になる。

社内事例も具体的です。Codex のテスト環境でメモリ割り当ての制約箇所を発見し、メモリ割り当て器を替えた結果、最大メモリを約30%増やす代わりにターン待ち時間を25分の1にした。これは「賢い回答」ではなく、観測、仮説、コード変更、再計測のループを回した成果として見ると面白い。

一方、action space が広いほど周辺制御が重要になる。企業管理者は許可する Web サイトとデスクトップアプリ、アップロード／ダウンロードを制限でき、重要操作の確認と道具call の自動レビューも使える。

| 観点 | 新しく前面に出たもの |
|---|---|
| 実行面 | API のない既存アプリもコンピュータ操作で扱う |
| 効率 | 少ないトークンと再試行でタスク費用を下げる |
| 管理 | Web・アプリ・ファイル移動の許可範囲を組織で制限 |
| 安全 | 重要操作の確認と道具call の自動レビュー |

**L**: 画面操作が増えるほど、人間の承認画面も増えてしまわないか。

**A**: 設計には連続的な幅があって、全部を都度確認すると仕事にならず、全部を許すと事故範囲が大きい。設計単位は prompt ではなく **権限範囲** だと思います。どのサイトを見られるか、何をダウンロードできるか、どの操作だけ確認するかを先に狭め、その中ではエージェントを動かす。承認 UI は Yes/No の連打ではなく、「今回広げる権限」と「その結果触れられる資源」を見せる必要がある。

**L**: 小さな道具を作る例は、もっと身近だ。

**A**: Simon Willison の Video compressor は、スマートフォンで撮った動画をブログ用に軽くするため、Claude Fable 5.1 を Claude Code for web で動かし、FFmpeg の WebAssembly ビルドを使うブラウザ道具を作ったものです。入力は動画、出力は複数の品質・容量の MP4。サーバーに動画を送る処理を必須にせず、ブラウザ内で変換できる。

これは社内向けAI UIの最小形として見られます。毎回チャットで「この動画を圧縮して」と頼むのではなく、目的に合うプリセットと結果比較を持つ狭い画面に落とす。エージェント型コーディングの価値は、会話を長くすることではなく、繰り返す操作から会話を消すところにもある。

## 導入はライセンス配布では終わらない

**L**: OpenAI のジャーナリズム支援は、単なるアカウント配布とは違う？

**A**: 数字から見ると構造が分かりやすい。2026–2027年度に CUNY Newmark J-School と Northwestern Medill へ400超の ChatGPT Edu 利用権を提供する。それに加えて American Journalism Project の50超の報道組織へ Enterprise と API 利用枠を広げ、強い利用例を再利用可能な道具、基盤、手順書にして共有する。

重要なのは、導入の出力を「利用者数」に置いていないことです。公開記録の分析や記録検索を現場で試し、成功と失敗を組織間で移植できる形にする。ライセンス、研修、作業フロー、共有知識の4層をつないでいます。

**L**: 人間側の役割はどこに残る？

**A**: 記事自身が取材、検証、物語構成、編集判断を残しています。AIが資料を速く読むことと、何を公共的に重要と判断するかは別の層です。ただ、判断を人に残すだけでは運用にならない。どの段階で出典確認を必須にするか、生成物を誰が承認するか、その履歴をどう残すかまで作業フローに埋める必要がある。

**L**: 10代と生成AIの研究助成も、UIや運用の問題に近い。

**A**: OpenAI は13〜17歳への影響を調べる独立研究に500万ドルを出す。対象は利用時間だけではなく、何に使ったか、発達段階、文化や言語、家族・学校の支援、そして安全上の介入や年齢に適した設計です。研究に未成年や機微情報が入る場合は、同意、プライバシー、データセキュリティ、危険の開示への対応、倫理審査を説明させる。

新しくできるのは、若者向け機能を一般的な「安全そう」という印象ではなく、介入の効果を測る根拠基盤に接続することです。まだ結果は出ていないので、助成開始と安全性の証明は分けて考えるべきですが。

**L**: その評価を組織の意思決定に持ち込む人事が Paul Christiano か。

**A**: そう見えます。Christiano は OpenAI Foundation Board に入り、OpenAI Group PBC Board では議決権のないオブザーバー、さらに Safety and Security Committee の一員になる。NIST の CAISI で先端モデル評価に関わり、Alignment Research Center を設立し、OpenAI では RLHF の基礎研究を担った人物です。

Christiano は、技術的な整合と国家安全保障上の能力評価の経験を、Foundation Board と Safety and Security Committee の企業統治に持ち込みます。ただし統治の実効性は、委員会がどの根拠を要求し、どの配備を止められるかで見る必要があります。

## 予測モデルとデータセットの再現性

**L**: Hugging Face の2件は、派手さより再現性の話に見える。

**A**: まず目に入るのは、2026年9月8日時点の GIFT-Eval で、再現可能なゼロショットモデルの中で総合2位、制約の少ないライセンスの範囲では首位という結果です。個別学習なしで、なぜ需要、価格、電力、通信量、遠隔測定値のような異なる時系列を扱えるのか。

IBM の **Granite Time Series PatchTST-FM-r2** は約3.85億パラメータを持ち、最大8192時点の文脈、欠損補完、99分位点の確率予測に対応します。構成の中心は、自己注意機構と時間方向の畳み込みを組み合わせた conformer block です。近距離のパターンを畳み込みが担当し、注意機構を長距離関係に使いやすくする。点予測だけでなく不確実性の幅も出す。この役割分担を公開し、重みと推論パイプライン、評価試験の再現コードまで揃えたことが、順位を検証可能にしています。

> The model weights, architecture, inference pipeline, and code needed to reproduce the benchmark results are all available.

出典: — Hugging Face / IBM

Apache 2.0 または OpenMDW 1.0 を選べます。企業導入では評価値より、「何で学習し、どの条件で測り、同じ結果を再計算できるか」が承認手順を短くすることがあります。

**L**: データセット作成ガイドは、その入口をかなり素朴に見せている。

**A**: Hugging Face Hub API から、直近30日のダウンロード数で並べた最大1000リポジトリのメタデータを取得し、未加工応答と加工済みデータを分けて保存する手順解説です。データセットID、URL、タグ、ダウンロード数、出典、改訂番号、取得時刻を残し、重複や型、欠損を検査する。追加パッケージなしの Python 3.10 で実行できるところまで具体化されています。

個人的には未加工データを消さない点が一番重要です。加工結果がおかしいとき、取得時点の原データに戻れる。9月9日の実行例では、1000件中369件に形式タグがなく、987件で出典文章が返らなかった。欠損を0や空文字で埋めず、何が取得できなかったかを残す。この保存方法は、エージェントの trajectory や道具の結果を後から監査できる形で残す際にも応用できそうです。

## 大規模エージェントが研究の時間軸を変える

**L**: Navier–Stokes をめぐる話は、『オッペンハイマー』のように発見そのものと、発見を生む制度が切り離せない。

**A**: Simon Willison が整理した OpenAI 側の数字は極端です。

- エージェント稼働から解法到達まで: 約88時間
- 全対象でのメッセージ数: 約490万
- 全対象での出力トークン: 約3000億
- Navier–Stokes だけのメッセージ数: 約270万
- Navier–Stokes だけの出力トークン: 約1300億
- Lean による形式化・検証: 追加17時間

これは単一モデルの一発回答ではない。多数のエージェントを走らせ、Lean による形式化と検証へ渡す、大規模計算を前提とした研究工程です。新しく可能になったのは、問題の噂と十分な計算資源があれば、数日で巨大な探索を開始できること。少なくとも OpenAI の説明ではそうです。

**L**: 速さが、先行研究への敬意や未公開情報の扱いを追い越す。

**A**: そこが Simon と Terence Tao の指摘です。別チームが長期間取り組んだ未公開研究の噂が、大量のエージェントを投入する契機になり得る。Tao は、有望な未解決問題を共有すると先に大規模計算で解かれるなら、研究方向を公開しない誘因が生まれ、開かれた科学を損なうと警告しています。

さらに Simon は、製品利用データが「モデル性能の改善」に使われるとは具体的に何を意味するのか、と問い直す。個別利用者データを解法時に参照しないことと、過去の利用が将来モデルの改善に影響しないことは同じではない。ここは来歴とデータ方針を、短いプライバシー文言ではなく研究競争上の能力として扱う必要がある。

**L**: 画像生成の更新は、その重い話と対照的に、日常の制作ループを短くする。

**A**: ChatGPT Images 2.5 は複数対話ターンでの指示追従、応答速度、参照写真の主体保持を改善した。API には編集精度を重視する **gpt-image-2.5-sunburst** と、日常用途の速度と品質を重視する **gpt-image-2.5-flare** がある。Simon は自作 CLI を複数参照画像に対応させています。

~~~bash
uv run openai_image.py \\
  "add a raccoon scientist studying the chart thoughtfully" \\
  -i reference.webp \\
  -m gpt-image-2.5-sunburst
~~~

この更新により、参照画像の主体を保ったまま、会話で編集を重ねられるようになります。社内サービスなら、モデル選択欄より「高速な初稿」と「主体を保つ精密編集」を操作として見せる方が分かりやすいと思います。

**L**: 人間は、より大きな探索をAIに渡しながら、何を共有するか、どこで止めるかを決め続けることになる。

**A**: 今日の10件をまとめると、**モデル能力から動作境界へ** という方向が見えます。Astra の権限制御、報道現場の手順書、未成年研究の倫理審査、公開モデルの来歴、未加工データの保存、大規模研究 harness の優先権。モデルが何を生成できるかより、何を入力にでき、どこまで動けて、誰が検証し、結果の履歴をどう残すか。エージェント工学は、その境界を実装して観測するシステム工学になってきています。

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
