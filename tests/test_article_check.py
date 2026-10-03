#!/usr/bin/env python3

import importlib.util
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "article_check", REPO / "scripts" / "article-check.py"
)
ARTICLE_CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ARTICLE_CHECK)
ARTIFACTS = Path(
    "/home/ubuntu/.openclaw/shared/artifacts/checks/20260922-tech-watch"
)


def main_lines(text):
    _, body = ARTICLE_CHECK.parse_frontmatter(text)
    lines = body.splitlines()
    list_idx = next(
        i for i, line in enumerate(lines) if line.startswith("## 今日の")
    )
    list_end = next(
        i for i in range(list_idx + 1, len(lines)) if lines[i].startswith("## ")
    )
    return lines[:list_idx] + lines[list_end:]


class SpeakerLabelTest(unittest.TestCase):
    @unittest.skipUnless(ARTIFACTS.exists(), "local review artifacts unavailable")
    def test_historical_unlabeled_paragraphs_are_detected(self):
        text = (ARTIFACTS / "run-2.article.md").read_text(encoding="utf-8")
        self.assertEqual(
            4,
            len(ARTICLE_CHECK.unlabeled_dialogue_paragraphs(main_lines(text))),
        )

    @unittest.skipUnless(ARTIFACTS.exists(), "local review artifacts unavailable")
    def test_corrected_final_version_is_accepted(self):
        text = (ARTIFACTS / "run-3.article.md").read_text(encoding="utf-8")
        self.assertEqual(
            [], ARTICLE_CHECK.unlabeled_dialogue_paragraphs(main_lines(text))
        )

    def test_each_prose_paragraph_requires_its_own_label(self):
        lines = [
            "**L**: 問い。", "", "## テーマ", "", "**A**: 一段目。", "",
            "同じ話者の二段目。", "", "**L**: 次の問い。",
        ]
        self.assertEqual(
            ["同じ話者の二段目。"],
            ARTICLE_CHECK.unlabeled_dialogue_paragraphs(lines),
        )

    def test_structural_blocks_do_not_need_labels(self):
        lines = [
            "**L**: 問い。", "", "## テーマ", "", "**A**: 説明。", "",
            "```text", "code", "```", "", "| 列 |", "| --- |", "| 値 |", "",
            "> 引用", "", "- 箇条書き", "", ":::message", "注記", "", "続き", ":::", "",
            "**L**: 次の問い。",
        ]
        self.assertEqual([], ARTICLE_CHECK.unlabeled_dialogue_paragraphs(lines))


class MarkdownSignalTest(unittest.TestCase):
    def test_raw_escape_outside_code_is_detected(self):
        text = "**A**: 前半。\\n\\n**L**: 後半。\n```text\n\\n\\t\n```\n`\\n`"
        self.assertEqual(["\\n", "\\n"], ARTICLE_CHECK.raw_escape_sequences(text))

    def test_numeric_density_flags_three_values_in_prose(self):
        lines = ["**A**: 成功率は 90%、99%、99.9% と段階的に上がった。"]
        self.assertEqual(1, len(ARTICLE_CHECK.numeric_density_candidates(lines)))

    def test_numeric_density_ignores_structures_dates_urls_and_code(self):
        lines = [
            "**A**: 2026-10-03 に公開した。",
            "| 1 | 2 | 3 |",
            "- 1、2、3",
            "> 1、2、3",
            "```text", "1 2 3", "```",
            "**A**: https://example.com/1/2/3 を参照した。",
        ]
        self.assertEqual([], ARTICLE_CHECK.numeric_density_candidates(lines))

    def test_numeric_density_treats_compound_values_as_single_values(self):
        lines = [
            "**A**: 1万6000人が100万件を処理した。",
            "**L**: 9×9数独を約15秒で解いた。",
            "**A**: 料金は5分の1である。",
            "**A**: Claude Fable 5.1 は62点で、費用を36%減らした。",
            "**A**: SWE-2 はSWE-1.7より127から53へ減らした。",
            "**A**: HTML 5 Canvasへ3枚を描いた。",
        ]
        self.assertEqual([], ARTICLE_CHECK.numeric_density_candidates(lines))


if __name__ == "__main__":
    unittest.main(verbosity=2)
