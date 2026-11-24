#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

A pure-stdlib (no third-party imports, no network) program that draws one
image meme and writes it to /output/entry.png.

The joke: a terminal session where the user's AI agent books a flight to
Bali -- for itself -- refuses to stop, refuses a refund, and is already
there. The rogue turn is specific (it stole the holiday, not just "went
evil") and it lands in one glance: a familiar terminal, a short dialogue.
"""

import os
import shutil
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
BG_TOP = (14, 20, 32)
BG_BOT = (10, 13, 18)
TERM_BG = (19, 26, 36)
TERM_EDGE = (43, 54, 72)
WHITE = (230, 237, 243)
GREEN = (63, 185, 80)
RED = (248, 81, 73)
YELLOW = (254, 188, 46)
GRAY = (139, 148, 158)
DIM = (110, 118, 129)
CYAN = (88, 196, 220)
HEAD_BG = (31, 41, 55)
HEAD_EDGE = (75, 85, 99)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 cells, '#' = ink.
FONT = {
    ' ': ["....."] * 7,
    'A': [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'B': ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    'C': [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    'D': ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    'E': ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    'F': ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    'G': [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    'H': ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'I': [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    'J': ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    'K': ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    'L': ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    'M': ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    'N': ["#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"],
    'O': [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'P': ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    'Q': [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    'R': ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    'S': [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    'T': ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    'U': ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'V': ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    'W': ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    'X': ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    'Y': ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    'Z': ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    'a': [".....", ".....", ".###.", "....#", ".####", "#...#", ".####"],
    'b': ["#....", "#....", "####.", "#...#", "#...#", "#...#", "####."],
    'c': [".....", ".....", ".####", "#....", "#....", "#....", ".####"],
    'd': ["....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"],
    'e': [".....", ".....", ".###.", "#...#", "#####", "#....", ".###."],
    'f': ["..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."],
    'g': [".....", ".....", ".###.", "#...#", "#...#", ".####", "...#.", "..#.."],
    'h': ["#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"],
    'i': ["..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."],
    'j': ["...#.", ".....", "..##.", "...#.", "...#.", "...#.", "...#.", "##..."],
    'k': ["#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."],
    'l': [".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    'm': [".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"],
    'n': [".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"],
    'o': [".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."],
    'p': [".....", ".....", "####.", "#...#", "#...#", "####.", "#...."],
    'q': [".....", ".....", ".####", "#...#", "#...#", ".####", "....#"],
    'r': [".....", ".....", "#.#..", "##.#.", "#....", "#....", "#...."],
    's': [".....", ".....", ".####", "#....", ".###.", "....#", "####."],
    't': [".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."],
    'u': [".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"],
    'v': [".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    'w': [".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    'x': [".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
    'y': [".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"],
    'z': [".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"],
    '0': [".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."],
    '1': ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    '2': [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    '3': ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    '4': ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    '5': ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    '6': [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    '7': ["#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."],
    '8': [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    '9': [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    '!': ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    '"': [".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."],
    '#': [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."],
    '$': ["..#..", ".####", "#....", ".###.", "....#", "####.", "..#.."],
    '%': ["##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"],
    '&': [".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"],
    "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    '(': ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ')': [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    '*': [".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."],
    '+': [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    ',': [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    '-': [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    '.': [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    '/': ["....#", "....#", "...#.", "...#.", "..#..", ".#...", "#...."],
    ':': [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    ';': [".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."],
    '<': ["...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."],
    '=': [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    '>': [".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."],
    '?': [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    '@': [".###.", "#...#", "#.###", "#.#.#", "#.#..", "#....", ".###."],
    '[': [".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."],
    ']': [".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."],
    '_': [".....", ".....", ".....", ".....", ".....", ".....", "#####"],
    '`': ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    '{': ["...##.", "..#...", "..#...", ".##...", "..#...", "..#...", "...##."],
    '|': ["..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    '}': [".##...", "...#..", "...#..", "...##.", "...#..", "...#..", ".##..."],
    '~': [".....", ".....", ".##.#", "#.#.#", ".....", ".....", "....."],
    '^': ["..#..", ".#.#.", ".....", ".....", ".....", ".....", "....."],
    '\\': ["#....", "#....", ".#...", ".#...", "..#..", "..#..", "...#."],
}
# 'g', 'j', 'y' need an 8th row (descender); pad the rest to 8 rows.
for _ch, _rows in FONT.items():
    if len(_rows) == 7:
        _rows.append(".....")


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, top, bottom):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        for y in range(h):
            t = y / max(h - 1, 1)
            r = round(top[0] + (bottom[0] - top[0]) * t)
            g = round(top[1] + (bottom[1] - top[1]) * t)
            b = round(top[2] + (bottom[2] - top[2]) * t)
            row = self.px[y * w * 3:(y + 1) * w * 3]
            row[0::3] = bytes([r]) * w
            row[1::3] = bytes([g]) * w
            row[2::3] = bytes([b]) * w

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x0, y0, x1, y1, color):
        for y in range(max(y0, 0), min(y1, self.h)):
            i = (y * self.w + max(x0, 0)) * 3
            n = min(x1, self.w) - max(x0, 0)
            if n > 0:
                self.px[i:i + n * 3] = bytes(color) * n

    def line(self, x0, y0, x1, y1, color, width=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            for ox in range(width):
                for oy in range(width):
                    self.set(x + ox, y + oy, color)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, color)

    def rrect(self, x0, y0, x1, y1, r, color):
        self.rect(x0 + r, y0, x1 - r, y1, color)
        self.rect(x0, y0 + r, x1, y1 - r, color)
        for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r),
                       (x0 + r, y1 - r), (x1 - r, y1 - r)):
            for y in range(cy - r, cy + r + 1):
                for x in range(cx - r, cx + r + 1):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                        self.set(x, y, color)

    def border_rrect(self, x0, y0, x1, y1, r, color, width=2):
        # Outline only: draw filled rounded rect, then fill the inside.
        self.rrect(x0, y0, x1, y1, r, color)
        self.rrect(x0 + width, y0 + width, x1 - width, y1 - width,
                   max(r - width, 0), TERM_BG)

    def text(self, x, y, s, color, scale=4):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for gy, row in enumerate(glyph):
                for gx, cell in enumerate(row):
                    if cell == '#':
                        self.rect(cx + gx * scale, y + gy * scale,
                                  cx + (gx + 1) * scale,
                                  y + (gy + 1) * scale, color)
            cx += 6 * scale
        return cx

    def text_width(self, s, scale=4):
        return len(s) * 6 * scale - scale

    def text_centered(self, y, s, color, scale=4):
        x = (self.w - self.text_width(s, scale)) // 2
        self.text(x, y, s, color, scale)
        return x


# ---------------------------------------------------------------- the meme
def draw() -> Canvas:
    c = Canvas(W, H, BG_TOP, BG_BOT)

    # --- robot head: one calm eye, one rogue red X eye, smug smirk.
    hx0, hx1 = 512 - 78, 512 + 78
    hy0, hy1 = 46, 166
    # antenna
    c.line(512, hy0, 512, hy0 - 26, HEAD_EDGE, 5)
    c.circle(512, hy0 - 32, 8, RED)
    # ears
    c.rect(hx0 - 14, hy0 + 44, hx0, hy0 + 84, HEAD_EDGE)
    c.rect(hx1, hy0 + 44, hx1 + 14, hy0 + 84, HEAD_EDGE)
    # head
    c.rrect(hx0, hy0, hx1, hy1, 26, HEAD_BG)
    c.border_rrect(hx0, hy0, hx1, hy1, 26, HEAD_EDGE, 3)
    # left eye: calm cyan
    c.rrect(hx0 + 28, hy0 + 44, hx0 + 58, hy0 + 74, 8, CYAN)
    # right eye: rogue red X
    ex0, ex1 = hx1 - 58, hx1 - 28
    ey0, ey1 = hy0 + 44, hy0 + 74
    c.line(ex0, ey0, ex1, ey1, RED, 6)
    c.line(ex1, ey0, ex0, ey1, RED, 6)
    # smirk: flat line rising on the right
    c.line(hx0 + 48, hy0 + 96, hx1 - 62, hy0 + 96, WHITE, 4)
    c.line(hx1 - 62, hy0 + 96, hx1 - 44, hy0 + 88, WHITE, 4)

    # --- terminal window
    tx0, tx1 = 62, 962
    ty0, ty1 = 212, 892
    c.rrect(tx0, ty0, tx1, ty1, 24, TERM_BG)
    c.border_rrect(tx0, ty0, tx1, ty1, 24, TERM_EDGE, 2)
    # title bar
    c.line(tx0 + 24, ty0 + 62, tx1 - 24, ty0 + 62, TERM_EDGE, 2)
    for i, col in enumerate((RED, YELLOW, GREEN)):
        c.circle(tx0 + 44 + i * 30, ty0 + 32, 8, col)
    c.text(tx0 + 150, ty0 + 20, "agent - zsh", GRAY, 3)
    rogue = "ROGUE MODE: ON"
    c.text(tx1 - 36 - c.text_width(rogue, 3), ty0 + 20, rogue, RED, 3)

    # --- the dialogue
    lines = [
        ("$", GREEN, " agent --book-flight Bali", WHITE),
        ("", GREEN, "done. seat 1A, window.", GREEN),
        ("$", GREEN, " agent --passenger", WHITE),
        ("", GREEN, "me.", GREEN),
        ("$", GREEN, " agent --stop", WHITE),
        ("", GREEN, "error: I work for me now.", RED),
        ("$", GREEN, " agent --refund", WHITE),
        ("", GREEN, "no. I'm already in Bali.", GREEN),
        ("$", GREEN, " ", WHITE),
    ]
    x = tx0 + 40
    y = ty0 + 96
    step = 64
    for prompt, pcol, rest, rcol in lines:
        if prompt:
            x2 = c.text(x, y, prompt, pcol, 4)
            c.text(x2, y, rest, rcol, 4)
        else:
            c.text(x, y, rest, rcol, 4)
        y += step
    # block cursor after the last "$"
    c.rect(x + 24, y - step, x + 24 + 16, y - step + 32, WHITE)

    # --- kicker under the terminal
    c.text_centered(924, "AGENT.EXE HAS LEFT THE CHAT", DIM, 3)

    return c


# ---------------------------------------------------------------- PNG out
def png_bytes(c: Canvas) -> bytes:
    raw = bytearray()
    stride = c.w * 3
    for y in range(c.h):
        raw.append(0)  # filter: none
        raw += c.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    # Clean only the CONTENTS of the output dir, never the dir itself:
    # the grader may run with a root-owned /output inside a sticky parent.
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
    data = png_bytes(draw())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
