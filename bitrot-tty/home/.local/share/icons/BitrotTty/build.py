#!/usr/bin/env python3
"""Generate the BitrotTty icon theme next to this file (Bitrot tty).

scalable/  64-unit SVGs: every icon is a composition of character cells on a
           monospace grid (cells 9 wide, 15 high), shade blocks in the structure
           colour on a transparent ground: ▓ at 78%, ▒ at 50%, ░ at 25%, █ solid,
           ▀ the upper half. The third row of every icon is displaced one cell to
           the right: the only glitch an icon carries. Folders are a ▓ body under
           a tab; the special folders cut one cell into the body (home ░, documents
           ≡, downloads ↓, pictures ▒ ...). Documents are a ▓ frame around ░ lines
           (the PDF prints its tag in the secondary colour); an image holds a
           ░▒▓█ ramp; the drive is a full block row with one indicator cell in the
           up colour; network is two blocks on a bus; trash is a lid over a ▒ body,
           ▓ when full. Marks are drawn as shapes, never as font text.
16/        sidebar size: one cell glyph each (⌂ ▓ █ ▀ ▒ ≡ ...) in the secondary colour.
Anything not drawn here falls through to Adwaita.
Run: python3 build.py   (then gtk-update-icon-cache runs by itself)
"""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = "BitrotTty"

STRUCT, SEC, UP = "#33CC55", "#6FBF7C", "#7DFF8F"
CW, CH = 9, 15                     # cell
SHADE = {"▓": 0.78, "▒": 0.50, "░": 0.25, "█": 1.0}


def rect(x, y, w, h, colour=STRUCT, op=1.0):
    o = f' fill-opacity="{op}"' if op < 1 else ""
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{colour}"{o}/>'


def pixels(rows, x, y, w, h, colour):
    """a tiny pixel letter: rows of '#' and '.', fitted into the box"""
    n, m = len(rows), len(rows[0])
    pw, ph = w / m, h / n
    return "".join(rect(x + i * pw, y + j * ph, pw + 0.01, ph + 0.01, colour) for j, r in enumerate(rows) for i, c in enumerate(r) if c == "#")


LETTERS = {
    "P": ["###", "#.#", "###", "#..", "#.."],
    "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "F": ["###", "#..", "##.", "#..", "#.."],
    "A": [".#.", "#.#", "###", "#.#", "#.#"],
}


def cell(ch, x, y, colour=STRUCT):
    """one character cell at (x, y)"""
    if ch in SHADE:
        return rect(x, y, CW, CH, colour, SHADE[ch])
    if ch == "▀":
        return rect(x, y, CW, CH / 2, colour)
    if ch == "▄":
        return rect(x, y + CH / 2, CW, CH / 2, colour)
    if ch == "▪":
        return rect(x + 2, y + 4.5, CW - 4, 6, UP)
    if ch == "≡":
        return "".join(rect(x + 1, y + 3 + k * 4, CW - 2, 2, colour) for k in range(3))
    if ch == "↓":
        return (rect(x + 3.5, y + 2, 2, 8, colour)
                + f'<path d="M{x + 1} {y + 8} H{x + 8} L{x + 4.5} {y + 13} Z" fill="{colour}"/>')
    if ch == "▶":
        return f'<path d="M{x + 1.5} {y + 3} L{x + 8} {y + 7.5} L{x + 1.5} {y + 12} Z" fill="{colour}"/>'
    if ch == ">":
        return f'<path d="M{x + 1.5} {y + 3.5} L{x + 7} {y + 7.5} L{x + 1.5} {y + 11.5}" fill="none" stroke="{colour}" stroke-width="2" stroke-linecap="square"/>'
    if ch == "<":
        return f'<path d="M{x + 7.5} {y + 3.5} L{x + 2} {y + 7.5} L{x + 7.5} {y + 11.5}" fill="none" stroke="{colour}" stroke-width="2" stroke-linecap="square"/>'
    if ch == "┼":
        return rect(x + 3.5, y, 2, CH, colour) + rect(x, y + 6.5, CW, 2, colour)
    if ch == "▚":
        return rect(x, y, CW / 2, CH / 2, colour) + rect(x + CW / 2, y + CH / 2, CW / 2, CH / 2, colour)
    if ch == "▞":
        return rect(x + CW / 2, y, CW / 2, CH / 2, colour) + rect(x, y + CH / 2, CW / 2, CH / 2, colour)
    if ch == "□":
        return f'<rect x="{x + 1.5}" y="{y + 3.5}" width="{CW - 3}" height="{CH - 7}" fill="none" stroke="{colour}" stroke-width="1.6"/>'
    if ch in "▂▆▄":
        frac = {"▂": 0.25, "▄": 0.5, "▆": 0.75}[ch]
        return rect(x, y + CH * (1 - frac), CW, CH * frac, colour)
    if ch in LETTERS:
        return pixels(LETTERS[ch], x + 1.5, y + 3, CW - 3, CH - 6, SEC)
    return ""


