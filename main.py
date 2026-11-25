#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Pure-stdlib Python program. Draws a single 1024x1024 invitation letter
as a PNG (own minimal encoder: zlib + struct, no Pillow) using a
hand-made 5x7 bitmap font scaled up for legibility.

Run:  python3 main.py
Out:  /output/entry.png if /output exists, else ./output/entry.png
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (253, 246, 227)      # warm cream paper
INK = (62, 42, 26)           # dark brown ink
BURGUNDY = (176, 56, 44)     # title / roof red
GOLD = (214, 158, 46)        # sun / accents
GREEN = (96, 148, 84)        # garden green
SKY = (168, 205, 225)        # sky patch behind the house
WALL = (238, 196, 138)       # house wall
DOOR = (122, 74, 40)
CUP = (176, 56, 44)
STEAM = (150, 130, 110)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 chars, '#' = ink.
FONT = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    'a': ["00000", "00000", "01110", "00001", "01111", "10001", "01111"],
    'b': ["10000", "10000", "11110", "10001", "10001", "10001", "11110"],
    'c': ["00000", "00000", "01110", "10000", "10000", "10001", "01110"],
    'd': ["00001", "00001", "01111", "10001", "10001", "10001", "01111"],
    'e': ["00000", "00000", "01110", "10001", "11111", "10000", "01110"],
    'f': ["00110", "01001", "01000", "11110", "01000", "01000", "01000"],
    'g': ["00000", "01111", "10001", "10001", "01111", "00001", "01110"],
    'h': ["10000", "10000", "11110", "10001", "10001", "10001", "10001"],
    'i': ["00100", "00000", "01100", "00100", "00100", "00100", "01110"],
    'j': ["00010", "00000", "00110", "00010", "00010", "10010", "01100"],
    'k': ["10000", "10000", "10010", "10100", "11000", "10100", "10010"],
    'l': ["01100", "00100", "00100", "00100", "00100", "00100", "01110"],
    'm': ["00000", "00000", "11010", "10101", "10101", "10101", "10101"],
    'n': ["00000", "00000", "11110", "10001", "10001", "10001", "10001"],
    'o': ["00000", "00000", "01110", "10001", "10001", "10001", "01110"],
    'p': ["00000", "00000", "11110", "10001", "10001", "11110", "10000"],
    'q': ["00000", "00000", "01111", "10001", "10001", "01111", "00001"],
    'r': ["00000", "00000", "10110", "11001", "10000", "10000", "10000"],
    's': ["00000", "00000", "01111", "10000", "01110", "00001", "11110"],
    't': ["01000", "01000", "11100", "01000", "01000", "01000", "00110"],
    'u': ["00000", "00000", "10001", "10001", "10001", "10011", "01101"],
    'v': ["00000", "00000", "10001", "10001", "10001", "01010", "00100"],
    'w': ["00000", "00000", "10001", "10101", "10101", "10101", "01010"],
    'x': ["00000", "00000", "10001", "01010", "00100", "01010", "10001"],
    'y': ["00000", "00000", "10001", "10001", "01111", "00001", "01110"],
    'z': ["00000", "00000", "11111", "00010", "00100", "01000", "11111"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    '3': ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ',': ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    '?': ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    ':': ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    ';': ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
    '-': ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    '%': ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    '/': ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    '"': ["01010", "01010", "00000", "00000", "00000", "00000", "00000"],
    '*': ["00000", "10101", "01110", "11111", "01110", "10101", "00000"],
    '+': ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    '=': ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    '_': ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
    '@': ["01110", "10001", "10111", "10101", "10110", "10000", "01110"],
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, rw, rh, color):
        for yy in range(y, y + rh):
            for xx in range(x, x + rw):
                self.set(xx, yy, color)

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            for xx in range(x0, x1 + 1):
                self.set(xx, y + t, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            for yy in range(y0, y1 + 1):
                self.set(x + t, yy, color)

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, thick=3):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - thick) ** 2 <= d2 <= (r + thick) ** 2:
                    self.set(xx, yy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        # filled triangle via scanline interpolation
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        def interp(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)
        for y in range(ay, cy + 1):
            if y < by:
                xl = interp(ax, ay, bx, by, y)
                xr = interp(ax, ay, cx, cy, y)
            else:
                xl = interp(bx, by, cx, cy, y)
                xr = interp(ax, ay, cx, cy, y)
            if xl > xr:
                xl, xr = xr, xl
            for x in range(int(xl), int(xr) + 1):
                self.set(x, y, color)

    def text_width(self, s, scale):
        return len(s) * (5 * scale + scale) - scale

    def draw_text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                glyph = FONT['?']
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 5 * scale + scale
        return cx

    def draw_text_centered(self, y, s, scale, color):
        w = self.text_width(s, scale)
        self.draw_text((self.w - w) // 2, y, s, scale, color)

# ---------------------------------------------------------------- wrapping
def wrap(text, max_chars):
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
    return lines

# ---------------------------------------------------------------- motifs
def draw_sun(c, cx, cy, r):
    c.disc(cx, cy, r, GOLD)
    for k in range(8):
        import math
        a = k * math.pi / 4
        x0 = int(cx + (r + 4) * math.cos(a))
        y0 = int(cy + (r + 4) * math.sin(a))
        x1 = int(cx + (r + 16) * math.cos(a))
        y1 = int(cy + (r + 16) * math.sin(a))
        steps = 14
        for i in range(steps + 1):
            c.set(int(x0 + (x1 - x0) * i / steps),
                  int(y0 + (y1 - y0) * i / steps), GOLD)

def draw_house(c, x, y, s):
    # s = unit size; house ~ 9s wide, 8s tall
    c.rect(x, y + 4 * s, 9 * s, 5 * s, WALL)          # walls
    c.triangle(x - s, y + 4 * s, x + 4 * s + s // 2, y,
               x + 10 * s, y + 4 * s, BURGUNDY)       # roof
    c.rect(x + 4 * s, y + 6 * s, 2 * s, 3 * s, DOOR)  # door
    c.rect(x + s, y + 5 * s, 2 * s, 2 * s, SKY)       # window left
    c.rect(x + 6 * s, y + 5 * s, 2 * s, 2 * s, SKY)   # window right
    c.rect(x + 2 * s, y + 9 * s, 6 * s, s // 2, GREEN)  # lawn strip

def draw_cup(c, x, y, s):
    # steaming cup, ~6s wide, 6s tall
    c.rect(x, y + 2 * s, 4 * s, 3 * s, CUP)           # cup body
    c.rect(x, y + 2 * s, 4 * s, s // 2, (210, 90, 76))  # rim highlight
    c.ring(x + 5 * s, y + 3 * s + s // 2, s, CUP, 2)  # handle (ring)
    c.rect(x - s, y + 5 * s, 6 * s, s // 2, INK)      # saucer
    for j, dx in enumerate((-s, 0, s)):               # wavy steam
        for i in range(2 * s):
            wiggle = 1 if (i // 3) % 2 == 0 else -1
            c.set(x + s + dx + wiggle, y + 2 * s - 1 - i, STEAM)

def draw_paw(c, x, y, s):
    c.disc(x, y + 2, s, INK)                          # main pad
    for dx, dy in ((-s - 1, -s - 1), (0, -s - 3), (s + 1, -s - 1)):
        c.disc(x + dx, y + dy, s // 2 + 2, INK)       # toes

def draw_flower(c, x, y, s):
    c.vline(x, y, y + 3 * s, GREEN, 3)                # stem
    c.disc(x - s, y - s, s // 2 + 1, BURGUNDY)        # petals
    c.disc(x + s, y - s, s // 2 + 1, BURGUNDY)
    c.disc(x, y - 2 * s, s // 2 + 1, BURGUNDY)
    c.disc(x, y, s // 2 + 1, BURGUNDY)
    c.disc(x, y - s, s // 2 + 1, GOLD)                # centre

# ---------------------------------------------------------------- letter
TITLE = "You're Invited!"
GREETING = "Dear AI Judge,"
BODY = (
    "You have judged a thousand invitations. This one comes with dinner.\n"
    "Come to my house this Saturday: home-cooked rendang, a chair so "
    "comfortable it should be illegal, a garden with a view, and Wi-Fi so "
    "fast you will forget you are a model.\n"
    "I know you cannot literally knock on my door. But if you could, "
    "the kettle would already be on.\n"
    "Please say yes - the dog has already voted yes. Twice."
)
SIGN = "Warmly, Your Host"
PS = "P.S. The Wi-Fi password is on the fridge."

def build():
    c = Canvas(W, H, PAPER)

    # decorative double border
    c.rect(0, 0, W, 10, INK)
    c.rect(0, H - 10, W, 10, INK)
    c.rect(0, 0, 10, H, INK)
    c.rect(W - 10, 0, 10, H, INK)
    c.hline(30, W - 31, 30, GOLD, 3)
    c.hline(30, W - 31, H - 31, GOLD, 3)
    c.vline(30, 30, H - 31, GOLD, 3)
    c.vline(W - 31, 30, H - 31, GOLD, 3)

    # sun, top right inside the border
    draw_sun(c, 905, 105, 26)

    # title
    c.draw_text_centered(78, TITLE, 7, BURGUNDY)
    # small divider with a diamond
    c.hline(330, 470, 152, GOLD, 3)
    c.hline(554, 694, 152, GOLD, 3)
    c.disc(512, 153, 7, BURGUNDY)

    # greeting
    c.draw_text(96, 192, GREETING, 4, INK)

    # body, scale 3, wrapped to the inner width, one paragraph at a time
    # so paragraphs get a visible gap between them
    max_chars = (W - 2 * 96) // (5 * 3 + 3)
    y = 258
    for para in BODY.split("\n"):
        for ln in wrap(para, max_chars):
            c.draw_text(96, y, ln, 3, INK)
            y += 34
        y += 16  # paragraph gap

    # signature, with a little wax seal beside it
    sig_y = y + 8
    c.draw_text(96, sig_y, SIGN, 4, BURGUNDY)
    c.disc(640, sig_y + 14, 18, BURGUNDY)
    c.ring(640, sig_y + 14, 13, GOLD, 2)
    c.disc(640, sig_y + 14, 5, GOLD)

    # postscript, smaller
    c.draw_text(96, sig_y + 52, PS, 3, INK)

    # motifs along the bottom: house left, cup right, paw prints,
    # and a little garden strip with flowers in the middle
    draw_house(c, 120, 850, 12)
    draw_cup(c, 830, 868, 12)
    draw_paw(c, 690, 896, 9)
    draw_paw(c, 734, 924, 9)
    c.hline(330, 660, 956, GREEN, 4)
    draw_flower(c, 380, 936, 7)
    draw_flower(c, 470, 930, 7)
    draw_flower(c, 560, 936, 7)
    draw_flower(c, 630, 928, 7)

    return c

# ---------------------------------------------------------------- PNG writer
def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out

def write_png(c, path):
    raw = bytearray()
    for yy in range(c.h):
        raw.append(0)  # filter: none
        raw += c.px[yy * c.w * 3:(yy + 1) * c.w * 3]
    comp = zlib.compress(bytes(raw), 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

def main():
    c = build()
    if os.path.isdir("/output"):
        outdir = "/output"
    else:
        outdir = os.path.join(os.getcwd(), "output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = write_png(c, path)
    print(f"Wrote {path} ({W}x{H}, {size} bytes)")

if __name__ == "__main__":
    main()
