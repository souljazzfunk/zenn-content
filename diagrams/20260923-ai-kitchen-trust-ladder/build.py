"""Build the diagrams for articles/20260923-ai-kitchen-trust-ladder.md.

Writes one SVG per diagram next to this file, then renders each to a 2x PNG in
images/20260923-ai-kitchen-trust-ladder/ (Zenn's GitHub sync does not serve SVG).

    python3 diagrams/20260923-ai-kitchen-trust-ladder/build.py
"""

import pathlib
import subprocess
import unicodedata

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent
OUT = ROOT / "images" / HERE.name
CHROMIUM = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# Colors follow zenn.dev: brand blue #3ea8ff, link blue #0f83fd, :::message yellow, alert pink.
FONT = "'Noto Sans CJK JP','Noto Sans JP','Hiragino Sans','Hiragino Kaku Gothic ProN','Yu Gothic',sans-serif"
INK = "#26323d"
MUTED = "#65717b"
LINE = "#a3b3bf"
W = 720

STYLES = {
    #        fill       stroke     title  sub
    "plain": ("#f5f9fc", "#d6e3ed", INK, MUTED),
    "green": ("#e6f4ff", "#3ea8ff", INK, "#0f83fd"),
    "amber": ("#fff6e4", "#f5a000", INK, "#a86200"),
    "red": ("#ffeff2", "#f0506e", INK, "#c9304f"),
    "dark": ("#3ea8ff", "#3ea8ff", "#ffffff", "#e6f4ff"),
    "ink": (INK, INK, "#ffffff", "#c5d0d9"),
    "solid": ("#0f83fd", "#0f83fd", "#ffffff", "#e0f1ff"),
}


def text_width(s, size):
    return sum(size if unicodedata.east_asian_width(c) in "WF" else size * 0.58 for c in s)


class Svg:
    def __init__(self, height, width=W):
        self.w, self.h = width, height
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=15, color=INK, weight=400, anchor="middle"):
        self.add(
            f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="{anchor}" dominant-baseline="central">{s}</text>'
        )

    def box(self, cx, cy, w, h, title, sub=None, style="plain", size=16, badge=None, r=12):
        fill, stroke, tc, sc = STYLES[style]
        self.add(
            f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        )
        if badge is not None:
            bx = cx - w / 2 + 22
            self.add(f'<circle cx="{bx}" cy="{cy}" r="12" fill="{tc}" opacity="0.12"/>')
            self.text(bx, cy, badge, size=13, color=tc, weight=700)
        if badge is not None:
            cx += 14
        if sub:
            self.text(cx, cy - size * 0.62, title, size=size, color=tc, weight=700)
            self.text(cx, cy + size * 0.72, sub, size=size - 3, color=sc)
        else:
            self.text(cx, cy, title, size=size, color=tc, weight=700)

    def label(self, x, y, s, color=MUTED, size=12.5):
        w = text_width(s, size) + 16
        self.add(f'<rect x="{x - w / 2}" y="{y - 11}" width="{w}" height="22" rx="11" fill="#ffffff"/>')
        self.text(x, y, s, size=size, color=color, weight=500)

    def path(self, d, color=LINE, dashed=False, head=True, width=1.8):
        dash = ' stroke-dasharray="6 5"' if dashed else ""
        marker = f' marker-end="url(#{self.marker(color)})"' if head else ""
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{dash}{marker} stroke-linecap="round" stroke-linejoin="round"/>')

    def arrow(self, x1, y1, x2, y2, **kw):
        self.path(f"M{x1},{y1} L{x2},{y2}", **kw)

    _markers = {}

    def marker(self, color):
        mid = "m" + color.lstrip("#")
        self._markers[mid] = color
        return mid

    def render(self):
        defs = "".join(
            f'<marker id="{mid}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
            for mid, c in self._markers.items()
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" '
            f'font-family="{FONT}"><defs>{defs}</defs>'
            f'<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>' + "".join(self.parts) + "</svg>\n"
        )


