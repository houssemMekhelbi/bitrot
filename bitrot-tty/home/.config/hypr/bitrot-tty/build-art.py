#!/usr/bin/env python3
"""Generate the Bitrot tty art: everything that is an image rather than CSS.

  ~/.config/hypr/bitrot-tty/wallpaper.svg, wallpaper.png   1920x1080: a memory dump. Six column
        groups of 16-bit hex words in IBM Plex Mono 14px behind their addresses, in the hairline
        colour; toward the lower third the words rot into ░ ▒ ▓ cells. Two slices: near the top two
        rows split into a green ghost shifted left and an amber ghost shifted right; lower down a
        whole row is displaced 24px to the right on a cleared band, its end running off the edge.
        lp prints the dump on continuous-form paper: pale green bars every three rows, a
        perforation line and tractor-feed holes in both margins. Every column is alike and both
        slices run the full width, so a cover crop to a 1440x2560 portrait monitor (the middle
        third) loses nothing essential.
  ~/.config/hypr/bitrot-tty/lock-clock.png   what the lock shows until bitrot-lock-clock's first
        reload: the slice without a time
  ~/.config/waybar/bitrot-tty/cap-left.png, cap-right.png   14x26 bar end caps: three 2px bands,
        green, amber displaced 4px, dim (the right one mirrored)
  ~/.config/waybar/bitrot-tty/ws-<state>.png   8x16 one character cell per workspace state, the
        shade drawn pixel by pixel: ░ empty dim, ▒ occupied secondary, ▓ active (on another
        monitor) amber, █ focused amber, █ urgent error; ws.css picks them
  ~/.config/gtk-3.0/bitrot-tty/crumb-tick.png   Thunar path separator: a 2px hairline tick

Deterministic; edit and re-run (needs rsvg-convert, python-cairo and the theme's fonts):
    python3 build-art.py
"""

import os
import random
import subprocess
from pathlib import Path

CONF = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
HYPR = CONF / "hypr/bitrot-tty"
BAR = CONF / "waybar/bitrot-tty"
GTK = CONF / "gtk-3.0/bitrot-tty"

GROUND, PANEL, LINE, DIM, SEC = "#050806", "#0A110C", "#1E3D26", "#62A66E", "#6FBF7C"
STRUCT, ATT, ERR, WALL_INK = "#33CC55", "#FFB000", "#FF6A55", "#1E3D26"
VARIANT = "tty"


def render(svg, out, keep=False):
    out.parent.mkdir(parents=True, exist_ok=True)
    src = out.with_suffix(".svg")
    src.write_text(svg)
    subprocess.run(["rsvg-convert", "-o", str(out), str(src)], check=True)
    if not keep:
        src.unlink()


def svg(w, h, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{defs}</defs>{body}</svg>\n')


# ---- wallpaper -------------------------------------------------------------------
W, H = 1920, 1080
X0, Y0, LH = 40, 40, 20                 # left margin, first baseline area, line height
ROWS = (H - Y0) // LH + 1
WORDS, GROUP = 36, 6                    # 36 words per row in six groups of six
ROT = "░▒▓"


def dump_rows():
    rnd = random.Random(11)
    rows = []
    for l in range(ROWS):
        line = f"{0x7f3a00 + l * 0x40:08x}  "
        for w in range(WORDS):
            h = f"{rnd.randrange(65536):04X}"
            # the words rot into shade cells from the middle of the screen down
            if l > ROWS * 0.45 and rnd.random() < (l - ROWS * 0.45) / (ROWS * 0.62):
                k = rnd.randrange(4)
                h = h[:k] + rnd.choice(ROT) + h[k + 1:]
                if l > ROWS * 0.75 and rnd.random() < 0.35:
                    k = rnd.randrange(4)
                    h = h[:k] + rnd.choice(ROT) + h[k + 1:]
            line += h + ("   " if w % GROUP == GROUP - 1 else " ")
        rows.append(line.rstrip())
    return rows


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def wallpaper():
    rows = dump_rows()
    text = "".join(f'<text x="{X0}" y="{Y0 + i * LH + 14}">{esc(r)}</text>' for i, r in enumerate(rows))
    dump = f'<g id="dump" font-family="IBM Plex Mono" font-size="14" xml:space="preserve">{text}</g>'
    band = lambda r, n=1: (Y0 + r * LH - 1, n * LH)        # a row band: top, height
    g_top, g_h = band(3)                                     # slice 1: row 3 green ghost, row 4 amber ghost
    a_top, a_h = band(4)                                     # (above the lock clock, below the bar)
    d_top, d_h = band(37)                                    # slice 2: a displaced row (lp: a plain, unbarred row)
    defs = (dump
            + f'<clipPath id="cg"><rect x="0" y="{g_top}" width="{W}" height="{g_h}"/></clipPath>'
            + f'<clipPath id="ca"><rect x="0" y="{a_top}" width="{W}" height="{a_h}"/></clipPath>'
            + f'<clipPath id="cd"><rect x="0" y="{d_top}" width="{W}" height="{d_h}"/></clipPath>')
    if VARIANT == "lp":
        paper = f'<rect width="{W}" height="{H}" fill="{GROUND}"/>'
        for r in range(0, ROWS + 3, 6):                      # greenbar: three rows printed on a bar, three plain
            paper += f'<rect x="0" y="{Y0 + (r + 3) * LH - 1}" width="{W}" height="{3 * LH}" fill="{PANEL}"/>'
        for x in (22, W - 22):                               # tractor feed: holes and a perforation in each margin
            paper += "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="none" stroke="{LINE}" stroke-width="1.5"/>'
                             for y in range(12, H, 24))
        for x in (36, W - 36):
            paper += f'<path d="M{x} 0 V{H}" stroke="{LINE}" stroke-width="1" stroke-dasharray="3 5"/>'
    else:
        paper = f'<rect width="{W}" height="{H}" fill="{GROUND}"/>'
    body = (paper
            + f'<use xlink:href="#dump" fill="{WALL_INK}"/>'
            + f'<use xlink:href="#dump" fill="{STRUCT}" fill-opacity="0.8" transform="translate(-8 0)" clip-path="url(#cg)"/>'
            + f'<use xlink:href="#dump" fill="{ATT}" fill-opacity="0.8" transform="translate(8 0)" clip-path="url(#ca)"/>'
            + f'<rect x="0" y="{d_top}" width="{W}" height="{d_h}" fill="{GROUND}"/>'
            + f'<use xlink:href="#dump" fill="{WALL_INK}" transform="translate(24 0)" clip-path="url(#cd)"/>')
    render(svg(W, H, body, defs), HYPR / "wallpaper.png", keep=True)


