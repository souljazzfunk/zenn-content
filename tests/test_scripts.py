"""article-fix.py / article-check.py / topic_emoji.py の回帰テスト。

    python3 -m unittest discover -s openclaw/fleet/zenn-content/tests

スクリプトは自分の親ディレクトリの articles/ を読むので、一時ディレクトリに scripts/ を複製して動かす。
標準ライブラリのみ。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import learning_watch_article as lw  # noqa: E402
import topic_emoji  # noqa: E402

SLUG = "20261010-tech-watch"
ARTICLE = """---
title: "Tech Watch 2026-10-10: {subject}"
emoji: "{emoji}"
type: "tech"
topics:
  - "AI"
published: false
---
本文
"""
LW_SHORT = ARTICLE.replace("Tech Watch 2026-10-10", "Learning Watch 2026-11-17")


def knowledge(name):
    # life-automation では fleet/shared/knowledge/、Deploy 先の VPS では ~/.openclaw/shared/knowledge/ にある
    return next(p for p in (Path(__file__).resolve().parents[2] / "shared" / "knowledge" / name,
                            Path.home() / ".openclaw" / "shared" / "knowledge" / name) if p.exists())


class TopicEmojiTest(unittest.TestCase):
    def test_pick_by_subject(self):
        cases = {
            "MCP ゲートウェイの設計": "🔌",
            "Claude Code のフック設計": "💻",
            "Opus 5.5 の発表": "🧠",
            "評価ループの作り方": "📊",
            "長時間稼働エージェント": "🔁",
            "Slack で使う Claude": "🏢",
            "ウェビナー三本": "🎓",
            "今日の雑多なニュース": topic_emoji.FALLBACK_EMOJI,
        }
        for subject, want in cases.items():
            self.assertEqual(topic_emoji.pick(subject), want, subject)

    def test_pick_uses_headings_and_body(self):
        body = "## 承認の境界を決める\n権限と境界の話。\n## もう一つの境界\n"
        self.assertEqual(topic_emoji.pick("運用の話", body), "🛡️")

    def test_old_mic_is_not_allowed(self):
        self.assertFalse(topic_emoji.is_allowed("🎙️"))

    def test_variation_selector_is_ignored(self):
        self.assertTrue(topic_emoji.is_allowed("🛡️"))
        self.assertTrue(topic_emoji.is_allowed("🛡"))

    def test_style_table_matches_module(self):
        # life-automation では fleet/shared/knowledge/、Deploy 先の VPS では ~/.openclaw/shared/knowledge/ にある
        style = next(p for p in (Path(__file__).resolve().parents[2] / "shared" / "knowledge" / "zenn-style.md",
                                 Path.home() / ".openclaw" / "shared" / "knowledge" / "zenn-style.md") if p.exists())
        text = style.read_text(encoding="utf-8")
        block = text[text.index("## シリーズごとの決まり"):]
        tech, learning = block[block.index("### tech-watch"):].split("### learning-watch")

        def rows(part):
            return [l.split("|")[1].strip() for l in part.splitlines() if l.startswith("| ") and "emoji" not in l]

        self.assertEqual(rows(tech), [e for e, _, _ in topic_emoji.TOPIC_EMOJI] + [topic_emoji.FALLBACK_EMOJI])
        self.assertEqual(rows(learning), [e for e, _, _ in topic_emoji.LEARNING_EMOJI] + [topic_emoji.LEARNING_FALLBACK])


class LearningEmojiTest(unittest.TestCase):
    """Learning Watch は 8 観点の表から選ぶ。Tech Watch の表では毎回 🎓 か 📊 になる（台帳 F214）。"""

    def test_pick_by_subject_from_the_learning_table(self):
        cases = {
            "学習を代行しないAI設計": "💬",
            "想起練習を AI に出題させる": "🃏",
            "間隔を空けた復習": "📅",
            "障害対応のロールプレイ": "🎭",
            "社内資料に出典を付ける": "📚",
            "学んだつもりを測り直す": "📏",
            "今日の雑多な話題": topic_emoji.LEARNING_FALLBACK,
        }
        for subject, want in cases.items():
            self.assertEqual(topic_emoji.pick(subject, series="learning-watch"), want, subject)

    def test_each_series_allows_only_its_own_table(self):
        self.assertTrue(topic_emoji.is_allowed("📊", "tech-watch"))
        self.assertFalse(topic_emoji.is_allowed("📊", "learning-watch"))
        self.assertTrue(topic_emoji.is_allowed("🛠", "learning-watch"))
        self.assertFalse(topic_emoji.is_allowed("🃏", "tech-watch"))


class ImportlibLoadTest(unittest.TestCase):
    def test_check_loads_without_scripts_on_path(self):
        """zenn-content の tests は article-check.py を importlib で読み込む。sys.path に scripts/ が無くても動くこと。"""
        code = ("import importlib.util, sys; sys.path = [p for p in sys.path if 'scripts' not in p]; "
                f"spec = importlib.util.spec_from_file_location('ac', {str(SCRIPTS / 'article-check.py')!r}); "
                "spec.loader.exec_module(importlib.util.module_from_spec(spec))")
        subprocess.run([sys.executable, "-c", code], check=True, cwd=tempfile.gettempdir())


class ScriptsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        shutil.copytree(SCRIPTS, self.tmp / "scripts")
        (self.tmp / "articles").mkdir()
        self.article = self.tmp / "articles" / f"{SLUG}.md"

    def run_slug(self, name, slug, home=None, rules=None):
        p = subprocess.run([sys.executable, str(self.tmp / "scripts" / name), slug, "--json-only",
                            "--rules", str(rules or self.tmp / "missing-rules.md")],
                           capture_output=True, text=True, env={**os.environ, "HOME": str(home or self.tmp / "home")})
        return p.returncode, json.loads(p.stdout.strip().splitlines()[-1])

    def run_script(self, name):
        return self.run_slug(name, SLUG)[1]

    def emoji_failures(self):
        return [f for f in self.run_script("article-check.py")["failures"] if "EMOJI" in f]

    def test_fix_replaces_old_mic(self):
        self.article.write_text(ARTICLE.format(subject="MCP ゲートウェイの設計", emoji="🎙️"), encoding="utf-8")
        out = self.run_script("article-fix.py")
        self.assertEqual(out["emoji"], {"from": "🎙️", "to": "🔌"})
        self.assertIn('emoji: "🔌"', self.article.read_text(encoding="utf-8"))
        self.assertEqual(self.emoji_failures(), [])

    def test_fix_keeps_allowed_emoji(self):
        self.article.write_text(ARTICLE.format(subject="MCP ゲートウェイの設計", emoji="🧠"), encoding="utf-8")
        self.assertIsNone(self.run_script("article-fix.py")["emoji"])
        self.assertIn('emoji: "🧠"', self.article.read_text(encoding="utf-8"))

    def test_check_rejects_emoji_outside_table(self):
        self.article.write_text(ARTICLE.format(subject="MCP ゲートウェイの設計", emoji="🎙️"), encoding="utf-8")
        self.assertEqual(len(self.emoji_failures()), 1)

    def test_check_exits_zero_on_a_failing_article_so_openclaw_does_not_report_bash_failed(self):
        self.article.write_text(ARTICLE.format(subject="MCP ゲートウェイの設計", emoji="🎙️"), encoding="utf-8")
        code, out = self.run_slug("article-check.py", SLUG)
        self.assertIs(out["pass"], False)
        self.assertEqual(code, 0)

    def test_check_fails_a_slug_of_no_known_series(self):
        notes = self.tmp / "articles" / "20261117-notes.md"
        notes.write_text(ARTICLE.format(subject="x", emoji="🧠").replace("Tech Watch 2026-10-10", "Notes"), encoding="utf-8")
        code, out = self.run_slug("article-check.py", "20261117-notes")
        self.assertEqual(code, 1)
        self.assertIs(out["pass"], False)
        self.assertIs(out["skipped"], False)
        self.assertEqual([f.split(":")[0] for f in out["failures"]], ["FAILURE_SLUG_FORMAT"])
        self.assertIn("tech-watch", out["failures"][0])

    def test_check_wants_the_title_to_carry_the_series_and_the_date_of_the_slug(self):
        def title_or_slug_failures():
            return [f.split(":")[0] for f in self.run_script("article-check.py")["failures"] if "TITLE" in f or "SLUG" in f]
        self.article.write_text(ARTICLE.format(subject="MCP ゲートウェイの設計", emoji="🔌"), encoding="utf-8")
        self.assertEqual(title_or_slug_failures(), [])
        self.article.write_text(ARTICLE.format(subject="x", emoji="🔌").replace("2026-10-10", "2026-10-11"), encoding="utf-8")
        self.assertEqual(title_or_slug_failures(), ["FAILURE_TITLE_FORMAT"])

    def test_check_reads_the_seen_list_of_the_series_when_no_seen_path_is_given(self):
        def seen_missing():
            return [w for w in self.run_script("article-check.py")["warnings"] if "WARNING_SEEN_MISSING" in w]
        self.article.write_text(ARTICLE.format(subject="x", emoji="🔌"), encoding="utf-8")
        self.assertEqual(len(seen_missing()), 1)
        state = self.tmp / "home/.openclaw/workspace/state"
        state.mkdir(parents=True)
        (state / "tech-watch-seen.json").write_text("[]", encoding="utf-8")
        self.assertEqual(seen_missing(), [])

    def test_fix_leaves_a_slug_of_no_known_series_untouched(self):
        notes = self.tmp / "articles" / "20261117-notes.md"
        text = ARTICLE.format(subject="x", emoji="🎙️")
        notes.write_text(text, encoding="utf-8")
        code, out = self.run_slug("article-fix.py", "20261117-notes")
        self.assertEqual(code, 2)
        self.assertIs(out["changed"], False)
        self.assertIn("tech-watch", out["error"])
        self.assertEqual(notes.read_text(encoding="utf-8"), text)

    def write(self, slug, text):
        (self.tmp / "articles" / f"{slug}.md").write_text(text, encoding="utf-8")

    def title_or_slug_failures(self, slug):
        code, out = self.run_slug("article-check.py", slug)
        self.assertIs(out["skipped"], False)
        return [f.split(":")[0] for f in out["failures"] if "TITLE" in f or "SLUG" in f]

    def test_check_takes_a_learning_watch_title_under_a_learning_watch_slug(self):
        self.write(lw.SLUG, LW_SHORT.format(subject="x", emoji="🏢"))
        self.assertEqual(self.title_or_slug_failures(lw.SLUG), [])

    def test_check_fails_the_title_of_one_series_under_the_slug_of_the_other(self):
        self.write("20261117-tech-watch", LW_SHORT.format(subject="x", emoji="🏢"))
        self.assertEqual(self.title_or_slug_failures("20261117-tech-watch"), ["FAILURE_TITLE_FORMAT"])
        self.write(lw.SLUG, ARTICLE.format(subject="x", emoji="🏢").replace("2026-10-10", "2026-11-17"))
        self.assertEqual(self.title_or_slug_failures(lw.SLUG), ["FAILURE_TITLE_FORMAT"])

    def test_fix_picks_the_emoji_of_a_learning_watch_article_from_its_subject(self):
        self.write(lw.SLUG, LW_SHORT.format(subject="想起練習を AI に出題させる", emoji="🎙️"))
        code, out = self.run_slug("article-fix.py", lw.SLUG)
        self.assertEqual(out["emoji"], {"from": "🎙️", "to": "🃏"})

    def slug_emoji_failures(self, slug):
        return [f for f in self.run_slug("article-check.py", slug)[1]["failures"] if "EMOJI" in f]

    def test_fix_replaces_the_writers_emoji_of_a_learning_watch_article_even_when_it_is_in_the_table(self):
        # 11-17〜11-21 の 3 本は書き手が 📊 を選び、表にあったので直らなかった（台帳 F214）
        self.write(lw.SLUG, LW_SHORT.format(subject="学んだつもりを測り直す", emoji="💬"))
        self.assertEqual(len(self.slug_emoji_failures(lw.SLUG)), 1)
        code, out = self.run_slug("article-fix.py", lw.SLUG)
        self.assertEqual(out["emoji"], {"from": "💬", "to": "📏"})
        self.assertEqual(self.slug_emoji_failures(lw.SLUG), [])

    def test_learning_watch_rejects_the_tech_watch_table(self):
        self.write(lw.SLUG, LW_SHORT.format(subject="学んだつもりを測り直す", emoji="📊"))
        self.assertEqual(len(self.slug_emoji_failures(lw.SLUG)), 1)
        self.assertEqual(self.run_slug("article-fix.py", lw.SLUG)[1]["emoji"], {"from": "📊", "to": "📏"})

    def test_tech_watch_keeps_the_writers_emoji_from_its_table(self):
        self.write("20261118-tech-watch", ARTICLE.format(subject="MCP ゲートウェイの設計", emoji="🧠")
                   .replace("2026-10-10", "2026-11-18"))
        self.assertIsNone(self.run_slug("article-fix.py", "20261118-tech-watch")[1]["emoji"])
        self.assertEqual(self.slug_emoji_failures("20261118-tech-watch"), [])

    def test_a_full_learning_watch_article_passes_the_check_against_its_own_seen_list(self):
        self.write(lw.SLUG, lw.ARTICLE)
        state = self.tmp / "home/.openclaw/workspace/state"
        state.mkdir(parents=True)
        urls = [line.strip() for line in lw.ARTICLE.splitlines() if line.strip().startswith("https://")]
        (state / "learning-watch-seen.json").write_text(json.dumps(urls), encoding="utf-8")
        code, out = self.run_slug("article-check.py", lw.SLUG, rules=knowledge("writing-rules.md"))
        self.assertEqual((code, out["failures"]), (0, []))
        self.assertIs(out["pass"], True)
        self.assertEqual((out["stats"]["list_items"], out["stats"]["list_urls_not_in_seen"]), (3, 0))
        self.assertEqual([w for w in out["warnings"] if "SEEN" in w], [])


if __name__ == "__main__":
    unittest.main()