def chain(s, y, items, w, gap, label=None):
    """Lay out boxes left to right, centred on the canvas, joined by arrows."""
    total = len(items) * w + (len(items) - 1) * gap
    x0 = (s.w - total) / 2 + w / 2
    xs = [x0 + i * (w + gap) for i in range(len(items))]
    for i, (x, it) in enumerate(zip(xs, items)):
        s.box(x, y, w, it.get("h", 64), it["t"], it.get("s"), it.get("style", "plain"), badge=it.get("badge"))
        if i:
            s.arrow(xs[i - 1] + w / 2 + 4, y, x - w / 2 - 6, y)
    return xs


# 1. 信頼のはしご: three rising steps
def d01():
    s = Svg(300)
    steps = [
        ("毎回見張る", "1〜5体", "red", 96),
        ("ときどき確認", "10〜20体", "amber", 150),
        ("並列で任せる", "数百体", "green", 204),
    ]
    base, w, gap = 268, 196, 16
    x0 = (W - (3 * w + 2 * gap)) / 2
    for i, (t, sub, st, h) in enumerate(steps):
        fill, stroke, tc, sc = STYLES[st]
        x = x0 + i * (w + gap)
        s.add(f'<rect x="{x}" y="{base - h}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        s.text(x + w / 2, base - h + 32, t, size=17, weight=700)
        s.text(x + w / 2, base - h + 60, sub, size=24, weight=700, color=stroke)
    # rising arrow over the steps
    s.path(f"M{x0 + 40},{base - 116} C{x0 + 200},{base - 150} {x0 + 420},{base - 220} {x0 + 3 * w + 2 * gap - 30},{base - 248}", color=INK, width=2)
    s.text(52, 36, "信頼を積むほど、任せられる数が増える", size=15, weight=700, anchor="start")
    s.text(W / 2, 288, "同時に動かすエージェントの数", size=12, color=MUTED)
    return s


# 2. ミシュランの厨房
def d02():
    s = Svg(250)
    y = 78
    s.box(120, y, 170, 64, "AIが調理", style="plain")
    s.box(360, y, 190, 64, "あなたが検品", style="dark")
    s.box(600, y, 170, 64, "提供", style="green")
    s.arrow(206, y, 262, y)
    s.arrow(456, y, 512, y, color="#3ea8ff")
    s.label(484, y - 24, "合格", color="#3ea8ff")
    s.box(360, 196, 190, 60, "厨房を直す", style="red")
    s.arrow(360, y + 33, 360, 163, color="#f0506e")
    s.label(400, 132, "不合格", color="#f0506e")
    s.path("M264,196 C170,196 120,170 120,113", color=MUTED, dashed=True)
    s.label(170, 196, "次の皿から失敗が減る")
    return s


# 3. 全体像: 結論と3本の柱
def d03():
    s = Svg(400)
    s.box(W / 2, 44, 340, 56, "AIへの信頼を積み上げる", style="dark", size=18)
    cols = [
        ("1. 直す", "誤りを起こせない形にする", ["5段のはしご", "文章のlint", "レビュー役のAI", "必ず成り立つ規則"]),
        ("2. 確かめる", "AI自身に検証させる", ["CLI: 同じ手順で証拠", "地図: 言葉を実物へ"]),
        ("3. 保つ", "悪い前例を増やさない", ["前例は複製される", "迷いようがないフォルダ", "庭師を置く"]),
    ]
    cw, gap = 212, 18
    x0 = (W - (3 * cw + 2 * gap)) / 2 + cw / 2
    s.path(f"M{W / 2},72 L{W / 2},96")
    s.path(f"M{x0},96 L{x0 + 2 * (cw + gap)},96", head=False)
    for i, (t, sub, kids) in enumerate(cols):
        x = x0 + i * (cw + gap)
        s.path(f"M{x},96 L{x},118")
        s.box(x, 152, cw, 64, t, sub, style="green", size=17)
        for j, k in enumerate(kids):
            ky = 216 + j * 44
            s.add(f'<rect x="{x - cw / 2 + 10}" y="{ky - 17}" width="{cw - 20}" height="34" rx="8" fill="#f5f9fc"/>')
            s.add(f'<rect x="{x - cw / 2 + 10}" y="{ky - 17}" width="4" height="34" rx="2" fill="#3ea8ff"/>')
            s.text(x - cw / 2 + 26, ky, k, size=14, anchor="start")
    return s


# 4. 5段のはしご
def d04():
    rungs = [
        ("1", "資料そのものを直す", "#0f83fd", "#ffffff"),
        ("2", "機械で止める", "#3ea8ff", "#ffffff"),
        ("3", "いつも読む指示", "#7cc4ff", INK),
        ("4", "手順書スキル", "#b5dcff", INK),
        ("5", "人の目でチェック", "#e0f1ff", INK),
    ]
    s = Svg(366)
    top, rh, gap = 30, 52, 10
    for i, (n, t, fill, tc) in enumerate(rungs):
        y = top + i * (rh + gap)
        w = 380 + (4 - i) * 0
        x = 210
        s.add(f'<rect x="{x}" y="{y}" width="{w}" height="{rh}" rx="10" fill="{fill}"/>')
        s.add(f'<circle cx="{x + 30}" cy="{y + rh / 2}" r="15" fill="{tc}" opacity="0.18"/>')
        s.text(x + 30, y + rh / 2, n, size=15, weight=700, color=tc)
        s.text(x + 60, y + rh / 2, t, size=17, weight=700, color=tc, anchor="start")
    bottom = top + 4 * (rh + gap) + rh
    s.path(f"M160,{bottom - 10} L160,{top + 12}", color=INK, width=2.4)
    s.text(132, (top + bottom) / 2, "昇格", size=15, weight=700, color=INK)
    s.text(625, top + rh / 2, "強い", size=13, color="#3ea8ff", weight=700, anchor="start")
    s.text(625, bottom - rh / 2, "弱い", size=13, color=MUTED, weight=700, anchor="start")
    s.text(W / 2 + 40, bottom + 22, "見つけた誤りは、できるだけ上の段で直す", size=13, color=MUTED)
    return s


# 5. 文章のlint
def d05():
    s = Svg(200)
    s.box(110, 100, 150, 60, "下書き")
    s.box(340, 100, 190, 64, "自動チェック", style="dark")
    s.box(600, 52, 150, 56, "通す", style="green")
    s.box(600, 148, 150, 56, "戻す", style="red")
    s.arrow(187, 100, 240, 100)
    s.path("M437,88 C480,88 480,52 520,52", color="#3ea8ff")
    s.path("M437,112 C480,112 480,148 520,148", color="#f0506e")
    s.label(478, 50, "OK", color="#3ea8ff")
    s.label(478, 150, "NG", color="#f0506e")
    return s


# 6. レビュー役のAI
def d06():
    s = Svg(240)
    xs = chain(s, 70, [
        {"t": "下書き"},
        {"t": "レビュー役のAI", "style": "green"},
        {"t": "指摘だけ"},
        {"t": "人が判断", "style": "dark"},
    ], 146, 30)
    s.box(xs[2], 186, 250, 56, "lintやテンプレへ昇格", style="amber")
    s.path(f"M{xs[3]},103 C{xs[3]},170 {xs[3] - 20},186 {xs[2] + 131},186", color="#d98a00", dashed=True)
    s.label(xs[3] - 10, 142, "同じ指摘が続いたら", color="#a86200")
    return s


# 7. 必ず成り立つ規則
def d07():
    s = Svg(270)
    y = 70
    xs = chain(s, y, [{"t": "申請"}, {"t": "承認"}, {"t": "完了", "style": "green"}], 140, 70)
    s.path(f"M{xs[1] - 30},{y + 33} C{xs[1] - 50},{y + 95} {xs[0] + 50},{y + 95} {xs[0] + 30},{y + 37}", color="#f0506e", dashed=True)
    s.label((xs[0] + xs[1]) / 2, y + 80, "差し戻し", color="#f0506e")
    s.add(f'<rect x="{W / 2 - 220}" y="196" width="440" height="50" rx="12" fill="#ffeff2" stroke="#f0506e" stroke-width="1.5"/>')
    s.add(f'<circle cx="{W / 2 - 190}" cy="221" r="12" fill="#f0506e"/>')
    s.text(W / 2 - 190, 221, "!", size=15, weight=700, color="#ffffff")
    s.text(W / 2 + 14, 221, "差し戻しが終わらない経路を発見", size=16, weight=700, color="#c9304f")
    return s


# 8. 地図とCLI
def d08():
    s = Svg(150)
    chain(s, 75, [
        {"t": "曖昧な依頼", "s": "？？？だけのスクショ", "h": 74},
        {"t": "地図で特定", "s": "どの機能のことか", "style": "green", "h": 74},
        {"t": "CLIで確かめる", "s": "本当に起きるか", "style": "green", "h": 74},
        {"t": "証拠つきで返す", "style": "amber", "h": 74},
    ], 150, 26)
    return s


# 9. AIは近道をしたがる
def d09():
    s = Svg(230)
    s.box(120, 115, 180, 70, "AIは", "近道をしたがる", style="dark", size=17)
    s.box(360, 55, 170, 56, "自由な環境")
    s.box(360, 175, 170, 56, "窮屈な環境")
    s.box(590, 55, 210, 56, "近道が誤った道に", style="red")
    s.box(590, 175, 210, 56, "近道が正しい道に", style="green")
    s.path("M212,100 C240,100 245,55 270,55")
    s.path("M212,130 C240,130 245,175 270,175")
    s.arrow(447, 55, 480, 55, color="#f0506e")
    s.arrow(447, 175, 480, 175, color="#3ea8ff")
    return s


# 10. 前例は複製される
def d10():
    s = Svg(330)

    def doc(x, y, scale=1.0, strong=False):
        w, h = 34 * scale, 42 * scale
        fill = "#ffc85c" if strong else "#fff6e4"
        s.add(
            f'<path d="M{x - w / 2},{y - h / 2} h{w * 0.68} l{w * 0.32},{w * 0.32} v{h - w * 0.32} h{-w} z" '
            f'fill="{fill}" stroke="#f5a000" stroke-width="1.5" stroke-linejoin="round"/>'
        )
        for k in range(3):
            ly = y - h / 2 + h * (0.42 + k * 0.17)
            s.add(f'<line x1="{x - w * 0.3}" x2="{x + w * 0.3}" y1="{ly}" y2="{ly}" stroke="#d98a00" stroke-width="1.4" opacity="0.6"/>')

    cx = [110, 360, 590]
    ys1 = [150]
    ys2 = [60, 150, 240]
    ys3 = [30 + 48 * k for k in range(6)]
    for y in ys2:
        s.path(f"M{cx[0] + 34},{ys1[0]} C{cx[0] + 140},{ys1[0]} {cx[1] - 130},{y} {cx[1] - 26},{y}", color="#f5a000")
    for i, y in enumerate(ys3):
        p = ys2[i // 2]
        s.path(f"M{cx[1] + 22},{p} C{cx[1] + 110},{p} {cx[2] - 110},{y} {cx[2] - 22},{y}", color="#f5a000")
    doc(cx[0], ys1[0], 1.6, strong=True)
    for y in ys2:
        doc(cx[1], y, 1.0)
    for y in ys3:
        doc(cx[2], y, 0.8)
    s.text(cx[0], 210, "「とりあえず」1枚", size=15, weight=700)
    for x, n in zip(cx, ["1枚", "3枚", "6枚"]):
        s.text(x, 312, n, size=14, weight=700, color="#a86200")
    return s


# 11. 迷いようがないフォルダ
def d11():
    s = Svg(300)
    s.add('<rect x="30" y="20" width="460" height="260" rx="16" fill="none" stroke="#a3b3bf" stroke-width="1.5" stroke-dasharray="6 5"/>')
    s.text(48, 42, "AIが入れる範囲", size=12.5, color=MUTED, weight=700, anchor="start")
    s.box(260, 90, 220, 64, "共通情報", "読むだけ", style="plain", size=17)
    s.box(150, 220, 170, 60, "A社の案件", style="green")
    s.box(370, 220, 170, 60, "B社の案件", style="green")
    s.path("M220,123 C220,160 150,160 150,188")
    s.path("M300,123 C300,160 370,160 370,188")
    s.add('<line x1="260" y1="196" x2="260" y2="244" stroke="#f0506e" stroke-width="3" stroke-linecap="round"/>')
    s.label(260, 268, "互いに見ない", color="#f0506e")
    s.box(605, 150, 170, 84, "社外秘", "AIは入れない", style="ink", size=17)
    return s


# 12. 庭師を置く
def d12():
    s = Svg(130)
    chain(s, 65, [
        {"t": "古いのを捨てる", "style": "green", "badge": "1"},
        {"t": "型は1つだけ", "style": "green", "badge": "2"},
        {"t": "同じミスを止める", "style": "green", "badge": "3"},
    ], 200, 34)
    return s


# 13. 連絡をきっかけに動く
def d13():
    s = Svg(130)
    chain(s, 65, [
        {"t": "連絡が来る"},
        {"t": "AIが動く", "style": "dark"},
        {"t": "下書きが届く", "style": "green"},
    ], 190, 50)
    return s


# 14. まとめ
def d14():
    s = Svg(250)
    y1, y2 = 60, 190
    s.box(100, y1, 150, 60, "誤りを直す")
    s.box(310, y1, 190, 60, "どの段で直せる？", style="plain")
    s.box(590, y1, 170, 60, "環境に残す", style="green")
    s.arrow(179, y1, 211, y1)
    s.arrow(409, y1, 501, y1, color="#3ea8ff")
    s.label(455, y1 - 22, "できるだけ上", color="#3ea8ff")
    s.box(590, y2, 170, 60, "信頼が増える", style="dark")
    s.box(270, y2, 300, 60, "任せられる数が増える", style="solid", size=17)
    s.arrow(590, y1 + 34, 590, y2 - 36)
    s.arrow(503, y2, 426, y2)
    return s


# Headless Chromium reserves space for browser UI, so render tall and crop.
CROP = "import sys; from PIL import Image; p, w, h = sys.argv[1:]; Image.open(p).crop((0, 0, int(w), int(h))).save(p, optimize=True)"

DIAGRAMS = [d01, d02, d03, d04, d05, d06, d07, d08, d09, d10, d11, d12, d13, d14]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for i, fn in enumerate(DIAGRAMS, 1):
        s = fn()
        name = f"{i:02d}"
        svg = HERE / f"{name}.svg"
        svg.write_text(s.render())
        subprocess.run(
            [CHROMIUM, "--headless", "--no-sandbox", "--hide-scrollbars", "--force-device-scale-factor=2",
             f"--window-size={s.w},{s.h + 200}", f"--screenshot={OUT / (name + '.png')}", svg.as_uri()],
            check=True, capture_output=True,
        )
        png = OUT / f"{name}.png"
        subprocess.run(["python3", "-c", CROP, str(png), str(s.w * 2), str(s.h * 2)], check=True)
        print(png)


if __name__ == "__main__":
    main()
