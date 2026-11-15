#!/usr/bin/env python3
"""series.py — 定期ジョブが書くシリーズの表と、1 回の実行（シリーズ × 日付）から決まる名前。

使い方:
    python3 scripts/series.py today    # 今日（JST）の実行。最後の行に JSON 1 行
    python3 scripts/series.py cron     # 定期ジョブの予定。「cron 式<TAB>タイムゾーン」の 1 行

- today: その曜日を持つシリーズがあれば {"run": true, "series", "head", "slug", "crawl_prompt", "seen", "extra"}、
  無ければ {"run": false, "say": "..."}。どちらも exit 0
- slug、タイトルの先頭、巡回手順・既読リスト・手動追加リストのパスは Run だけが決める。
  他のスクリプトは today() か of_slug() で Run を受け取り、SERIES を直接は見ない
- 環境変数 WATCH_TODAY=YYYY-MM-DD は today の日付を差し替える（テスト用）

標準ライブラリのみ。ネットワークに出ない。
"""
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9))
TZ = "Asia/Tokyo"
RUN_AT = (6, 0)  # 時, 分
WORKSPACE = Path.home() / ".openclaw/workspace"
KEY_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SLUG_RE = re.compile(r"^(\d{8})-(.+)$")


@dataclass(frozen=True)
class Series:
    key: str  # slug の末尾、ops-record の trigger、巡回手順・既読リスト・手動追加リストのファイル名の幹
    title: str  # タイトルと報告の先頭
    weekdays: frozenset  # isoweekday。1 = 月曜、7 = 日曜


def validated(table):
    """表をそのまま返す。key と title の重複、1 つの曜日を 2 シリーズが持つ表は ValueError。"""
    owner = {}
    for s in table:
        if not KEY_RE.match(s.key):
            raise ValueError(f"key {s.key!r} は英小文字・数字・ハイフンだけにする")
        if not s.weekdays <= set(range(1, 8)):
            raise ValueError(f"{s.key}: weekdays は 1〜7")
        for d in s.weekdays:
            if d in owner:
                raise ValueError(f"曜日 {d} を {owner[d]} と {s.key} の両方が持っている")
            owner[d] = s.key
    for field in ("key", "title"):
        values = [getattr(s, field) for s in table]
        if len(set(values)) != len(values):
            raise ValueError(f"{field} が重複している: {values}")
    return tuple(table)


SERIES = validated((
    Series("tech-watch", "Tech Watch", frozenset({1, 3, 5})),
    Series("learning-watch", "Learning Watch", frozenset({2, 4, 6})),
))


@dataclass(frozen=True)
class Run:
    """あるシリーズのある日の実行。"""
    series: Series
    day: date

    @property
    def slug(self):
        return f"{self.day:%Y%m%d}-{self.series.key}"

    @property
    def head(self):
        return f"{self.series.title} {self.day.isoformat()}"

    @property
    def crawl_prompt(self):
        return WORKSPACE / "watch" / f"{self.series.key}.crawl.md"

    @property
    def seen(self):
        return WORKSPACE / "state" / f"{self.series.key}-seen.json"

    @property
    def extra(self):
        return WORKSPACE / "state" / f"{self.series.key}-extra.json"


def for_day(day):
    """その曜日を持つシリーズの Run。どのシリーズも持たない曜日は None。"""
    s = next((s for s in SERIES if day.isoweekday() in s.weekdays), None)
    return Run(s, day) if s else None


def today_date(now=None):
    if os.environ.get("WATCH_TODAY"):
        return date.fromisoformat(os.environ["WATCH_TODAY"])
    return (now or datetime.now(JST)).astimezone(JST).date()


def today(now=None):
    return for_day(today_date(now))


def of_slug(slug):
    """slug（YYYYMMDD-<key>）の Run。知らないシリーズ、ありえない日付は None。"""
    m = SLUG_RE.match(slug)
    s = next((s for s in SERIES if m and s.key == m.group(2)), None)
    if not s:
        return None
    try:
        return Run(s, datetime.strptime(m.group(1), "%Y%m%d").date())
    except ValueError:
        return None


def cron():
    """(cron 式, タイムゾーン)。曜日の欄は全曜日なら *、連続なら a-b、それ以外は列挙。"""
    days = sorted(set().union(*(s.weekdays for s in SERIES)))
    if len(days) == 7:
        field = "*"
    elif len(days) > 1 and days[-1] - days[0] == len(days) - 1:
        field = f"{days[0]}-{days[-1]}"
    else:
        field = ",".join(map(str, days))
    hour, minute = RUN_AT
    return f"{minute} {hour} * * {field}", TZ


def keys():
    return tuple(s.key for s in SERIES)


def main(argv=None):
    cmd = (sys.argv[1:] if argv is None else argv)[:1]
    if cmd == ["cron"]:
        print("\t".join(cron()))
        return 0
    if cmd == ["today"]:
        day = today_date()
        run = for_day(day)
        if run is None:
            out = {"run": False, "say": f"watch {day.isoformat()}（{'月火水木金土日'[day.isoweekday() - 1]}）: 今日は休み"}
        else:
            out = {"run": True, "series": run.series.key, "head": run.head, "slug": run.slug,
                   "crawl_prompt": str(run.crawl_prompt), "seen": str(run.seen), "extra": str(run.extra)}
        print(json.dumps(out, ensure_ascii=False))
        return 0
    print("usage: series.py today|cron", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
