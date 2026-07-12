---
title: "AI調査コンテンツのリッチHTMLアーカイブ戦略"
emoji: "🗂️"
type: "tech"
topics:
  - "ai"
  - "html"
  - "markdown"
  - "github"
  - "cloudflare"
published: true
---

#### AIが書きました🤖
この記事は、AIが書いたものを人間が確認してから投稿しています。

結論として、**Markdownを捨ててHTMLへ移行する**というより、**MarkdownやJSONを原本、リッチHTMLを配布用のビルド成果物として両方残す**設計が一番きれいです。

HTMLを置けるのはレンタルサーバーだけではありません。GitHub Pages、Cloudflare Pages、Netlifyはいずれも静的なHTML、CSS、画像、JavaScriptをそのまま配信できます。GitHub Pagesはリポジトリ内の静的ファイルを公開でき、Cloudflare Pagesもフレームワークなしの静的HTMLをGit連携で自動デプロイできます。([docs.github.com](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages?utm_source=chatgpt.com))

## 推奨構成

**GitHubを保管庫、Cloudflare Pagesを閲覧場所にする**形が、今の用途には一番バランスが良いです。

```text
AI調査エージェント
  ↓
report package を生成
  ↓
GitHub repository に commit
  ↓
CIで検証・サニタイズ・索引生成
  ↓
Cloudflare Pages に自動デプロイ
  ↓
公開用サイト / Access付き非公開サイト
```

リポジトリは単なるHTML置き場ではなく、調査成果物の台帳になります。

```text
research-archive/
├─ reports/
│  └─ 2026/
│     └─ 06/
│        └─ ai-research-archive/
│           ├─ index.html
│           ├─ source.md
│           ├─ manifest.json
│           ├─ sources.json
│           ├─ assets/
│           │  ├─ chart-01.png
│           │  └─ cover.webp
│           └─ snapshot.pdf
├─ templates/
├─ scripts/
└─ public/
```

`index.html` は読者向けの完成版、`source.md` は検索、差分確認、再編集用、`manifest.json` はタイトル、タグ、作成日時、生成モデル、元URL、ライセンス、ハッシュなどの機械可読な台帳です。

## 役割分担

| 層 | 保存するもの | 目的 |
|---|---|---|
| 原本 | Markdown、JSON、引用元URL、調査メモ | 再利用、差分確認、再生成 |
| 表示物 | HTML、CSS、画像、図表、埋め込みメディア | 人間向けの読書体験 |
| 固定版 | ZIP、PDF、Git tag、Release asset | 後から内容が変わらない証跡 |
| 公開面 | Cloudflare Pages または GitHub Pages | 閲覧、検索、共有 |

GitHub Releasesには多数の配布ファイルを添付でき、immutable releaseを使えば、公開後にタグや添付成果物を変えられない形にもできます。調査レポートの確定版や月次アーカイブには相性が良いです。([docs.github.com](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases?utm_source=chatgpt.com))

## ホスティングの選び方

| 選択肢 | 向く用途 | 強み | 注意点 |
|---|---|---|---|
| GitHub Pages | 公開ブログ、個人ナレッジベース | Gitだけで完結、最も簡単 | 通常は公開前提。機密保護には向かない |
| Cloudflare Pages | 公開と限定共有が混在するアーカイブ | Git pushで自動デプロイ、静的HTML対応、ヘッダー制御、Access連携 | 初回だけCloudflare設定が必要 |
| Netlify | レビュー付き編集フロー、複数人運用 | Deploy Previewが使いやすい | 静的アーカイブだけなら少し機能過多 |
| 自前VPS | 独自認証や特殊処理が必要 | 完全な自由度 | 保守、パッチ、監視を自分で持つ必要がある |

Cloudflare PagesはGitHubまたはGitLabへのpushで自動デプロイでき、Pull RequestごとにプレビューURLも作れます。静的ファイルへのカスタムヘッダーも `_headers` で管理できます。([developers.cloudflare.com](https://developers.cloudflare.com/pages/configuration/git-integration/github-integration/?utm_source=chatgpt.com))

NetlifyもGit連携による継続デプロイとDeploy Previewを提供しているため、編集レビューを重視するなら有力です。ただし、個人または小規模の調査アーカイブであれば、Cloudflare Pagesの方が「静的コンテンツを置く」目的に対して素直です。([docs.netlify.com](https://docs.netlify.com/api-and-cli-guides/cli-guides/get-started-with-cli/?utm_source=chatgpt.com))

## セキュリティ上の考え方

HTMLを置くこと自体が危険なのではありません。静的ホスティングは通常、PHPやサーバー側コードを実行せず、HTML、CSS、JSを配信するだけです。注意すべきなのは、**AIが生成したHTML内のJavaScript、外部iframe、外部画像、追跡タグ、リンク先**です。

AI生成HTMLは以下を基本ルールにすると安全です。

- `<script>`、`onclick` などのイベント属性、埋め込みフォームを禁止する
- 画像や動画は可能な限りローカルの `assets/` に保存する
- 外部埋め込みはYouTube、Vimeo、Google Mapsなど明示許可したドメインだけに限定する
- HTMLを公開前にサニタイズする
- CSPを設定し、許可していないJavaScriptや外部読み込みを止める
- 公開サイトとログインや業務ツールのドメインを分ける
- 個人情報、社内情報、APIキー、会議URLを公開成果物に含めない

OWASPはCSPをXSS対策の追加防御として推奨しており、Cloudflare PagesとNetlifyはいずれもレスポンスヘッダーでCSPを設定できます。([cheatsheetseries.owasp.org](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html?utm_source=chatgpt.com))

GitHub Pagesは、リポジトリがprivateでも通常は公開される前提で考えるべきです。非公開の調査アーカイブには使わず、Cloudflare Accessなどの認証レイヤーを置く方が安全です。Cloudflare AccessはIDベースのプロキシとして前段に置けます。([docs.github.com](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https?utm_source=chatgpt.com))

## 実務的にはこの運用がよいです

1. AIには自由なHTMLを書かせるのではなく、`summary`、`key_findings`、`risks`、`sources`、`media` のような構造化データを生成させる。
2. テンプレート側で、重要事項は青、リスクは赤、判断事項は紫、推奨アクションは緑のように意味ごとのコンポーネントとして描画する。
3. 最後にHTMLをビルドして保存する。
4. Git pushでCloudflare Pagesへ公開する。
5. 公開版とは別に、HTML一式をZIPとPDFでReleaseへ固定する。

これなら、AIが毎回独自デザインのHTMLを吐いて保守不能になる問題を避けられます。色やレイアウトはテンプレートに集約し、AIには「何が重要か」を構造化して出させる役割を持たせます。

**2026年っぽい最適解は、Gitを証跡と原本の台帳にし、静的HTMLをビルド成果物としてCloudflare Pagesへ出し、必要ならCloudflare Accessで閉じる構成**です。GitHub Pagesは公開専用の最短ルート、Netlifyはレビュー体験を重視する場合の代替、VPSは特殊要件が出るまで不要です。
