"""topic_emoji.py — 対話記事の frontmatter `emoji` をその日の主題から選ぶ対応表。シリーズごとに表を持つ。

zenn-style.md の「アイコン（emoji）の選び方」節と同じ表。変えるときは両方を合わせる。
article-fix.py（表に無い emoji を主題から選び直す）と article-check.py（表に無い emoji を不合格にする）が使う。
MACHINE_PICKED のシリーズは、書き手の選んだ emoji を使わず、article-fix.py が常に pick() の結果で書き換え、
article-check.py は pick() と違う emoji を不合格にする。
標準ライブラリのみ。
"""

# (emoji, 主題, 主題・見出し・本文で数えるキーワード)。点数の付け方は pick() を参照。同点なら上の行を優先する
TOPIC_EMOJI = [
    ("🛡️", "安全性・境界・権限", ["安全", "セキュリティ", "脆弱", "権限", "ガバナンス", "サンドボックス", "境界", "承認", "security", "safety"]),
    ("🔌", "MCP・ツール連携", ["MCP", "ツール", "コネクタ", "ゲートウェイ", "API", "connector"]),
    ("🤝", "マルチエージェント・オーケストレーション", ["マルチエージェント", "オーケストレーション", "サブエージェント", "協調", "subagent"]),
    ("💻", "エージェント型コーディング", ["Claude Code", "Codex", "OpenClaw", "コーディング", "開発", "コード", "coding"]),
    ("📊", "評価・ベンチマーク", ["評価", "ベンチマーク", "検証", "測定", "eval", "benchmark"]),
    ("🔁", "ハーネス・ループ・長時間稼働", ["ハーネス", "ループ", "長時間", "常時稼働", "再試行", "harness", "loop"]),
    ("🧩", "スキル・ナレッジ化", ["スキル", "ナレッジ", "CLAUDE.md", "手順書", "メモリ", "記憶", "skill"]),
    ("🏢", "社内活用・チーム導入", ["社内", "チーム", "業務", "企業", "導入", "Slack", "Team", "Enterprise"]),
    ("🏠", "生活の自動化・パーソナルエージェント", ["生活", "パーソナル", "個人", "家庭", "定期ジョブ"]),
    ("🖼️", "画像・音声・動画", ["画像", "音声", "動画", "マルチモーダル", "image", "voice", "video"]),
    ("🎓", "イベント・コース・学習", ["イベント", "ウェビナー", "コース", "講座", "学習", "教育", "webinar", "course"]),
    ("🔬", "研究・論文", ["研究", "論文", "解釈", "interpretability", "research"]),
    ("🧠", "新モデル・推論", ["新モデル", "小さなモデル", "推論", "Fable", "Opus", "Sonnet", "Haiku", "GPT", "Gemini", "reasoning"]),
]
FALLBACK_EMOJI = "📰"  # どれにも当たらない日（話題が散らばった日）
ALLOWED_EMOJI = {e for e, _, _ in TOPIC_EMOJI} | {FALLBACK_EMOJI}

# Learning Watch は毎回「学習」の話なので、Tech Watch の表では 🎓 か 📊 にしか当たらない。
# watch/learning-watch.crawl.md の 8 観点から作った別表を使う
LEARNING_EMOJI = [
    ("🧭", "差分の診断", ["スキルギャップ", "差分", "診断", "能力の差", "足りない", "skills gap", "gap"]),
    ("📚", "社内資料への RAG", ["社内資料", "RAG", "一次資料", "出典", "ナレッジベース", "社内文書", "retrieval-augmented"]),
    ("💬", "AI チューター", ["チューター", "ヒント", "問い返", "訂正", "答えを先に", "代行", "考えさせ", "tutor"]),
    ("🃏", "想起練習", ["想起", "思い出", "小テスト", "出題", "retrieval practice"]),
    ("📅", "分散練習", ["分散", "間隔", "復習", "再出題", "spaced"]),
    ("🎭", "シミュレーションとロールプレイ", ["ロールプレイ", "シミュレーション", "演じ", "練習相手", "roleplay", "simulation"]),
    ("🛠️", "実務への転移", ["転移", "実務", "職場", "現場", "仕事で使", "transfer"]),
    ("📏", "測定", ["測定", "測る", "測り", "測れ", "点数", "成績", "効果", "time to competence"]),
]
LEARNING_FALLBACK = "🎓"

# シリーズの key（series.py）→ (表, どれにも当たらないときの emoji)
TABLES = {
    "tech-watch": (TOPIC_EMOJI, FALLBACK_EMOJI),
    "learning-watch": (LEARNING_EMOJI, LEARNING_FALLBACK),
}
MACHINE_PICKED = frozenset({"learning-watch"})  # 書き手が 11-17〜11-21 に 3 回続けて 📊 を選んだ（台帳 F214）


def normalize(emoji):
    """異体字セレクタ（U+FE0F）の有無を同一視する。"""
    return (emoji or "").replace("️", "")


def allowed(series="tech-watch"):
    table, fallback = TABLES[series]
    return {e for e, _, _ in table} | {fallback}


def is_allowed(emoji, series="tech-watch"):
    return normalize(emoji) in {normalize(e) for e in allowed(series)}


def same(a, b):
    return normalize(a) == normalize(b)


def pick(subject, body="", series="tech-watch"):
    """タイトルの主題（「<シリーズ名> YYYY-MM-DD: 」の後ろ）と本文から emoji を選ぶ。

    キーワードの出現回数を数え、主題は 5 倍、`## ` 見出しは 3 倍、それ以外の本文は 1 倍で重み付けする。
    最高点の行を選び、同点なら表の上の行を優先する。どこにも当たらなければそのシリーズの fallback。
    """
    table, fallback = TABLES[series]
    lines = (body or "").splitlines()
    headings = "\n".join(l for l in lines if l.startswith("## ")).lower()
    rest = "\n".join(l for l in lines if not l.startswith("## ")).lower()
    subject = (subject or "").lower()
    best, best_score = fallback, 0
    for emoji, _, keywords in table:
        score = sum(5 * subject.count(k.lower()) + 3 * headings.count(k.lower()) + rest.count(k.lower())
                    for k in keywords)
        if score > best_score:
            best, best_score = emoji, score
    return best
