#!/usr/bin/env python3
"""Generate the BitrotLpCell cursor theme (Bitrot lp) next to this file.

Every cursor is a composition of character cells (8 by 14 units each in a
32-unit square), drawn in #1A1F1A with a 1px #F4F1E6 outline
so it reads on both grounds. The hotspot is the top-left cell. The arrow is a
full block over a half block; the link pointer adds a small square cell; the
text cursor is a left half block two cells tall. Busy is the one-eighth ramp
▁▂▃▄▅▆▇█ in amber over 800 ms (8 frames); progress is the arrow with the ramp
beside it. Crosshair ┼, not-allowed ╪, grab ▙▟, grabbing ▟▙, move ╬, and the
resize arrows. Cursors never slice: a displaced band would move the hotspot.

Writes two formats from the same SVGs:
  hyprcursors/ + manifest.hl*   hyprcursor (Hyprland draws it; SVG, any size)
  cursors/                      XCursor 24/32/48 (GTK3, XWayland, anything else)
Shapes not drawn here fall back to Adwaita (index.theme Inherits).
Needs rsvg-convert and hyprcursor-util. Run: python3 build.py
"""

import os
import shutil
import struct
import subprocess
import tempfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = "BitrotLpCell"
FILL, EDGE, AMBER = "#1A1F1A", "#F4F1E6", "#8A5200"
XSIZES = (24, 32, 48)
CW, CH = 8, 14                      # one character cell
X0, Y0 = 2, 2                       # the top-left cell starts here (hotspot)


def cur(*parts):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">'
            + "".join(parts) + "</svg>\n")


def shape(d, colour=FILL):
    """a filled path with the 1px outline (a 2-unit stroke under the fill)"""
    return (f'<path d="{d}" fill="{EDGE}" stroke="{EDGE}" stroke-width="2" stroke-linejoin="miter"/>'
            f'<path d="{d}" fill="{colour}"/>')


def box(x, y, w, h):
    return f"M{x} {y}h{w}v{h}h{-w}z"


