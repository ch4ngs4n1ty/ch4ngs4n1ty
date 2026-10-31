"""Builds the animated GitHub profile banner: a pixel-art bonsai under a night sky.

The animation is plain CSS inside the SVG (GitHub plays it in READMEs; no
scripts). The tree is drawn on a 4px grid and every color becomes one <path>,
so the file stays small. Same seed, same tree, whichever theme.

    python3 assets/make_banner.py                  # red and black -> banner.svg
    python3 assets/make_banner.py --theme autumn   # fall colors   -> banner-autumn.svg
"""
import math
import random
import sys
from pathlib import Path

S = 4                      # px per pixel-art cell
W, H = 960, 320            # banner size in px
rnd = random.Random(27)

THEMES = {
    # crimson leaves, black wood and lacquer, a blood moon
    'red': {
        'file': 'banner.svg', 'tree': 'crimson',
        'sky': ('#020202', '#0b0304'), 'nebula': (('#b3141f', .2), ('#7a0a12', .14)),
        'leaf': ['#2b0508', '#520a10', '#820f18', '#b5141f', '#e02a2f', '#ff5a52'],
        'bark': {'light': '#4a1a1c', 'base': '#1d1414', 'dark': '#0a0707', 'streak': '#2c1c1c'},
        'pot': {'rim': '#3a1416', 'lip': '#070505', 'lit': '#1f1515', 'mid': '#141010',
                'dark': '#0a0808', 'foot': '#040303', 'band': '#c0141e'},
        'moss': ['#140909', '#261012', '#3d1316'], 'pebble': '#2e2424',
        'stars': ['#f2efe9', '#ff6b6b', '#d8cfcb', '#ff3b3b'], 'sparkle': '#ffe9e6',
        'moon': ('#ff4d4d', '#a3161f'), 'moonglow': ('#ff2a2a', .3),
        'line': '#e0242c', 'node': '#ff3b3b', 'embers': ['#ff3b30', '#ff6b4a', '#d4141e'],
        'floor': '#1a0707', 'name_first': '#f2efe9', 'name': ('#ff6a5a', '#ff3b3b', '#b3141f'),
        'rule': '#e0242c', 'border': ('#b3141f', .45), 'ink': '#f2efe9', 'ink_dim': '#9c8f8f',
    },
    # the first version: red maple in fall, gold moon
    'autumn': {
        'file': 'banner-autumn.svg', 'tree': 'red maple',
        'sky': ('#060507', '#140a08'), 'nebula': (('#c0392b', .16), ('#c9a84c', .07)),
        'leaf': ['#4f1513', '#7e2420', '#b23428', '#d9532c', '#ee8a35', '#f4c463'],
        'bark': {'light': '#8c5b3b', 'base': '#613d29', 'dark': '#3d2418', 'streak': '#2e1b12'},
        'pot': {'rim': '#7d4a36', 'lip': '#24140f', 'lit': '#4a2b23', 'mid': '#3a211c',
                'dark': '#26161a', 'foot': '#1a0f0e', 'band': '#c9a84c'},
        'moss': ['#33482a', '#4b6634', '#67853f'], 'pebble': '#8a7d6c',
        'stars': ['#f2efe9', '#f0c060', '#f6d7b0', '#e8a07a'], 'sparkle': '#fff3d6',
        'moon': ('#f6e2b0', '#d9bf86'), 'moonglow': ('#f6e2b0', .35),
        'line': '#c9a84c', 'node': '#f0c060', 'embers': ['#f0c060', '#ee8a35', '#ffd58a'],
        'floor': '#2a1712', 'name_first': 'url(#name)', 'name': ('#e74c3c', '#e8823f', '#f0c060'),
        'rule': '#c9a84c', 'border': ('#c9a84c', .28), 'ink': '#f2efe9', 'ink_dim': '#a39c91',
    },
}
theme_name = sys.argv[sys.argv.index('--theme') + 1] if '--theme' in sys.argv else 'red'
T = THEMES[theme_name]
LEAF, BARK, POT, MOSS = T['leaf'], T['bark'], T['pot'], T['moss']