# ---- bar end caps ------------------------------------------------------------------
def caps():
    left = (f'<rect x="0" y="8" width="14" height="2" fill="{STRUCT}"/>'
            f'<rect x="4" y="12" width="10" height="2" fill="{ATT}"/>'
            f'<rect x="0" y="16" width="14" height="2" fill="{DIM}"/>')
    right = (f'<rect x="0" y="8" width="14" height="2" fill="{DIM}"/>'
             f'<rect x="0" y="12" width="10" height="2" fill="{ATT}"/>'
             f'<rect x="0" y="16" width="14" height="2" fill="{STRUCT}"/>')
    render(svg(14, 26, left), BAR / "cap-left.png")
    render(svg(14, 26, right), BAR / "cap-right.png")


# ---- workspace cells -----------------------------------------------------------------
def shade(level, colour, w=8, h=16):
    """a character cell in shade: 1 = ░ (one pixel in four), 2 = ▒ (checker), 3 = ▓ (three in four), 4 = █"""
    if level == 4:
        return f'<rect width="{w}" height="{h}" fill="{colour}"/>'
    px = []
    for y in range(h):
        for x in range(w):
            on = {1: x % 2 == 0 and y % 2 == 0, 2: (x + y) % 2 == 0, 3: not (x % 2 == 1 and y % 2 == 1)}[level]
            if on:
                px.append(f"M{x} {y}h1v1h-1z")
    return f'<path d="{"".join(px)}" fill="{colour}"/>'


def workspaces():
    states = {"empty": (1, DIM), "occupied": (2, SEC), "active": (3, ATT), "urgent": (4, ERR), "focused": (4, ATT)}
    css = ["/* Generated by ~/.config/hypr/bitrot-tty/build-art.py: one shade cell per state (the same in every slot). */"]
    ids = lambda suffix: ",\n".join(f"#custom-ws-{n}{suffix}" for n in range(1, 11))
    for state, (level, colour) in states.items():
        render(svg(8, 16, shade(level, colour)), BAR / f"ws-{state}.png")
    # order matters: a focused slot carries .active and .focused, so .focused comes last
    for state in ("occupied", "empty", "active", "urgent", "focused"):
        css.append(f'{ids("" if state == "occupied" else "." + state)} {{ background-image: url("ws-{state}.png"); }}')
    (BAR / "ws.css").write_text("\n".join(css) + "\n")


def crumb():
    render(svg(12, 18, f'<rect x="9" y="3" width="2" height="12" fill="{LINE}"/>'), GTK / "crumb-tick.png")


def lock_clock():
    subprocess.run([str(Path.home() / ".local/bin/bitrot-lock-clock"), "--static", str(HYPR / "lock-clock.png")], check=True)


if __name__ == "__main__":
    wallpaper()
    caps()
    workspaces()
    crumb()
    lock_clock()
    print("art written")