def compose(art):
    """art: rows of characters; the third row starts one cell to the right (a leading space).
    The plain blocks of one shade are merged into one path, so no seam shows between cells
    when the icon is scaled."""
    rows = art.split("\n")
    cols = max(len(r) for r in rows)
    w, h = cols * CW, len(rows) * CH
    x0, y0 = round((64 - w) / 2), round((64 - h) / 2)
    runs, marks = {}, ""
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            x, y = x0 + i * CW, y0 + j * CH
            if ch in SHADE:
                runs.setdefault(SHADE[ch], []).append(f"M{x} {y}h{CW}v{CH}h{-CW}z")
            elif ch == "▀":
                runs.setdefault(1.0, []).append(f"M{x} {y}h{CW}v{CH / 2}h{-CW}z")
            elif ch == "▄":
                runs.setdefault(1.0, []).append(f"M{x} {y + CH / 2}h{CW}v{CH / 2}h{-CW}z")
            elif ch != " ":
                marks += cell(ch, x, y)
    body = "".join(f'<path d="{"".join(d)}" fill="{STRUCT}"' + (f' fill-opacity="{op}"' if op < 1 else "") + "/>"
                   for op, d in sorted(runs.items()))
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">{body}{marks}</svg>\n'


def write(rel, content, names):
    for name in names:
        path = ROOT / rel / f"{name}.svg"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def folder(mark=None):
    return compose("▓▓▓\n▓▓▓▓▓▓\n ▓▓" + (mark or "▓") + "▓▓▓\n▓▓▓▓▓▓")


FOLDERS = {
    None: ["folder", "inode-directory", "folder-open", "folder-drag-accept", "folder-visiting"],
    "░": ["user-home", "folder-home"],
    "≡": ["folder-documents"],
    "↓": ["folder-download"],
    "▚": ["folder-music"],
    "▒": ["folder-pictures"],
    "▶": ["folder-videos"],
    "□": ["folder-templates"],
    "▞": ["folder-publicshare"],
    "▀": ["user-desktop"],
}
for mark, names in FOLDERS.items():
    write("scalable/places", folder(mark), names)
    if mark is None:
        write("scalable/mimetypes", folder(mark), names)

NETWORK = compose("██  ██\n▀▀▀▀▀▀\n ██  ██\n▀▀▀▀▀▀")
write("scalable/places", NETWORK, ["folder-remote", "network-workgroup", "network-server"])
write("scalable/places", compose("▀▀▀▀▀\n▒▒▒▒▒\n ▒▒▒▒▒\n▒▒▒▒▒"), ["user-trash"])
write("scalable/places", compose("▀▀▀▀▀\n▓▓▓▓▓\n ▓▓▓▓▓\n▓▓▓▓▓"), ["user-trash-full"])


def doc(row2, row3):
    return compose(f"▓▓▓▓▓\n{row2}\n {row3}\n▓▓▓▓▓")


