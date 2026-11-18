#!/usr/bin/env python3
"""Sum up Tuesday 17 November 2026's world news in one image.

Writes a 1024x1024 PNG to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).
Pure Python 3 standard library: no network, no files read, no clock, no
randomness, so two runs write byte-identical output. The picture is drawn
from code with a small embedded 5x7 bitmap font, so it renders the same
in any sandbox, with no system font to depend on.

The news it sums up (events of 17 Nov 2026, as reported that day):
  1. Ukraine hits the Kerch Bridge again; a road span falls into the strait.
  2. The US strikes an Iranian missile site on Qeshm Island after Iran's
     drones target a US radar in Bahrain.
  3. Nvidia reports $115.8bn of quarterly revenue, but will not bring
     back ousted chief Jensen Huang.
  4. Bitcoin sinks to about $62,000, its lowest since mid-July, with
     about $2bn of leveraged positions liquidated.
  5. OpenAI launches GPT-6.2 Astra and Sol for professional work.
  6. Donald Trump travels in Asia ahead of talks with Xi Jinping and
     Vladimir Putin in Shenzhen.
  Plus briefs: the Gaza aid-access call, the US losing measles-free
  status, and Anthropic pricing its IPO.
"""

import os
import math
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font: each glyph is 7 rows of 5 bits, written as strings.
# Only capitals, digits and common punctuation are needed: every string
# the program draws is upper-cased and normalised before rendering.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "00000", "00000", "00000", "01100", "00000"),
    ";": ("00000", "01100", "00000", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}

_NORMALISE = {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
              "\u2013": "-", "\u2014": "-", "\u2022": "*", "\u00d7": "X"}


def normalise(text):
    out = []
    for ch in text.upper():
        out.append(_NORMALISE.get(ch, ch))
    return "".join(out)


def text_width(text, scale):
    return len(normalise(text)) * 6 * scale - scale


def wrap(text, max_px, scale):
    """Greedy word wrap of normalised text to lines fitting max_px."""
    words = normalise(text).split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_px or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

# -------------------------------------------------------------- canvas ----
PAPER = (247, 243, 232)
INK = (20, 20, 20)
NAVY = (18, 53, 91)
RED = (179, 38, 30)
TEAL = (15, 110, 110)
GOLD = (201, 162, 39)
SKY = (191, 217, 232)
SEA = (46, 107, 138)
GREY = (90, 90, 90)
LIGHT = (255, 255, 255)
GREEN = (34, 139, 34)