def line(d, colour=FILL, w=2.2):
    """a stroked line with the outline"""
    return (f'<path d="{d}" fill="none" stroke="{EDGE}" stroke-width="{w + 2}" stroke-linecap="square"/>'
            f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{w}" stroke-linecap="square"/>')


def at(col, row):
    return X0 + col * CW, Y0 + row * CH


def full(col, row):
    x, y = at(col, row)
    return box(x, y, CW, CH)


def upper(col, row):
    x, y = at(col, row)
    return box(x, y, CW, CH / 2)


def ramp(col, row, k, x_off=0.0, y_off=0.0):
    """frame k (0-7) of the ramp ▁▂▃▄▅▆▇█ in one cell"""
    x, y = at(col, row)
    h = CH * (k + 1) / 8
    return shape(box(x + x_off, y + y_off + CH - h, CW, h), AMBER)


ARROW = shape(full(0, 0) + upper(0, 1))
SMALL = shape(box(at(1, 0)[0] + 1.5, at(1, 0)[1] + 4, CW - 3, 6))
FRAMES = 8


def arrows(pairs):
    """resize arrows: shafts with square heads"""
    return "".join(line(d) for d in pairs)


SHAPES = {
    "left_ptr": ([cur(ARROW)], (X0, Y0), 0,
                 ["default", "arrow", "top_left_arrow", "left_arrow", "context-menu", "copy", "alias",
                  "dnd-copy", "dnd-link", "dnd-none", "dnd-ask", "help", "question_arrow", "whats_this"]),
    "hand2": ([cur(ARROW, SMALL)], (X0, Y0), 0,
              ["pointer", "hand1", "hand", "pointing_hand", "e29285e634086352946a0e7090d73106"]),
    "xterm": ([cur(shape(box(14, 2, 4, 28)))], (16, 16), 0, ["text", "ibeam"]),
    "vertical-text": ([cur(shape(box(2, 14, 28, 4)))], (16, 16), 0, []),
    "watch": ([cur(ramp(0, 0, k, 10, 7)) for k in range(FRAMES)], (16, 16), 100, ["wait"]),
    "left_ptr_watch": ([cur(ARROW, ramp(1, 0, k, 3, 7)) for k in range(FRAMES)], (X0, Y0), 100,
                       ["progress", "half-busy", "00000000000000020006000e7e9ffc3f",
                        "08e8e1c95fe2fc01f976f1e063a24ccd", "3ecb610c1bf2410f44200f48c40d3599"]),
    "crosshair": ([cur(line("M16 3 V29 M3 16 H29"))], (16, 16), 0,
                  ["cross", "tcross", "cell", "plus", "color-picker"]),
    "not-allowed": ([cur(line("M16 3 V29 M7 12 H25 M7 20 H25"))], (16, 16), 0,
                    ["no-drop", "forbidden", "circle", "crossed_circle", "dnd-no-drop"]),
    "grab": ([cur(shape(f"M3 4 h6 v10 h7 v6 h-13 z M29 4 h-6 v10 h-7 v6 h13 z"))], (16, 16), 0,
             ["openhand", "hand-grab"]),
    "grabbing": ([cur(shape(f"M9 12 h7 v8 h-13 v-2 h6 z M23 12 h-7 v8 h13 v-2 h-6 z"))], (16, 16), 0,
                 ["closedhand", "dnd-move", "hand-grabbing"]),
    "fleur": ([cur(line("M13 3 V29 M19 3 V29 M3 13 H29 M3 19 H29", w=1.8))], (16, 16), 0,
              ["move", "all-scroll", "size_all", "4498f0e0c1937ffe01fd06f973665830", "9081237383d90e509aa00f00170e968f"]),
    "sb_h_double_arrow": ([cur(arrows(["M4 16 H28", "M9 11 L4 16 L9 21", "M23 11 L28 16 L23 21"]))], (16, 16), 0,
                          ["ew-resize", "col-resize", "e-resize", "w-resize", "h_double_arrow", "left_side",
                           "right_side", "size_hor", "split_h", "14fef782d02440884392942c11205230",
                           "028006030e0e7ebffc7f7070c0600140"]),
    "sb_v_double_arrow": ([cur(arrows(["M16 4 V28", "M11 9 L16 4 L21 9", "M11 23 L16 28 L21 23"]))], (16, 16), 0,
                          ["ns-resize", "row-resize", "n-resize", "s-resize", "v_double_arrow", "top_side",
                           "bottom_side", "size_ver", "split_v", "2870a09082c103050810ffdffffe0204",
                           "00008160000006810000408080010102"]),
    "bd_double_arrow": ([cur(arrows(["M6 6 L26 26", "M5 12 V5 H12", "M27 20 V27 H20"]))], (16, 16), 0,
                        ["nwse-resize", "nw-resize", "se-resize", "top_left_corner",
                         "bottom_right_corner", "size_fdiag", "c7088f0f3e6c8088236ef8e1e3e70000"]),
    "fd_double_arrow": ([cur(arrows(["M26 6 L6 26", "M20 5 H27 V12", "M12 27 H5 V20"]))], (16, 16), 0,
                        ["nesw-resize", "ne-resize", "sw-resize", "top_right_corner",
                         "bottom_left_corner", "size_bdiag", "fcf1c3c7cd4491d801f1e1c78f100000"]),
}


# ---- PNG decode (8-bit RGBA from rsvg-convert) --------------------------------

def load_png(path):
    d = Path(path).read_bytes()
    pos, idat = 8, b""
    while pos < len(d):
        n, t = struct.unpack(">I4s", d[pos:pos + 8])
        body = d[pos + 8:pos + 8 + n]
        pos += 12 + n
        if t == b"IHDR":
            w, h, bd, ct = struct.unpack(">IIBB", body[:10])
            assert bd == 8 and ct == 6, "expected 8-bit RGBA"
        elif t == b"IDAT":
            idat += body
    raw, bpp, stride = zlib.decompress(idat), 4, w * 4
    rows, prev, i = [], bytearray(stride), 0
    for _ in range(h):
        f, line_ = raw[i], bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = line_[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if f == 1:
                line_[x] = (line_[x] + a) & 255
            elif f == 2:
                line_[x] = (line_[x] + b) & 255
            elif f == 3:
                line_[x] = (line_[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line_[x] = (line_[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(bytes(line_))
        prev = line_
    return w, h, rows


def argb_premultiplied(rows):
    out = bytearray()
    for r in rows:
        for x in range(0, len(r), 4):
            R, G, B, A = r[x:x + 4]
            out += struct.pack("<I", (A << 24) | ((R * A // 255) << 16) | ((G * A // 255) << 8) | (B * A // 255))
    return bytes(out)


def xcursor(images):
    """images: list of (nominal, w, h, xhot, yhot, delay, argb). Returns XCursor bytes."""
    ntoc = len(images)
    header = struct.pack("<4sIII", b"Xcur", 16, 0x10000, ntoc)
    pos = 16 + ntoc * 12
    toc, chunks = b"", b""
    for nominal, w, h, xh, yh, delay, px in images:
        toc += struct.pack("<III", 0xFFFD0002, nominal, pos)
        chunk = struct.pack("<IIIIIIIII", 36, 0xFFFD0002, nominal, 1, w, h, xh, yh, delay) + px
        chunks += chunk
        pos += len(chunk)
    return header + toc + chunks


def main():
    for d in ("hyprcursors", "cursors"):
        shutil.rmtree(ROOT / d, ignore_errors=True)
    for f in ROOT.glob("manifest.*"):
        f.unlink()
    (ROOT / "cursors").mkdir()

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "work"
        (work / "hyprcursors").mkdir(parents=True)
        (work / "manifest.hl").write_text(
            f"name = {NAME}\ndescription = Bitrot lp: character-cell block cursors, an amber ramp when busy\n"
            "version = 0.1\ncursors_directory = hyprcursors\n")
        for shape, (frames, (hx, hy), delay, aliases) in SHAPES.items():
            sd = work / "hyprcursors" / shape
            sd.mkdir()
            meta = [f"resize_algorithm = bilinear", f"hotspot_x = {hx / 32:.4f}", f"hotspot_y = {hy / 32:.4f}"]
            meta += [f"define_override = {a}" for a in aliases]
            images = []
            for k, body in enumerate(frames):
                fname = f"{shape}-{k}.svg"
                (sd / fname).write_text(body)
                meta.append(f"define_size = 0, {fname}" + (f", {delay}" if delay else ""))
                for size in XSIZES:
                    png = Path(tmp) / f"{shape}-{k}-{size}.png"
                    subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), "-o", str(png), str(sd / fname)], check=True)
                    w, h, rows = load_png(png)
                    images.append((size, w, h, round(hx * size / 32), round(hy * size / 32), delay or 0, argb_premultiplied(rows)))
            (sd / "meta.hl").write_text("\n".join(meta) + "\n")
            images.sort(key=lambda i: i[0])
            (ROOT / "cursors" / shape).write_bytes(xcursor(images))
            for a in aliases:
                link = ROOT / "cursors" / a
                if not link.exists():
                    os.symlink(shape, link)

        out = Path(tmp) / "out"
        out.mkdir()
        subprocess.run(["hyprcursor-util", "--create", str(work), "--output", str(out)], check=True,
                       stdout=subprocess.DEVNULL)
        built = next(out.iterdir())
        for item in built.iterdir():
            dest = ROOT / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

    (ROOT / "index.theme").write_text(
        f"[Icon Theme]\nName={NAME}\nComment=Bitrot lp cursors: character-cell blocks, an amber one-eighth ramp when busy\nInherits=Adwaita\n")
    print(f"{NAME} written to {ROOT}")


if __name__ == "__main__":
    main()
