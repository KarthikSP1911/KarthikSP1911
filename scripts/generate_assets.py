#!/usr/bin/env python3
"""Generate the animated RPG-style SVGs used in README.md.

Outputs (light + dark variants of each) into assets/rpg/:
  hero-{theme}.svg             animated pixel-art player character
  banner-{theme}.svg           pixel-art "LEVEL UP" header
  stats-{theme}.svg            animated HP / XP / attribute bars
  room-{1,2,3}-{theme}.svg     dungeon "quest map" rooms, one per project

Edit STATS / ROOMS below and re-run:  python3 scripts/generate_assets.py
"""
import os
import random

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "rpg")

THEMES = {
    "dark":  {"bg": "#0d1117", "fg": "#ffffff", "mid": "#8b949e", "dim": "#30363d", "faint": "#161b22", "skin": "#c9d1d9", "hair": "#484f58"},
    "light": {"bg": "#ffffff", "fg": "#1f2328", "mid": "#57606a", "dim": "#d0d7de", "faint": "#f6f8fa", "skin": "#eaeef2", "hair": "#1f2328"},
}

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

STATS = [
    ("COMBAT", [
        ("DSA / PROBLEM SOLVING", 90),
        ("BACKEND ENGINEERING", 85),
        ("DISTRIBUTED SYSTEMS", 75),
        ("FRONTEND", 75),
        ("CLOUD &amp; DEVOPS", 70),
        ("AI / GENAI", 65),
    ]),
    ("PHYSICAL", [
        ("STAMINA  (MARATHONS)", 95),
        ("STRENGTH (GYM)", 80),
        ("DEXTERITY (RUBIK'S)", 85),
    ]),
]

ROOMS = [
    {"num": "I",   "name": "MSR INSIGHT", "tag": "AI ACADEMIC REPORTING", "tech": "Next.js · FastAPI · RAG",   "status": "cleared"},
    {"num": "II",  "name": "QUANT EDGE",  "tag": "AI TRADING PLATFORM",   "tech": "Spring Boot · Kafka · AI", "status": "cleared"},
    {"num": "III", "name": "LEETFORCE",   "tag": "CODE EXECUTION ARENA",  "tech": "Go · K8s · Terraform",     "status": "active"},
]

# --------------------------------------------------------------------------- #
# 5x7 pixel font
# --------------------------------------------------------------------------- #
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "10001", "11001", "10101", "10011", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    ">": ["01000", "00100", "00010", "00001", "00010", "00100", "01000"],
    " ": ["00000"] * 7,
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def pixel_text(text, x, y, scale, color, char_class=None, delay_step=0.0, delay0=0.0):
    """Render text as pixel rects. Each glyph is its own <g> so it can animate."""
    out = []
    for i, ch in enumerate(text.upper()):
        glyph = FONT.get(ch, FONT[" "])
        rects = []
        for r, row in enumerate(glyph):
            for c, bit in enumerate(row):
                if bit == "1":
                    rects.append(
                        f'<rect x="{x + (i * 6 + c) * scale}" y="{y + r * scale}" '
                        f'width="{scale}" height="{scale}"/>'
                    )
        if not rects:
            continue
        attrs = f'fill="{color}"'
        if char_class:
            attrs += f' class="{char_class}" style="animation-delay:{delay0 + i * delay_step:.2f}s"'
        out.append(f"<g {attrs}>{''.join(rects)}</g>")
    return "".join(out)


def sprite(rows, x, y, scale, colors):
    out = []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch in colors:
                out.append(
                    f'<rect x="{x + c * scale}" y="{y + r * scale}" width="{scale}" '
                    f'height="{scale}" fill="{colors[ch]}"/>'
                )
    return "".join(out)


def svg(w, h, body, style, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{title}" shape-rendering="crispEdges">'
        f"<title>{title}</title><style>{style}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important;opacity:1!important}}"
        f"</style>{body}</svg>\n"
    )