def to_paths(cells, extra=''):
    """cells: {(x, y): color} on the grid -> one run-length <path> per color."""
    by_color = {}
    for (x, y), color in cells.items():
        by_color.setdefault(color, {}).setdefault(y, []).append(x)
    out = []
    for color, rows in by_color.items():
        d = []
        for y in sorted(rows):
            xs = sorted(rows[y])
            start = prev = xs[0]
            for x in xs[1:] + [None]:
                if x is not None and x == prev + 1:
                    prev = x
                    continue
                d.append(f'M{start * S} {y * S}h{(prev - start + 1) * S}v{S}h-{(prev - start + 1) * S}z')
                if x is not None:
                    start = prev = x
        out.append(f'<path fill="{color}" d="{"".join(d)}"{extra}/>')
    return ''.join(out)


# ── pot, soil, moss ─────────────────────────────────────────────────────────
pot = {}
for x in range(40, 85):
    pot[(x, 62)] = POT['rim']
for x in range(41, 84):
    pot[(x, 63)] = POT['lip']
for i, y in enumerate(range(64, 72)):
    left, right = 42 + i // 2, 82 - i // 2
    for x in range(left, right + 1):
        t = (x - left) / (right - left)
        dither = (x + y) % 2
        if t < 0.28 or (t < 0.36 and dither):
            pot[(x, y)] = POT['lit']
        elif t > 0.74 or (t > 0.66 and dither):
            pot[(x, y)] = POT['dark']
        else:
            pot[(x, y)] = POT['mid']
for x in range(43, 82):                        # worn band around the pot
    if rnd.random() > 0.05:
        pot[(x, 66)] = POT['band']
for x in range(46, 79):
    pot[(x, 72)] = POT['dark']
for x in list(range(47, 52)) + list(range(73, 78)):
    for y in (73, 74):
        pot[(x, y)] = POT['foot']
for x in range(42, 83):                        # moss and soil just inside the rim
    pot[(x, 61)] = MOSS[rnd.choice([0, 1, 1, 2])]
    if rnd.random() < 0.45 and 44 < x < 80:
        pot[(x, 60)] = MOSS[rnd.choice([1, 2])]
for x in (48, 71, 76):                         # pebbles
    pot[(x, 61)] = T['pebble']

# ── trunk and branches: stamped discs, shaded after ──────────────────────────
wood = set()


def stroke(points):
    """points: [(x, y, radius), ...] in cells; stamps discs along the polyline."""
    for (x0, y0, r0), (x1, y1, r1) in zip(points, points[1:]):
        steps = int(math.hypot(x1 - x0, y1 - y0) * 3) + 1
        for k in range(steps + 1):
            t = k / steps
            cx, cy, r = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r0 + (r1 - r0) * t
            for gx in range(int(cx - r - 1), int(cx + r + 2)):
                for gy in range(int(cy - r - 1), int(cy + r + 2)):
                    if (gx + 0.5 - cx) ** 2 + (gy + 0.5 - cy) ** 2 <= r * r:
                        wood.add((gx, gy))


stroke([(61, 61, 4.2), (59, 57, 3.6), (57, 52, 3.2), (59, 47, 2.8), (62, 42, 2.5),
        (61, 37, 2.1), (59, 33, 1.8), (61, 28, 1.5), (63, 23, 1.2)])
stroke([(58, 50, 1.8), (52, 47, 1.5), (45, 45, 1.2), (38, 43, 1.0)])     # left, low
stroke([(61, 43, 1.8), (67, 40, 1.5), (74, 37, 1.2), (81, 34, 1.0)])     # right
stroke([(60, 34, 1.4), (55, 31, 1.1), (49, 29, 0.9)])                    # left, high
stroke([(54, 60, 1.0), (58, 59, 2.0), (65, 59, 2.0), (70, 60, 1.0)])     # root flare
wood = {c for c in wood if c[1] <= 61}

