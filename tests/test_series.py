"""series.py の回帰テスト。

    python3 -m unittest discover -s openclaw/fleet/zenn-content/tests

標準ライブラリのみ。
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import series  # noqa: E402

MON_TO_SAT = series.validated((
    series.Series("a-watch", "A Watch", frozenset({1, 3, 5})),
    series.Series("b-watch", "B Watch", frozenset({2, 4, 6})),
))


def cli(*args, today=None):
    env = {k: v for k, v in os.environ.items() if k != "WATCH_TODAY"}
    env["HOME"] = "/home/ubuntu"
    if today:
        env["WATCH_TODAY"] = today
    return subprocess.run([sys.executable, str(SCRIPTS / "series.py"), *args], env=env, capture_output=True, text=True)


class Cli(unittest.TestCase):
    def test_today_on_a_monday_prints_the_tech_watch_run(self):
        p = cli("today", today="2026-11-16")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout.strip().splitlines()[-1]), {
            "run": True, "series": "tech-watch", "head": "Tech Watch 2026-11-16", "slug": "20261116-tech-watch",
            "crawl_prompt": "/home/ubuntu/.openclaw/workspace/watch/tech-watch.crawl.md",
            "seen": "/home/ubuntu/.openclaw/workspace/state/tech-watch-seen.json",
            "extra": "/home/ubuntu/.openclaw/workspace/state/tech-watch-extra.json",
        })

    def test_today_on_a_tuesday_prints_the_learning_watch_run(self):
        p = cli("today", today="2026-11-17")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout.strip().splitlines()[-1]), {
            "run": True, "series": "learning-watch", "head": "Learning Watch 2026-11-17", "slug": "20261117-learning-watch",
            "crawl_prompt": "/home/ubuntu/.openclaw/workspace/watch/learning-watch.crawl.md",
            "seen": "/home/ubuntu/.openclaw/workspace/state/learning-watch-seen.json",
            "extra": "/home/ubuntu/.openclaw/workspace/state/learning-watch-extra.json",
        })

    def test_an_unknown_command_is_an_error(self):
        self.assertEqual(cli("yesterday").returncode, 2)

    def test_a_day_no_series_owns_prints_run_false_and_exits_0(self):
        out = io.StringIO()
        with mock.patch.object(series, "SERIES", MON_TO_SAT), mock.patch.dict(os.environ, {"WATCH_TODAY": "2026-11-15"}), \
                contextlib.redirect_stdout(out):
            code = series.main(["today"])
        self.assertEqual(code, 0)
        res = json.loads(out.getvalue().strip().splitlines()[-1])
        self.assertIs(res["run"], False)
        self.assertIn("2026-11-15", res["say"])


class Policy(unittest.TestCase):
    """依頼「tech watchは月水金にして、火木土は…学習支援の事例や記事を…紹介するようにして、日曜日はお休みにしよう」の曜日。"""

    def test_tech_watch_runs_mon_wed_fri_learning_watch_runs_tue_thu_sat_and_sunday_runs_nothing(self):
        want = {"2026-11-15": None, "2026-11-16": "tech-watch", "2026-11-17": "learning-watch", "2026-11-18": "tech-watch",
                "2026-11-19": "learning-watch", "2026-11-20": "tech-watch", "2026-11-21": "learning-watch"}
        for day, key in want.items():
            p = cli("today", today=day)
            self.assertEqual(p.returncode, 0, p.stderr)
            out = json.loads(p.stdout.strip().splitlines()[-1])
            if key is None:
                self.assertEqual((out["run"], day in out["say"]), (False, True), day)
            else:
                self.assertEqual((out["run"], out["series"], out["slug"]), (True, key, f"{day.replace('-', '')}-{key}"), day)

    def test_the_job_is_scheduled_at_six_from_monday_to_saturday_in_japan(self):
        p = cli("cron")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout, "0 6 * * 1-6\tAsia/Tokyo\n")


class Today(unittest.TestCase):
    def test_the_day_is_the_date_in_japan(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("WATCH_TODAY", None)
            run = series.today(datetime(2026, 11, 15, 22, 0, tzinfo=timezone.utc))
        self.assertEqual(run.slug, "20261116-tech-watch")

    def test_each_weekday_goes_to_the_series_that_owns_it(self):
        with mock.patch.object(series, "SERIES", MON_TO_SAT):
            got = [(r.series.key if r else None) for r in (series.for_day(date(2026, 11, d)) for d in range(15, 22))]
        self.assertEqual(got, [None, "a-watch", "b-watch", "a-watch", "b-watch", "a-watch", "b-watch"])


class OfSlug(unittest.TestCase):
    def test_a_series_slug_gives_its_run(self):
        run = series.of_slug("20261116-tech-watch")
        self.assertEqual((run.series.key, run.day, run.slug, run.head),
                         ("tech-watch", date(2026, 11, 16), "20261116-tech-watch", "Tech Watch 2026-11-16"))

    def test_an_unknown_series_an_impossible_date_and_a_bare_key_give_nothing(self):
        for slug in ("20261117-notes", "20261341-tech-watch", "tech-watch"):
            self.assertIsNone(series.of_slug(slug), slug)


class Table(unittest.TestCase):
    def test_a_weekday_in_two_series_is_rejected(self):
        with self.assertRaises(ValueError):
            series.validated((series.Series("a-watch", "A Watch", frozenset({1, 2})),
                              series.Series("b-watch", "B Watch", frozenset({2, 3}))))

    def test_a_duplicate_key_is_rejected(self):
        with self.assertRaises(ValueError):
            series.validated((series.Series("a-watch", "A Watch", frozenset({1})),
                              series.Series("a-watch", "B Watch", frozenset({2}))))


class Cron(unittest.TestCase):
    def test_monday_to_saturday_is_a_range(self):
        with mock.patch.object(series, "SERIES", MON_TO_SAT):
            self.assertEqual(series.cron(), ("0 6 * * 1-6", "Asia/Tokyo"))

    def test_days_with_gaps_are_listed(self):
        with mock.patch.object(series, "SERIES", MON_TO_SAT[:1]):
            self.assertEqual(series.cron(), ("0 6 * * 1,3,5", "Asia/Tokyo"))


if __name__ == "__main__":
    unittest.main()