# --------------------------------------------------------------------------- #
# Hero (player character)
# --------------------------------------------------------------------------- #
HERO = [
    "    ########    ",
    "   #hhhhhhhh#   ",
    "  #hhhhhhhhhh#  ",
    "  #hhssssshhh#  ",
    "  #ssssssssss#  ",
    "  #ssesssesss#  ",
    "  #ssssssssss#  ",
    "  #sssmmmmsss#  ",
    "   #ssssssss#   ",
    "    ##ssss##    ",
    "  ############  ",
    " #oooooooooooo# ",
    "#oo#oooooooo#oo#",
    "#oo#ooowwooo#oo#",
    "#oo#oooooooo#oo#",
    "#ss#oooooooo#ss#",
    " ##oooooooooo## ",
    "   #pppppppp#   ",
    "   #ppp##ppp#   ",
    "   #ppp##ppp#   ",
    "  #fff#  #fff#  ",
    "  #####  #####  ",
]
CUBE = [
    "#######",
    "#o#w#o#",
    "#######",
    "#w#o#w#",
    "#######",
    "#o#w#o#",
    "#######",
]
DUMBBELL = [
    "##     ##",
    "##     ##",
    "#########",
    "##     ##",
    "##     ##",
]


def hero(t):
    W, H = 300, 360
    style = (
        "@keyframes idle{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}"
        ".idle{animation:idle 1.4s steps(2) infinite}"
        "@keyframes eye{0%,92%,100%{opacity:1}94%,98%{opacity:0}}"
        ".eye{animation:eye 4s steps(1) infinite}"
        "@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}"
        ".fl1{animation:float 2.2s steps(4) infinite}"
        ".fl2{animation:float 2.6s steps(4) infinite .7s}"
        ".fl3{animation:float 2s steps(4) infinite 1.3s}"
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
        ".bl{animation:blink 1s steps(1) infinite}"
    )
    sc = 10
    sx, sy = (W - 16 * sc) // 2, 46
    colors = {
        "#": t["fg"], "h": t["hair"], "s": t["skin"], "e": t["skin"], "m": t["fg"],
        "o": t["mid"], "w": t["bg"], "p": t["dim"], "f": t["fg"],
    }
    eyes = [row.replace("e", "#") for row in HERO]
    eyes = [''.join(c if c == "#" and HERO[r][i] == "e" else " " for i, c in enumerate(row))
            for r, row in enumerate(eyes)]
    b = [f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>']
    b.append(f'<rect x="3" y="3" width="{W-6}" height="{H-6}" fill="none" stroke="{t["fg"]}" stroke-width="4"/>')
    b.append(f'<rect x="12" y="12" width="{W-24}" height="{H-24}" fill="none" stroke="{t["dim"]}" stroke-width="1"/>')
    b.append(f'<text x="{W//2}" y="34" text-anchor="middle" font-family="{MONO}" font-size="11" letter-spacing="3" fill="{t["mid"]}">PLAYER 1</text>')
    # ground shadow
    b.append(f'<rect x="{sx+30}" y="{sy+22*sc+4}" width="{16*sc-60}" height="6" fill="{t["dim"]}"/>')
    b.append(
        f'<g class="idle">{sprite(HERO, sx, sy, sc, colors)}'
        f'<g class="eye">{sprite(eyes, sx, sy, sc, {"#": t["fg"]})}</g></g>'
    )
    # floating items: </> code, rubik's cube, dumbbell
    item = {"#": t["fg"], "o": t["mid"], "w": t["bg"]}
    b.append(f'<g class="fl1">{sprite(CUBE, 30, 92, 4, item)}</g>')
    b.append(f'<g class="fl2">{sprite(DUMBBELL, W - 30 - 9 * 4, 100, 4, item)}</g>')
    b.append(
        f'<g class="fl3"><text x="22" y="236" font-family="{MONO}" font-size="18" font-weight="700" '
        f'fill="{t["fg"]}">&lt;/&gt;</text></g>'
    )
    b.append(f'<g class="fl1"><text x="{W-58}" y="236" font-family="{MONO}" font-size="18" font-weight="700" fill="{t["fg"]}">{{ }}</text></g>')
    # name plate + mini HP bar
    b.append(pixel_text("KARTHIK", (W - text_width("KARTHIK", 4)) // 2, 296, 4, t["fg"]))
    hx = (W - 20 * 9) // 2
    for i in range(20):
        b.append(f'<rect x="{hx + i*9}" y="{332}" width="7" height="8" fill="{t["fg"]}"/>')
    b.append(f'<text x="{hx-8}" y="340" text-anchor="end" font-family="{MONO}" font-size="10" fill="{t["mid"]}">HP</text>')
    b.append(f'<text class="bl" x="{hx+180+6}" y="340" font-family="{MONO}" font-size="10" fill="{t["fg"]}">▮</text>')
    return svg(W, H, "".join(b), style, "Player 1: Karthik, pixel-art character")


# --------------------------------------------------------------------------- #
# Banner
# --------------------------------------------------------------------------- #
def banner(t):
    W, H = 1200, 320
    rnd = random.Random(1911)
    style = (
        "@keyframes tw{0%,100%{opacity:.15}50%{opacity:1}}"
        ".st{animation:tw 2.4s steps(4) infinite}"
        "@keyframes flash{0%,49%{opacity:1}50%,100%{opacity:.25}}"
        ".lv{animation:flash 1s steps(1) infinite}"
        "@keyframes pop{0%{opacity:0;transform:translateY(-12px)}100%{opacity:1;transform:none}}"
        ".ch{opacity:0;animation:pop .35s steps(3) forwards}"
        "@keyframes fill{to{opacity:1}}"
        ".xp{opacity:0;animation:fill .12s linear forwards}"
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
        ".bl{animation:blink 1.1s steps(1) infinite}"
        "@keyframes fade{from{opacity:0}to{opacity:1}}"
        ".fd{opacity:0;animation:fade .6s ease forwards}"
    )
    b = [f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>']
    # 8-bit double frame with notched corners
    b.append(f'<rect x="10" y="10" width="{W-20}" height="{H-20}" fill="none" stroke="{t["fg"]}" stroke-width="6"/>')
    b.append(f'<rect x="24" y="24" width="{W-48}" height="{H-48}" fill="none" stroke="{t["dim"]}" stroke-width="2"/>')
    for cx, cy in [(7, 7), (W - 19, 7), (7, H - 19), (W - 19, H - 19)]:
        b.append(f'<rect x="{cx}" y="{cy}" width="12" height="12" fill="{t["bg"]}"/>')
    # twinkling stars, kept out of the text block
    for _ in range(46):
        sx, sy = rnd.randint(36, W - 40), rnd.randint(34, H - 40)
        if 150 < sx < 1050 and 30 < sy < 290:
            continue
        s = rnd.choice([3, 3, 4, 6])
        b.append(
            f'<rect class="st" style="animation-delay:{rnd.uniform(0, 2.4):.2f}s" x="{sx}" y="{sy}" '
            f'width="{s}" height="{s}" fill="{t["fg"]}"/>'
        )
    # LEVEL UP!
    lv = "> LEVEL UP! <"
    b.append(f'<g class="lv">{pixel_text(lv, (W - text_width(lv, 4)) // 2, 44, 4, t["fg"])}</g>')
    # name, dropping in letter by letter
    name = "KARTHIK S POOJARY"
    b.append(pixel_text(name, (W - text_width(name, 8)) // 2, 100, 8, t["fg"], "ch", 0.07, 0.3))
    # subtitle
    b.append(
        f'<text class="fd" style="animation-delay:1.6s" x="{W//2}" y="194" text-anchor="middle" '
        f'font-family="{MONO}" font-size="19" letter-spacing="3" fill="{t["mid"]}">'
        "FULL-STACK ENGINEER · DISTRIBUTED SYSTEMS · AI</text>"
    )
    # LV 3 -> LV 4 xp bar
    segs, sw, gap = 30, 14, 4
    bw = segs * (sw + gap) - gap
    bx, by = (W - bw) // 2, 222
    b.append(f'<text x="{bx-16}" y="{by+14}" text-anchor="end" font-family="{MONO}" font-size="16" fill="{t["mid"]}">LV 3</text>')
    b.append(f'<text x="{bx+bw+16}" y="{by+14}" font-family="{MONO}" font-size="16" font-weight="700" fill="{t["fg"]}">LV 4</text>')
    for i in range(segs):
        x = bx + i * (sw + gap)
        b.append(f'<rect x="{x}" y="{by}" width="{sw}" height="18" fill="{t["dim"]}"/>')
        b.append(
            f'<rect class="xp" style="animation-delay:{1.9 + i * 0.05:.2f}s" x="{x}" y="{by}" '
            f'width="{sw}" height="18" fill="{t["fg"]}"/>'
        )
    b.append(
        f'<text class="bl" x="{W//2}" y="278" text-anchor="middle" font-family="{MONO}" '
        f'font-size="16" letter-spacing="4" fill="{t["fg"]}">▶ PRESS START</text>'
    )
    return svg(W, H, "".join(b), style, "Level up — Karthik S Poojary, Full-Stack Engineer")


# --------------------------------------------------------------------------- #
# Stats
# --------------------------------------------------------------------------- #
def stats(t):
    W = 900
    style = (
        "@keyframes on{to{opacity:1}}"
        ".s{opacity:0;animation:on .12s linear forwards}"
        ".v{opacity:0;animation:on .3s ease forwards}"
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
        ".cur{animation:blink 1s steps(1) infinite}"
        "@keyframes hp{0%,100%{opacity:1}50%{opacity:.55}}"
        ".hp{animation:hp 1.6s steps(2) infinite}"
    )
    b = []
    y = 28
    lbl_x, bar_x, val_x = 40, 330, 860
    b.append(f'<text x="{lbl_x}" y="{y+22}" font-family="{MONO}" font-size="20" font-weight="700" fill="{t["fg"]}" letter-spacing="2">◼ BASE STATS</text>')
    b.append(f'<text x="{val_x}" y="{y+22}" text-anchor="end" font-family="{MONO}" font-size="14" fill="{t["mid"]}">LV 4 · FULL-STACK ENGINEER</text>')
    y += 50
    delay = 0.2

    def bar(y, n_on, n_total, sw, gap, h, delay, step, cls="s"):
        parts = []
        for i in range(n_total):
            x = bar_x + i * (sw + gap)
            parts.append(f'<rect x="{x}" y="{y}" width="{sw}" height="{h}" fill="{t["dim"]}"/>')
            if i < n_on:
                parts.append(
                    f'<rect class="{cls}" style="animation-delay:{delay + i * step:.2f}s" x="{x}" y="{y}" '
                    f'width="{sw}" height="{h}" fill="{t["fg"]}"/>'
                )
        return "".join(parts)

    # HP / XP
    for label, sub, on, val in [("HP", "100 / 100", 20, "MAX"), ("XP", "1200+ SOLVED", 16, "80%")]:
        b.append(f'<text x="{lbl_x}" y="{y+15}" font-family="{MONO}" font-size="16" font-weight="700" fill="{t["fg"]}">{label}'
                 f'<tspan font-weight="400" font-size="13" fill="{t["mid"]}">  {sub}</tspan></text>')
        b.append(bar(y, on, 20, 21, 4, 20, delay, 0.03))
        b.append(f'<text class="v" style="animation-delay:{delay + on*0.03:.2f}s" x="{val_x}" y="{y+16}" text-anchor="end" font-family="{MONO}" font-size="14" fill="{t["mid"]}">{val}</text>')
        y += 34
        delay += 0.5
    y += 14
    b.append(f'<rect x="{lbl_x}" y="{y}" width="{val_x-lbl_x}" height="2" fill="{t["dim"]}"/>')
    y += 22

    for group, rows in STATS:
        b.append(f'<text x="{lbl_x}" y="{y+12}" font-family="{MONO}" font-size="13" letter-spacing="3" fill="{t["mid"]}">// {group}</text>')
        y += 26
        for label, val in rows:
            on = round(val / 5)
            b.append(f'<text x="{lbl_x}" y="{y+15}" font-family="{MONO}" font-size="15" fill="{t["fg"]}">{label}</text>')
            b.append(bar(y, on, 20, 21, 4, 20, delay, 0.04))
            b.append(f'<text class="v" style="animation-delay:{delay + on*0.04:.2f}s" x="{val_x}" y="{y+16}" text-anchor="end" font-family="{MONO}" font-size="17" font-weight="700" fill="{t["fg"]}">{val}</text>')
            y += 34
            delay += 0.22
        y += 10
    b.append(f'<text x="{lbl_x}" y="{y+14}" font-family="{MONO}" font-size="13" fill="{t["mid"]}">&gt; stats self-assessed · grinding daily<tspan class="cur" fill="{t["fg"]}"> ▮</tspan></text>')
    H = y + 34
    body = (
        f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>'
        f'<rect x="3" y="3" width="{W-6}" height="{H-6}" fill="none" stroke="{t["fg"]}" stroke-width="4"/>'
        f'<rect x="12" y="12" width="{W-24}" height="{H-24}" fill="none" stroke="{t["dim"]}" stroke-width="1"/>'
        + "".join(b)
    )
    return svg(W, H, body, style, "Base stats")


# --------------------------------------------------------------------------- #
# Quest map rooms
# --------------------------------------------------------------------------- #
CHEST = [
    "  ########  ",
    " #oooooooo# ",
    "#oooooooooo#",
    "############",
    "#oooo##oooo#",
    "#oooo##oooo#",
    "#oooooooooo#",
    "############",
]
SKULL = [
    "  #######  ",
    " #ooooooo# ",
    "#ooooooooo#",
    "#o###o###o#",
    "#o###o###o#",
    "#ooooooooo#",
    "#oooo#oooo#",
    " #ooooooo# ",
    "  #o#o#o#  ",
    "  #######  ",
]


def room(t, idx, r):
    W, H = 300, 280
    wall = 22
    door_y, door_h = 118, 44
    style = (
        "@keyframes fl{0%{opacity:1}33%{opacity:.5}66%{opacity:.85}100%{opacity:1}}"
        ".fl{animation:fl .6s steps(3) infinite}"
        "@keyframes tw{0%,100%{opacity:0}50%{opacity:1}}"
        ".sp{opacity:0;animation:tw 1.8s steps(3) infinite}"
        "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}"
        ".bob{animation:bob 1.2s steps(2) infinite}"
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
        ".bl{animation:blink 1s steps(1) infinite}"
    )
    b = [f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>']
    # brick walls
    bw, bh = 16, 8
    for row in range(H // bh + 1):
        off = 0 if row % 2 == 0 else bw // 2
        for col in range(-1, W // bw + 1):
            x, y = col * bw + off, row * bh
            in_floor = wall <= x + bw and x <= W - wall and wall <= y + bh and y <= H - wall
            if in_floor and wall < x and x + bw < W - wall and wall < y and y + bh < H - wall:
                continue
            b.append(f'<rect x="{x+1}" y="{y+1}" width="{bw-2}" height="{bh-2}" fill="{t["dim"]}"/>')
    # floor with dot grid
    b.append(f'<rect x="{wall}" y="{wall}" width="{W-2*wall}" height="{H-2*wall}" fill="{t["faint"]}" stroke="{t["fg"]}" stroke-width="3"/>')
    for gx in range(wall + 14, W - wall, 18):
        for gy in range(wall + 14, H - wall, 18):
            b.append(f'<rect x="{gx}" y="{gy}" width="2" height="2" fill="{t["dim"]}"/>')
    # doors / corridors to neighbouring rooms (run to the image edge so tiles join up)
    b.append(f'<rect x="0" y="{door_y}" width="{wall+3}" height="{door_h}" fill="{t["faint"]}"/>')
    b.append(f'<rect x="{W-wall-3}" y="{door_y}" width="{wall+3}" height="{door_h}" fill="{t["faint"]}"/>')
    for x0, x1 in [(0, wall), (W - wall, W)]:
        b.append(f'<rect x="{x0}" y="{door_y-3}" width="{x1-x0}" height="3" fill="{t["fg"]}"/>')
        b.append(f'<rect x="{x0}" y="{door_y+door_h}" width="{x1-x0}" height="3" fill="{t["fg"]}"/>')
    # torches
    for tx in (wall + 10, W - wall - 18):
        b.append(f'<rect x="{tx+2}" y="{wall+14}" width="4" height="12" fill="{t["mid"]}"/>')
        b.append(
            f'<g class="fl"><rect x="{tx}" y="{wall+6}" width="8" height="8" fill="{t["fg"]}"/>'
            f'<rect x="{tx+2}" y="{wall+2}" width="4" height="4" fill="{t["fg"]}"/></g>'
        )
    # header
    b.append(f'<text x="{W//2}" y="{wall+20}" text-anchor="middle" font-family="{MONO}" font-size="11" letter-spacing="3" fill="{t["mid"]}">ROOM {r["num"]}</text>')
    b.append(pixel_text(r["name"], (W - text_width(r["name"], 3)) // 2, wall + 30, 3, t["fg"]))
    b.append(f'<text x="{W//2}" y="{wall+70}" text-anchor="middle" font-family="{MONO}" font-size="10" letter-spacing="1.5" fill="{t["mid"]}">{r["tag"]}</text>')
    # centrepiece
    colors = {"#": t["fg"], "o": t["mid"]}
    if r["status"] == "cleared":
        sc = 5
        sx = (W - 12 * sc) // 2
        b.append(sprite(CHEST, sx, 128, sc, colors))
        for i, (px, py) in enumerate([(sx - 14, 124), (sx + 66, 118), (sx + 30, 108)]):
            b.append(
                f'<g class="sp" style="animation-delay:{i*0.6:.1f}s" fill="{t["fg"]}">'
                f'<rect x="{px+3}" y="{py}" width="3" height="9"/><rect x="{px}" y="{py+3}" width="9" height="3"/></g>'
            )
        status = "[ CLEARED ✓ ]"
    else:
        sc = 5
        sx = (W - 11 * sc) // 2
        b.append(f'<g class="bob">{sprite(SKULL, sx, 116, sc, colors)}</g>')
        b.append(f'<g class="bl">{pixel_text("!", sx + 62, 112, 3, t["fg"])}</g>')
        status = "[ BOSS FIGHT ▮ ]"
    b.append(f'<text x="{W//2}" y="{H-wall-36}" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{t["mid"]}">{r["tech"]}</text>')
    b.append(f'<text x="{W//2}" y="{H-wall-16}" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="700" letter-spacing="2" fill="{t["fg"]}">{status}</text>')
    return svg(W, H, "".join(b), style, f"Quest room {r['num']}: {r['name'].title()}")


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, t in THEMES.items():
        files = {f"hero-{name}.svg": hero(t), f"banner-{name}.svg": banner(t), f"stats-{name}.svg": stats(t)}
        for i, r in enumerate(ROOMS, 1):
            files[f"room-{i}-{name}.svg"] = room(t, i, r)
        for fn, content in files.items():
            with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
                f.write(content)
            print("wrote", os.path.normpath(os.path.join(OUT, fn)))


if __name__ == "__main__":
    main()