trunk = {}
for (x, y) in wood:
    if (x - 1, y) not in wood:
        trunk[(x, y)] = BARK['light']
    elif (x + 1, y) not in wood:
        trunk[(x, y)] = BARK['dark']
    elif rnd.random() < 0.14:
        trunk[(x, y)] = BARK['streak']
    else:
        trunk[(x, y)] = BARK['base']

# ── foliage pads (each pad sways on its own) ─────────────────────────────────
PADS = [
    # anchor (branch tip the pad pivots on), sub-blobs (cx, cy, rx, ry)
    {'anchor': (63, 23), 'blobs': [(63, 17, 11, 5.5), (55, 20, 7, 4), (71, 20, 7, 4), (59, 13, 6, 3), (67, 13, 5, 3)]},
    {'anchor': (49, 29), 'blobs': [(48, 25, 9, 4.5), (41, 27, 6, 3.5), (56, 27, 6, 3.5), (46, 21, 5, 3)]},
    {'anchor': (81, 34), 'blobs': [(81, 30, 10, 5), (74, 32, 6, 3.5), (88, 32, 6, 3.5), (83, 26, 6, 3)]},
    {'anchor': (38, 43), 'blobs': [(37, 39, 10, 5), (30, 41, 6, 3.5), (44, 41, 6, 3.5), (35, 35, 6, 3)]},
    {'anchor': (67, 40), 'blobs': [(69, 36, 5, 2.5), (65, 37, 4, 2)]},
    {'anchor': (52, 47), 'blobs': [(49, 44, 5, 2.5), (53, 45, 3, 1.5)]},
]


def shade(light):
    if light > 0.95:
        return LEAF[5]
    if light > 0.55:
        return LEAF[4]
    if light > 0.15:
        return LEAF[3]
    if light > -0.25:
        return LEAF[2]
    if light > -0.6:
        return LEAF[1]
    return LEAF[0]


pad_cells = []
for pad in PADS:
    cells = {}
    for (cx, cy, rx, ry) in pad['blobs']:
        for gx in range(int(cx - rx - 2), int(cx + rx + 3)):
            for gy in range(int(cy - ry - 2), int(cy + ry + 3)):
                dx, dy = (gx + 0.5 - cx) / rx, (gy + 0.5 - cy) / (ry * (0.75 if gy > cy else 1))
                if dx * dx + dy * dy > 1 + rnd.uniform(-0.3, 0.12):
                    continue
                light = -0.35 * dx - 0.85 * dy + rnd.uniform(-0.35, 0.35)
                color = shade(light)
                if rnd.random() < 0.04:
                    color = LEAF[5]                        # stray sunlit leaves
                if (gx, gy) not in cells or LEAF.index(color) > LEAF.index(cells[(gx, gy)]):
                    cells[(gx, gy)] = color
    # moonlit top edges, dark undersides: gives each pad some volume
    for (gx, gy) in list(cells):
        if (gx, gy - 1) not in cells and rnd.random() < 0.65:
            cells[(gx, gy)] = LEAF[5] if rnd.random() < 0.4 else LEAF[4]
        elif (gx, gy + 1) not in cells and rnd.random() < 0.75:
            cells[(gx, gy)] = LEAF[0]
    pad_cells.append(cells)

# ── sky: stars, moon, constellation, shooting star ──────────────────────────
stars = []
for _ in range(78):
    x, y = rnd.uniform(14, W - 14), rnd.uniform(10, 236)
    if 470 < x < 930 and 125 < y < 245:        # keep the text area clear
        continue
    size = 4 if rnd.random() < 0.22 else 2
    stars.append((round(x), round(y), size, rnd.uniform(2.2, 6.5), rnd.uniform(-6, 0),
                  rnd.choice(T['stars'])))

MOON = (888, 64)
CONSTELLATION = [(488, 74), (538, 46), (586, 82), (640, 54), (694, 88), (742, 60), (792, 98)]