DOCUMENTS = {
    doc("▓░░░▓", "▓░░▓▓"): ["application-x-generic", "unknown", "empty", "text-x-generic", "text-plain",
                            "x-office-document", "text-markdown", "text-x-readme"],
    doc("▓>░░▓", "▓░░▓▓"): ["text-x-script", "application-x-shellscript", "text-x-python", "text-x-makefile"],
    doc("▓<>░▓", "▓░░▓▓"): ["text-html", "application-json", "text-x-csrc", "text-x-c++src", "text-x-javascript"],
    doc("▓███▓", "▓██▓▓"): ["application-x-executable", "application-x-sharedlib"],
    compose("▓▓▓▓▓▓\n▓░▒▓█▓\n ▓░▒▓█▓\n▓▓▓▓▓▓"): ["image-x-generic"],
    doc("▓▂▆▄▓", "▓▆▂▓▓"): ["audio-x-generic"],
    doc("▓░▶░▓", "▓░░▓▓"): ["video-x-generic"],
    doc("▓▚▞░▓", "▓▚▞▓▓"): ["package-x-generic", "application-x-archive", "application-zip",
                            "application-x-compressed-tar", "application-x-tar"],
    doc("▓░░░▓", "▓PDF▓"): ["application-pdf"],
    doc("▓┼┼┼▓", "▓┼┼▓▓"): ["x-office-spreadsheet"],
    doc("▓▀▀▀▓", "▓░░▓▓"): ["x-office-presentation"],
    doc("▓░A░▓", "▓░░▓▓"): ["font-x-generic"],
}
for svg, names in DOCUMENTS.items():
    write("scalable/mimetypes", svg, names)

DEVICES = {
    compose("▓▓▓▓▓▓\n██████\n ▪▓▓▓▓▓\n▓▓▓▓▓▓"): ["drive-harddisk", "drive-harddisk-system", "drive-multidisk"],
    compose(" ▀▀ \n▓▓▓▓\n ▪▓▓▓\n▓▓▓▓"): ["drive-removable-media", "drive-harddisk-usb", "media-removable", "media-flash"],
    compose("▄██▄\n█░░█\n █░░█\n▀██▀"): ["drive-optical", "media-optical"],
    compose("▓▓▓▓▓▓\n▓░░░░▓\n ▓░░░░▓\n▀▀██▀▀"): ["computer", "video-display"],
}
for svg, names in DEVICES.items():
    write("scalable/devices", svg, names)


# ---- 16px sidebar: one cell glyph -------------------------------------------------
def glyph16(ch):
    if ch == "⌂":
        body = f'<path d="M3 8 L8 3.5 L13 8 V14 H3 Z" fill="none" stroke="{SEC}" stroke-width="1.6" stroke-linejoin="miter"/>'
    else:
        # one character cell (9x15 units) scaled into the 16px square
        body = f'<g transform="translate(3.5 0.5)">{cell(ch, 0, 0, SEC)}</g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">{body}</svg>\n'


SIDEBAR = {
    "places": {
        "⌂": ["user-home", "folder-home", "go-home"], "▀": ["user-desktop"], "≡": ["folder-documents", "document-open-recent", "folder-recent"],
        "↓": ["folder-download"], "▚": ["folder-music"], "▒": ["folder-pictures", "user-trash", "user-trash-full"],
        "▶": ["folder-videos"], "□": ["folder-templates", "user-bookmarks", "bookmark-new"], "▞": ["folder-publicshare"],
        "▓": ["folder", "inode-directory", "folder-open", "folder-drag-accept", "folder-visiting"],
        "▂": ["folder-remote", "network-workgroup", "network-server"],
    },
    "devices": {
        "█": ["drive-harddisk", "drive-harddisk-system", "drive-multidisk", "drive-removable-media", "drive-harddisk-usb",
              "media-removable", "media-flash", "drive-optical", "media-optical", "computer", "video-display"],
    },
}
for ctx, groups in SIDEBAR.items():
    for ch, names in groups.items():
        write(f"16/{ctx}", glyph16(ch), names)

(ROOT / "index.theme").write_text(f"""[Icon Theme]
Name={NAME}
Comment=Bitrot tty: shade-block compositions on a character grid, the third row displaced one cell
Inherits=Adwaita,hicolor
Example=folder

Directories=16/places,16/devices,scalable/places,scalable/mimetypes,scalable/devices

[16/places]
Size=16
Context=Places
Type=Fixed

[16/devices]
Size=16
Context=Devices
Type=Fixed

[scalable/places]
Size=64
MinSize=20
MaxSize=512
Context=Places
Type=Scalable

[scalable/mimetypes]
Size=64
MinSize=16
MaxSize=512
Context=MimeTypes
Type=Scalable

[scalable/devices]
Size=64
MinSize=20
MaxSize=512
Context=Devices
Type=Scalable
""")
subprocess.run(["gtk-update-icon-cache", "-f", "-t", str(ROOT)], check=False,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"{NAME} icons written to {ROOT}")
