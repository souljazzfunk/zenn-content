"""article-fix.py / article-check.py / topic_emoji.py の回帰テスト。

    python3 -m unittest discover -s openclaw/fleet/zenn-content/tests

スクリプトは自分の親ディレクトリの articles/ を読むので、一時ディレクトリに scripts/ を複製して動かす。
標準ライブラリのみ。
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
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
        section = text[text.index("## アイコン（emoji）の選び方"):]
        rows = [l.split("|")[1].strip() for l in section.splitlines() if l.startswith("| ") and "emoji" not in l]
        self.assertEqual(rows, [e for e, _, _ in topic_emoji.TOPIC_EMOJI] + [topic_emoji.FALLBACK_EMOJI])


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

    def run_script(self, name):
        p = subprocess.run([sys.executable, str(self.tmp / "scripts" / name), SLUG, "--json-only",
                            "--rules", str(self.tmp / "missing-rules.md")],
                           capture_output=True, text=True)
        return json.loads(p.stdout.strip().splitlines()[-1])

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


if __name__ == "__main__":
    unittest.main()