# ── moving bits: falling leaves and rising embers ───────────────────────────
leaves = []
for i in range(18):
    pad = rnd.choice(PADS)
    cx, cy, rx, ry = rnd.choice(pad['blobs'])
    x0, y0 = (cx + rnd.uniform(-rx, rx) * 0.8) * S, (cy + rnd.uniform(-ry, ry * 0.5)) * S
    fall = rnd.uniform(296, 314) - y0
    drift = rnd.uniform(-90, 60)
    leaves.append({'x': round(x0), 'y': round(y0), 'fall': round(fall), 'drift': round(drift),
                   'sway': rnd.uniform(14, 30), 'dur': rnd.uniform(9, 15), 'delay': rnd.uniform(-15, 0),
                   'color': rnd.choice([LEAF[2], LEAF[3], LEAF[3], LEAF[4], LEAF[5]]),
                   'shape': rnd.choice(['h', 'v', 'dot'])})

embers = []
for i in range(11):
    embers.append({'x': round(rnd.uniform(150, 360)), 'y': round(rnd.uniform(230, 290)),
                   'rise': round(rnd.uniform(110, 210)), 'drift': round(rnd.uniform(-40, 40)),
                   'dur': rnd.uniform(6, 11), 'delay': rnd.uniform(-11, 0),
                   'color': rnd.choice(T['embers'])})

# ── assemble ────────────────────────────────────────────────────────────────
css = [f"""
.tw{{animation:twinkle var(--d) ease-in-out var(--o) infinite}}
@keyframes twinkle{{0%,100%{{opacity:.25}}50%{{opacity:1}}}}
.pad{{transform-box:view-box;animation:sway var(--d) ease-in-out var(--o) infinite alternate}}
@keyframes sway{{from{{transform:rotate(-1.4deg)}}to{{transform:rotate(1.4deg)}}}}
.edge{{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 13s ease-in-out var(--o) infinite}}
@keyframes draw{{0%{{stroke-dashoffset:1;opacity:1}}14%{{stroke-dashoffset:0}}78%{{stroke-dashoffset:0;opacity:1}}90%,100%{{stroke-dashoffset:0;opacity:0}}}}
.node{{animation:node 13s ease-in-out var(--o) infinite}}
@keyframes node{{0%,4%{{opacity:.15}}12%{{opacity:1}}78%{{opacity:1}}90%,100%{{opacity:.15}}}}
.shoot{{animation:shoot 11s linear 2s infinite;opacity:0}}
@keyframes shoot{{0%{{transform:translate(0,0);opacity:0}}1%{{opacity:1}}7%{{transform:translate(-260px,110px);opacity:0}}100%{{transform:translate(-260px,110px);opacity:0}}}}
.moonglow{{animation:glow 7s ease-in-out infinite alternate}}
@keyframes glow{{from{{opacity:.55}}to{{opacity:.9}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.leaf,.ember,.shoot{{display:none}}.edge{{stroke-dashoffset:0}}}}
"""]

for i, lf in enumerate(leaves):
    f, d, s = lf['fall'], lf['drift'], lf['sway']
    css.append(
        f"@keyframes l{i}{{0%{{transform:translate(0,0);opacity:0}}6%{{opacity:1}}"
        f"25%{{transform:translate({d * .25 + s:.0f}px,{f * .25:.0f}px)}}"
        f"50%{{transform:translate({d * .5 - s:.0f}px,{f * .5:.0f}px)}}"
        f"75%{{transform:translate({d * .75 + s:.0f}px,{f * .75:.0f}px)}}"
        f"90%{{transform:translate({d:.0f}px,{f:.0f}px);opacity:1}}"
        f"100%{{transform:translate({d:.0f}px,{f:.0f}px);opacity:0}}}}"
        f".l{i}{{animation:l{i} {lf['dur']:.1f}s ease-in-out {lf['delay']:.1f}s infinite}}")