class Canvas:
    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.px = bytearray(PAPER * (w * h))

    def _off(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = self._off(x, y)
            self.px[o], self.px[o + 1], self.px[o + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            o = self._off(x0, yy)
            for xx in range(x0, x1):
                self.px[o], self.px[o + 1], self.px[o + 2] = c
                o += 3

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x + a, y + b, c)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill and d <= r * r:
                    self.set(xx, yy, c)
                elif not fill and abs(d - r * r) <= r * 2:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for k in range(t):
            self.circle(cx, cy, r - k, c, fill=False)

    def poly(self, pts, c):
        """Filled polygon via scanlines (pts: list of (x, y))."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(max(0, int(xs[i])), min(self.w, int(xs[i + 1]) + 1)):
                    self.set(x, y, c)

    def burst(self, cx, cy, r1, r2, c, points=12):
        """Starburst explosion shape."""
        pts = []
        for i in range(points * 2):
            r = r1 if i % 2 == 0 else r2
            a = 3.141592653589793 * i / points
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        self.poly(pts, c)

    def text(self, x, y, s, scale, c, bold=False):
        """Draw normalised text; returns width drawn."""
        s = normalise(s)
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, c)
                        if bold:
                            self.fill_rect(cx + col * scale + 1, y + row * scale,
                                           scale, scale, c)
            cx += 6 * scale
        return cx - x - scale

    def text_lines(self, x, y, lines, scale, c, leading=None, bold=False):
        lh = leading if leading is not None else 7 * scale + 3
        for line in lines:
            self.text(x, y, line, scale, c, bold=bold)
            y += lh
        return y

    def centred(self, y, s, scale, c, bold=False, cx=W // 2):
        w = text_width(s, scale)
        return self.text(cx - w // 2, y, s, scale, c, bold=bold)


def write_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        return out + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# -------------------------------------------------------------- layout ----
M = 24  # outer margin


def card(c, x, y, w, h, fill=LIGHT):
    c.fill_rect(x, y, w, h, fill)
    c.rect(x, y, w, h, NAVY, 2)


def kicker_head_sub(c, x, y, w, kick, head, sub, head_scale=2, sub_scale=2,
                   bottom=None):
    """Kicker + wrapped headline + wrapped sub inside a card. Returns y."""
    c.text(x, y, kick, 2, RED, bold=True)
    y += 22
    lines = wrap(head, w, head_scale)
    y = c.text_lines(x, y, lines, head_scale, INK,
                     leading=7 * head_scale + 4, bold=True)
    y += 4
    lines = wrap(sub, w, sub_scale)
    y = c.text_lines(x, y, lines, sub_scale, INK,
                     leading=7 * sub_scale + 3)
    if bottom is not None:
        assert y <= bottom, f"text overflows card: ends y={y}, bottom={bottom}"
    return y


def draw_masthead(c):
    c.fill_rect(0, 0, W, 10, RED)
    c.centred(22, "THE DAY'S WORLD NEWS - IN ONE IMAGE", 2, GREY, bold=True)
    c.centred(52, "TUESDAY 17 NOVEMBER 2026", 4, NAVY, bold=True)
    c.centred(96, "SIX STORIES THAT DEFINED THE DAY - FROM THE KERCH STRAIT TO WALL STREET",
              2, INK)
    c.fill_rect(M, 128, W - 2 * M, 3, INK)


def draw_hero(c):
    x, y, w, h = M, 140, W - 2 * M, 330
    card(c, x, y, w, h)
    dx, dy, dw, dh = x + 3, y + 3, 593, h - 6
    # sky, sea, bridge
    c.fill_rect(dx, dy, dw, 150, SKY)
    c.fill_rect(dx, dy + 150, dw, dh - 150, SEA)
    c.circle(dx + 520, dy + 42, 26, GOLD)
    c.circle(dx + 90, dy + 40, 18, LIGHT)
    c.circle(dx + 120, dy + 34, 22, LIGHT)
    c.circle(dx + 430, dy + 70, 14, LIGHT)
    # waves
    for wy in (dy + 190, dy + 230, dy + 270):
        for wx in range(dx + 10, dx + dw - 10, 46):
            c.line(wx, wy, wx + 22, wy, (140, 190, 210), 2)
    # towers and cables
    for tx in (dx + 130, dx + 430):
        c.fill_rect(tx, dy + 60, 14, 90, (70, 70, 70))
        c.line(tx + 7, dy + 60, tx - 60, dy + 148, (70, 70, 70), 1)
        c.line(tx + 7, dy + 60, tx + 74, dy + 148, (70, 70, 70), 1)
    # deck, left and right of the break
    c.fill_rect(dx, dy + 148, 278, 10, (70, 70, 70))
    c.fill_rect(dx + 393, dy + 148, 200, 10, (70, 70, 70))
    # the break itself: deck missing in the middle, explosion and splash
    # below it (no fallen span drawn: the gap is the story)
    c.burst(dx + 336, dy + 138, 34, 16, (255, 140, 40))
    c.burst(dx + 336, dy + 138, 20, 9, (255, 220, 80))
    c.circle(dx + 318, dy + 104, 16, (120, 120, 120))
    c.circle(dx + 348, dy + 92, 20, (140, 140, 140))
    c.circle(dx + 336, dy + 200, 12, LIGHT)
    c.circle(dx + 362, dy + 206, 9, LIGHT)
    # drone above the bridge
    c.line(dx + 500, dy + 96, dx + 524, dy + 108, INK, 2)
    c.line(dx + 524, dy + 96, dx + 500, dy + 108, INK, 2)
    c.circle(dx + 512, dy + 102, 3, INK)
    # text, right of the drawing
    tx = dx + dw + 20
    tw = x + w - 3 - tx
    c.text(tx, y + 20, "UKRAINE - WAR IN EUROPE", 2, RED, bold=True)
    y2 = c.text_lines(tx, y + 50, wrap("KERCH BRIDGE HIT AGAIN", tw, 3),
                      3, INK, leading=25, bold=True)
    c.text_lines(tx, y2 + 8,
                 wrap("A ROAD SPAN FALLS INTO THE KERCH STRAIT AFTER A "
                      "SECOND DAY OF UKRAINIAN STRIKES. KYIV CALLS THE "
                      "ATTACK 'UNPRECEDENTED'. RUSSIA ANSWERS BY HITTING "
                      "BRIDGES IN KYIV.", tw, 2),
                 2, INK, leading=17)
    c.text(tx, y + h - 58, "TRAFFIC HALTED", 2, RED, bold=True)
    c.text(tx, y + h - 34, "SOME TRAINS RESUME", 2, RED, bold=True)


def draw_card_a(c):  # US - Iran
    x, y, w, h = M, 482, 312, 260
    card(c, x, y, w, h)
    ix, iy, iw, ih = x + 2, y + 2, w - 4, 104
    c.fill_rect(ix, iy, iw, ih, (16, 32, 56))
    c.circle(ix + 250, iy + 26, 14, (220, 220, 200))  # moon
    c.burst(ix + 110, iy + 52, 40, 18, (255, 140, 40))
    c.burst(ix + 110, iy + 52, 22, 10, (255, 220, 80))
    c.poly([(ix + 20, iy + ih), (ix + 70, iy + 78), (ix + 150, iy + 88),
            (ix + 210, iy + 76), (ix + 290, iy + ih)], (30, 90, 60))  # island
    c.line(ix + 210, iy + 30, ix + 250, iy + 70, LIGHT, 2)  # missile streak
    c.circle(ix + 250, iy + 70, 4, LIGHT)
    c.text(ix + 14, iy + 12, "QESHM ISLAND", 2, LIGHT, bold=True)
    kicker_head_sub(c, x + 14, y + 120, w - 28,
                    "MIDDLE EAST",
                    "US STRIKES IRAN SITE",
                    "US JETS STRIKE QESHM ISLAND AFTER IRANIAN DRONES "
                    "HIT A US RADAR IN BAHRAIN - THE THIRD TIME IN "
                    "FIVE DAYS.", bottom=y + h - 6)


def draw_card_b(c):  # Nvidia
    x, y, w, h = 356, 482, 312, 260
    card(c, x, y, w, h)
    ix, iy, iw, ih = x + 2, y + 2, w - 4, 104
    c.fill_rect(ix, iy, iw, ih, (12, 60, 30))
    # rising chart, drawn first so the chip sits on top of it
    c.line(ix + 14, iy + 88, ix + 70, iy + 62, LIGHT, 3)
    c.line(ix + 70, iy + 62, ix + 120, iy + 70, LIGHT, 3)
    c.line(ix + 120, iy + 70, ix + 200, iy + 30, LIGHT, 3)
    c.line(ix + 200, iy + 30, ix + 210, iy + 44, LIGHT, 3)
    c.line(ix + 200, iy + 30, ix + 214, iy + 30, LIGHT, 3)
    # chip
    c.fill_rect(ix + 118, iy + 26, 72, 52, (30, 140, 70))
    c.rect(ix + 118, iy + 26, 72, 52, GOLD, 3)
    for px in range(ix + 126, ix + 186, 14):
        c.fill_rect(px, iy + 18, 5, 8, GOLD)
        c.fill_rect(px, iy + 78, 5, 8, GOLD)
    c.text(ix + 138, iy + 44, "AI", 3, LIGHT, bold=True)
    kicker_head_sub(c, x + 14, y + 120, w - 28,
                    "TECH - CHIPS",
                    "NVIDIA'S $115.8BN QUARTER",
                    "REVENUE DOUBLES IN A YEAR, BUT NVIDIA WILL NOT BRING "
                    "BACK OUSTED CHIEF JENSEN HUANG.", bottom=y + h - 6)


def draw_card_c(c):  # Bitcoin
    x, y, w, h = 688, 482, 312, 260
    card(c, x, y, w, h)
    ix, iy, iw, ih = x + 2, y + 2, w - 4, 104
    c.fill_rect(ix, iy, iw, ih, (90, 20, 20))
    c.circle(ix + 70, iy + 52, 36, GOLD)
    c.ring(ix + 70, iy + 52, 36, (160, 120, 20), 2)
    c.text(ix + 58, iy + 38, "B", 4, (120, 70, 0), bold=True)
    # falling chart
    c.line(ix + 130, iy + 24, ix + 180, iy + 44, LIGHT, 3)
    c.line(ix + 180, iy + 44, ix + 230, iy + 40, LIGHT, 3)
    c.line(ix + 230, iy + 40, ix + 285, iy + 82, LIGHT, 3)
    c.line(ix + 285, iy + 82, ix + 271, iy + 82, LIGHT, 3)
    c.line(ix + 285, iy + 82, ix + 285, iy + 68, LIGHT, 3)
    kicker_head_sub(c, x + 14, y + 120, w - 28,
                    "MARKETS - CRYPTO",
                    "BITCOIN SINKS TO $62,000",
                    "LOWEST SINCE MID-JULY. ABOUT $2BN OF LEVERAGED BETS "
                    "ARE WIPED OUT AS FEAR GRIPS THE MARKET.", bottom=y + h - 6)


def draw_row3(c):
    specs = [
        (M, "AI - OPENAI", "OPENAI LAUNCHES GPT-6.2",
         "ASTRA AND SOL ARRIVE FOR PROFESSIONAL WORK, ABOUT 20% CHEAPER.",
         TEAL, "ring"),
        (356, "DIPLOMACY - ASIA", "TRUMP HEADS TO SHENZHEN",
         "IN MANILA FOR ASEAN, DUE THURSDAY FOR TALKS WITH XI AND PUTIN.",
         NAVY, "globe"),
        (688, "MIDDLE EAST - GAZA", "GAZA AID ACCESS URGED",
         "UK, AUSTRALIA, CANADA AND ITALY URGE ISRAEL TO OPEN CROSSINGS.",
         (40, 90, 140), "truck"),
    ]
    for x, kick, head, sub, bg, icon in specs:
        y, w, h = 754, 312, 180
        card(c, x, y, w, h)
        ix, iy, iw, ih = x + 2, y + 2, w - 4, 56
        c.fill_rect(ix, iy, iw, ih, bg)
        if icon == "ring":
            c.ring(ix + iw // 2, iy + 28, 18, LIGHT, 3)
            c.burst(ix + iw // 2, iy + 28, 12, 5, LIGHT)
        elif icon == "globe":
            c.circle(ix + iw // 2, iy + 28, 20, (90, 160, 220))
            c.line(ix + iw // 2 - 20, iy + 28, ix + iw // 2 + 20, iy + 28,
                   (90, 160, 220), 2)
            c.poly([(ix + iw // 2 - 8, iy + 14), (ix + iw // 2 + 10, iy + 20),
                    (ix + iw // 2 + 2, iy + 38), (ix + iw // 2 - 12, iy + 30)],
                   (60, 160, 90))
            c.line(ix + iw // 2 + 30, iy + 18, ix + iw // 2 + 62, iy + 34, LIGHT, 2)
            c.poly([(ix + iw // 2 + 62, iy + 34), (ix + iw // 2 + 48, iy + 30),
                    (ix + iw // 2 + 48, iy + 40)], LIGHT)
        else:  # aid truck
            c.fill_rect(ix + 60, iy + 14, 150, 26, LIGHT)
            c.fill_rect(ix + 210, iy + 22, 44, 18, LIGHT)
            c.fill_rect(ix + 118, iy + 20, 6, 14, RED)
            c.fill_rect(ix + 113, iy + 25, 16, 5, RED)
            c.circle(ix + 96, iy + 44, 7, INK)
            c.circle(ix + 228, iy + 44, 7, INK)
            c.line(ix + 20, iy + 50, ix + 290, iy + 50, LIGHT, 2)
        kicker_head_sub(c, x + 14, y + 72, w - 28, kick, head, sub,
                        bottom=y + h - 6)


def draw_footer(c):
    x, y, w, h = M, 946, W - 2 * M, 64
    c.fill_rect(x, y, w, h, NAVY)
    c.text(x + 16, y + 10,
           "ALSO: ANTHROPIC PRICES ITS IPO, LISTING AS ANT ON 19 NOV",
           2, LIGHT, bold=True)
    c.text(x + 16, y + 34,
           "US LOSES MEASLES-FREE STATUS AFTER 26 YEARS - NEPAL FIRST FOR UN LOSS FUNDS",
           2, LIGHT)
    c.centred(1014, "EVENTS OF 17 NOVEMBER 2026 AS REPORTED THAT DAY", 1, GREY)


def build():
    c = Canvas()
    draw_masthead(c)
    draw_hero(c)
    draw_card_a(c)
    draw_card_b(c)
    draw_card_c(c)
    draw_row3(c)
    draw_footer(c)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(build(), path)
    print(f"wrote {path} ({size} bytes)")


if __name__ == "__main__":
    main()