for i, em in enumerate(embers):
    css.append(
        f"@keyframes e{i}{{0%{{transform:translate(0,0);opacity:0}}15%{{opacity:.95}}"
        f"60%{{opacity:.7}}100%{{transform:translate({em['drift']}px,-{em['rise']}px);opacity:0}}}}"
        f".e{i}{{animation:e{i} {em['dur']:.1f}s ease-out {em['delay']:.1f}s infinite}}")

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'role="img" aria-labelledby="t d">',
       '<title id="t">Ethan Chang</title>',
       f'<desc id="d">Pixel-art {T["tree"]} bonsai under a night sky, with falling leaves, rising embers, '
       'twinkling stars and a constellation drawing itself beside the name Ethan Chang.</desc>',
       f'<style>{"".join(css)}</style>',
       '<defs>',
       f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{T["sky"][0]}"/>'
       f'<stop offset="1" stop-color="{T["sky"][1]}"/></linearGradient>',
       *[f'<radialGradient id="neb{i + 1}" cx="{cx}" cy="{cy}" r="{r}"><stop offset="0" stop-color="{c}" '
         f'stop-opacity="{o}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
         for i, ((c, o), (cx, cy, r)) in enumerate(zip(T['nebula'], [('.28', '.55', '.45'), ('.72', '.25', '.4')]))],
       f'<radialGradient id="moonglow"><stop offset="0" stop-color="{T["moonglow"][0]}" stop-opacity="{T["moonglow"][1]}"/>'
       f'<stop offset="1" stop-color="{T["moonglow"][0]}" stop-opacity="0"/></radialGradient>',
       '<radialGradient id="shadow"><stop offset="0" stop-color="#000" stop-opacity=".7"/>'
       '<stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>',
       f'<linearGradient id="floor" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{T["floor"]}" stop-opacity="0"/>'
       f'<stop offset=".25" stop-color="{T["floor"]}" stop-opacity=".9"/><stop offset=".75" stop-color="{T["floor"]}" stop-opacity=".9"/>'
       f'<stop offset="1" stop-color="{T["floor"]}" stop-opacity="0"/></linearGradient>',
       f'<linearGradient id="name" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{T["name"][0]}"/>'
       f'<stop offset=".5" stop-color="{T["name"][1]}"/><stop offset="1" stop-color="{T["name"][2]}"/></linearGradient>',
       f'<linearGradient id="streak" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{T["sparkle"]}"/>'
       f'<stop offset="1" stop-color="{T["sparkle"]}" stop-opacity="0"/></linearGradient>',
       '<filter id="soft" x="-1" y="-1" width="3" height="3"><feGaussianBlur stdDeviation="1.6"/></filter>',
       f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="14"/></clipPath>',
       '</defs>',
       '<g clip-path="url(#frame)">',
       f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
       f'<rect width="{W}" height="{H}" fill="url(#neb1)"/>',
       f'<rect width="{W}" height="{H}" fill="url(#neb2)"/>']

# stars
svg.append('<g>')
for (x, y, size, dur, off, color) in stars:
    svg.append(f'<rect class="tw" x="{x}" y="{y}" width="{size}" height="{size}" fill="{color}" '
               f'style="--d:{dur:.1f}s;--o:{off:.1f}s"/>')
for (x, y) in [(120, 34), (410, 22), (842, 158)]:          # a few bigger cross-shaped stars
    svg.append(f'<g class="tw" style="--d:4.8s;--o:-{(x % 5):.0f}s" fill="{T["sparkle"]}">'
               f'<rect x="{x}" y="{y - 4}" width="2" height="10"/><rect x="{x - 4}" y="{y}" width="10" height="2"/></g>')
svg.append('</g>')

# moon: pixel crescent with a soft halo
mx, my = MOON
svg.append(f'<circle class="moonglow" cx="{mx}" cy="{my}" r="58" fill="url(#moonglow)"/>')
moon = {}
for gx in range(-8, 9):
    for gy in range(-8, 9):
        inside = gx * gx + gy * gy <= 56
        bite = (gx + 4) ** 2 + (gy - 2) ** 2 <= 46
        if inside and not bite:
            moon[(gx + mx // S, gy + my // S)] = T['moon'][0] if gx > 2 else T['moon'][1]
svg.append(to_paths(moon, ' shape-rendering="crispEdges"'))

# constellation that draws itself, edge by edge
svg.append(f'<g stroke="{T["line"]}" stroke-width="1.2" stroke-opacity=".6" fill="none">')
for i, ((x0, y0), (x1, y1)) in enumerate(zip(CONSTELLATION, CONSTELLATION[1:])):
    svg.append(f'<path class="edge" pathLength="1" d="M{x0} {y0}L{x1} {y1}" style="--o:{i * 0.55:.2f}s"/>')
svg.append('</g>')
for i, (x, y) in enumerate(CONSTELLATION):
    o = max(0, i - 1) * 0.55
    svg.append(f'<g class="node" style="--o:{o:.2f}s"><circle cx="{x}" cy="{y}" r="5" fill="{T["node"]}" '
               f'opacity=".35" filter="url(#soft)"/><rect x="{x - 2}" y="{y - 2}" width="4" height="4" fill="{T["sparkle"]}"/></g>')

# shooting star
# bright head at the lower-left end, so it leads the motion
svg.append('<g class="shoot"><path d="M630 52 L700 22" stroke="url(#streak)" stroke-width="2" '
           'stroke-linecap="round"/></g>')

# floor, shadow, embers behind the tree
svg.append('<rect x="20" y="298" width="470" height="22" fill="url(#floor)"/>')
svg.append('<ellipse cx="250" cy="300" rx="118" ry="10" fill="url(#shadow)"/>')
for i, em in enumerate(embers):
    svg.append(f'<g class="ember e{i}"><circle cx="{em["x"]}" cy="{em["y"]}" r="4" fill="{em["color"]}" '
               f'opacity=".5" filter="url(#soft)"/><rect x="{em["x"] - 1}" y="{em["y"] - 1}" width="3" height="3" '
               f'fill="{em["color"]}"/></g>')

# the tree: pot and trunk fixed, pads sway around their branch tips
svg.append(f'<g shape-rendering="crispEdges">{to_paths(pot)}{to_paths(trunk)}')
for i, (pad, cells) in enumerate(zip(PADS, pad_cells)):
    ax, ay = pad['anchor']
    svg.append(f'<g class="pad" style="transform-origin:{ax * S}px {ay * S}px;--d:{4.6 + i * 0.9:.1f}s;'
               f'--o:-{i * 1.3:.1f}s">{to_paths(cells)}</g>')
svg.append('</g>')

# falling leaves, in front of the tree
for i, lf in enumerate(leaves):
    x, y, c = lf['x'], lf['y'], lf['color']
    if lf['shape'] == 'h':
        body = f'<rect x="{x}" y="{y}" width="6" height="3" fill="{c}"/>'
    elif lf['shape'] == 'v':
        body = f'<rect x="{x}" y="{y}" width="3" height="6" fill="{c}"/>'
    else:
        body = f'<rect x="{x}" y="{y}" width="4" height="4" fill="{c}"/>'
    svg.append(f'<g class="leaf l{i}">{body}</g>')

# name and subtitle
svg.append('<g font-family="Georgia, \'Times New Roman\', serif">'
           '<text x="486" y="186" font-size="58" font-weight="700" letter-spacing="-0.5">'
           f'<tspan fill="{T["name_first"]}">Ethan </tspan><tspan fill="url(#name)">Chang</tspan></text>'
           f'<rect x="488" y="204" width="56" height="2" fill="{T["rule"]}"/>'
           f'<text x="488" y="238" font-size="18" font-style="italic" fill="{T["ink"]}" fill-opacity=".9">'
           'Software engineering and data science</text>'
           '</g>'
           '<text x="488" y="270" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
           f'font-size="12" letter-spacing="1.8" fill="{T["ink_dim"]}">CS @ RIT · CLASS OF 2027 · R&amp;D INTERN @ SANDIA</text>')

svg.append('</g>')
svg.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="13.5" fill="none" '
           f'stroke="{T["border"][0]}" stroke-opacity="{T["border"][1]}"/>')
svg.append('</svg>')

out = Path(__file__).with_name(T['file'])
out.write_text('\n'.join(svg) + '\n')
print(f'wrote {out} ({out.stat().st_size / 1024:.1f} KB)')
