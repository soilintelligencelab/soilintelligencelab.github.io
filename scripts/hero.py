"""Soil-profile hero for the Soil Intelligence Lab site (assets/img/hero.svg).
usage: python3 hero.py OUT.svg [seed]
Stdlib only; same seed -> same file."""
import math
import random
import sys

W, H = 1600, 600
OUT = sys.argv[1]
R = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 7)


def n(v):
    s = '%.1f' % v
    if s.endswith('.0'):
        s = s[:-2]
    if s in ('-0', ''):
        return '0'
    if s.startswith('0.'):
        s = s[1:]
    elif s.startswith('-0.'):
        s = '-' + s[2:]
    return s


def pt(p):
    return n(p[0]) + ',' + n(p[1])


def rel(a, b):
    return n(b[0] - a[0]) + ',' + n(b[1] - a[1])


def wave(base, terms):
    """Sum of sines with random phases: terms = [(amplitude, wavelength), ...]."""
    ph = [R.uniform(0, 2 * math.pi) for _ in terms]
    return lambda x: base + sum(a * math.sin(2 * math.pi * x / lam + p) for (a, lam), p in zip(terms, ph))


def catmull(pts, closed=False):
    """Catmull-Rom spline through pts as an SVG path of relative cubic Beziers."""
    # round first so the relative steps do not accumulate rounding error
    pts = [(round(x, 1), round(y, 1)) for x, y in pts]
    P = ([pts[-1]] + pts + [pts[0], pts[1]]) if closed else ([pts[0]] + pts + [pts[-1]])
    d = ['M' + pt(P[1])]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append('c' + rel(p1, c1) + ' ' + rel(p1, c2) + ' ' + rel(p1, p2))
    return ''.join(d) + ('z' if closed else '')


def blob(cx, cy, r, k=7, jit=0.28, rot=None, sx=1.0):
    rot = R.uniform(0, math.pi) if rot is None else rot
    pts = []
    for i in range(k):
        a = 2 * math.pi * i / k + R.uniform(-0.25, 0.25)
        rr = r * (1 + R.uniform(-jit, jit))
        x, y = rr * math.cos(a) * sx, rr * math.sin(a)
        pts.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return pts


def quad(p0, c, p1):
    return 'M' + pt(p0) + 'q' + rel(p0, c) + ' ' + rel(p0, p1)


# ---------------------------------------------------------------- geometry
surf = wave(121, [(4.5, 1700), (2.2, 530), (0.9, 170)])
bOA = wave(150, [(5, 900), (3, 260), (1.5, 90)])
bAB = wave(300, [(11, 1300), (6, 420), (3, 120), (1.6, 45)])
bBC = wave(448, [(14, 1100), (7, 380), (4, 140), (2, 50)])


def line_pts(fn, step=10):
    return [(x, fn(x)) for x in range(-80, W + 81, step)]


def band(fn, bottom=H + 80):
    return catmull(line_pts(fn)) + 'L%d,%dL%d,%dz' % (W + 80, bottom, -80, bottom)


out = []
o = out.append

o('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" preserveAspectRatio="xMidYMid slice" role="img" '
  'aria-label="Illustrated soil profile with grasses, roots, weathered rock and a network of data nodes">' % (W, H))

# ---------------------------------------------------------------- defs
o('<defs>')
o('<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dbe5df"/>'
  '<stop offset=".75" stop-color="#ebeadf"/><stop offset="1" stop-color="#f3ecdd"/></linearGradient>')
o('<radialGradient id="sun" cx="1260" cy="18" r="420" gradientUnits="userSpaceOnUse">'
  '<stop offset="0" stop-color="#fbf1da" stop-opacity=".95"/><stop offset=".45" stop-color="#f6ead2" stop-opacity=".35"/>'
  '<stop offset="1" stop-color="#f3ecdd" stop-opacity="0"/></radialGradient>')
grads = {
    'gO': ((110, 165), [(0, '#2a1c14'), (1, '#33241a')]),
    'gA': ((140, 320), [(0, '#36261b'), (.55, '#47311f'), (1, '#5a3b26')]),
    'gB': ((280, 470), [(0, '#6b4126'), (.5, '#82512f'), (1, '#93603a')]),
    'gC': ((430, 600), [(0, '#a3734b'), (.5, '#b48a62'), (1, '#c4a07a')]),
}
for gid, ((y1, y2), stops) in grads.items():
    o('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="0" y1="%d" x2="0" y2="%d">%s</linearGradient>' % (
        gid, y1, y2, ''.join('<stop offset="%s" stop-color="%s"/>' % (n(t), c) for t, c in stops)))
# rock fills, lit from the upper left
rocks = {
    'rk1': ('#e2cfae', '#b39370', '#8f7154'),   # weathered sandstone
    'rk2': ('#d4bf9f', '#a38667', '#7c6249'),   # saprolite
    'rk3': ('#8d8984', '#5d5955', '#3e3b38'),   # basalt
    'rk4': ('#f2ebde', '#d3c6b1', '#ab9c86'),   # quartz
    'rk5': ('#c9a27d', '#9c6e4a', '#734e33'),   # iron-stained
}
for gid, (c1, c2, c3) in rocks.items():
    o('<linearGradient id="%s" x1=".15" y1=".05" x2=".8" y2="1"><stop offset="0" stop-color="%s"/>'
      '<stop offset=".55" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (gid, c1, c2, c3))
o('<linearGradient id="root" gradientUnits="userSpaceOnUse" x1="0" y1="120" x2="0" y2="560">'
  '<stop offset="0" stop-color="#eadbbd" stop-opacity=".62"/><stop offset=".4" stop-color="#e2cfab" stop-opacity=".42"/>'
  '<stop offset="1" stop-color="#d6bf98" stop-opacity=".2"/></linearGradient>')
o('<radialGradient id="nodeGlow"><stop offset="0" stop-color="#eaffe9" stop-opacity=".9"/>'
  '<stop offset=".35" stop-color="#cdf3d2" stop-opacity=".4"/><stop offset="1" stop-color="#cdf3d2" stop-opacity="0"/></radialGradient>')
o('<clipPath id="soil"><path d="%s"/></clipPath>' % band(surf))
o('<clipPath id="subA"><path d="%s"/></clipPath>' % band(bAB))
FR = 'filterUnits="userSpaceOnUse" x="-100" y="0" width="1800" height="760"'
o('<filter id="soft" %s><feGaussianBlur stdDeviation="3.2"/></filter>' % FR)
o('<filter id="blur5" %s><feGaussianBlur stdDeviation="5"/></filter>' % FR)
# one drop shadow for the whole rock layer
o('<filter id="drop" %s color-interpolation-filters="sRGB"><feGaussianBlur in="SourceAlpha" stdDeviation="1.3"/>'
  '<feOffset dx="1.2" dy="1.8"/><feColorMatrix values="0 0 0 0 .14 0 0 0 0 .09 0 0 0 0 .05 0 0 0 .5 0"/>'
  '<feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>' % FR)


def speckle(fid, freq, octaves, seed, colour, gain, cut, low=False):
    """Noise thresholded into grains: alpha = gain*(R - cut), or gain*(cut - R) for the low tail."""
    r, g, b = (int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    a, c = (-gain, gain * cut) if low else (gain, -gain * cut)
    o('<filter id="%s" filterUnits="userSpaceOnUse" x="0" y="0" width="%d" height="%d" color-interpolation-filters="sRGB">'
      '<feTurbulence type="fractalNoise" baseFrequency="%s" numOctaves="%d" seed="%d"/>'
      '<feColorMatrix values="0 0 0 0 %.3f 0 0 0 0 %.3f 0 0 0 0 %.3f %s 0 0 0 %.3f"/></filter>' % (
          fid, W, H, freq, octaves, seed, r, g, b, n(a), c))


speckle('grainL', '.9', 2, 3, '#f4e6cb', 7, .64)
speckle('grainD', '.9', 2, 3, '#140c07', 7, .36, low=True)
speckle('sandL', '.32', 2, 11, '#f1dfbf', 5, .66)
speckle('sandD', '.32', 2, 11, '#2a1a10', 5, .35, low=True)
speckle('mottleD', '.0045 .014', 4, 5, '#1d120b', 2.6, .5)
speckle('mottleL', '.006 .018', 4, 9, '#d9a777', 2.4, .55)
o('</defs>')

# ---------------------------------------------------------------- sky
o('<rect width="%d" height="%d" fill="url(#sky)"/>' % (W, H))
o('<rect width="%d" height="200" fill="url(#sun)"/>' % W)
far = wave(96, [(10, 900), (6, 330), (2, 90)])
hill = wave(106, [(8, 700), (4, 240), (1.5, 70)])
for fn, col, op in ((far, '#cbd7cd', .75), (hill, '#bdcbbb', .8)):
    o('<path d="%sL%d,160L-80,160z" fill="%s" opacity="%s"/>' % (catmull(line_pts(fn, 16)), W + 80, col, n(op)))
o('<g fill="#adbfac" opacity=".7">')   # distant tree line
x = -10
while x < W + 10:
    if R.random() < 0.42:
        for _ in range(R.randint(2, 6)):
            r = R.uniform(3.5, 8)
            o('<circle cx="%s" cy="%s" r="%s"/>' % (n(x), n(hill(x) - r * 0.7 + R.uniform(-1, 2)), n(r)))
            x += r * R.uniform(0.9, 1.5)
    x += R.uniform(20, 90)
o('</g>')

# ---------------------------------------------------------------- soil body
o('<g clip-path="url(#soil)">')
o('<rect x="-80" y="80" width="%d" height="%d" fill="url(#gO)"/>' % (W + 160, H))
o('<g filter="url(#soft)">')
for fn, gid in ((bOA, 'gA'), (bAB, 'gB'), (bBC, 'gC')):
    o('<path d="%s" fill="url(#%s)"/>' % (band(fn), gid))
o('</g>')
o('<rect width="%d" height="%d" filter="url(#mottleD)" opacity=".35"/>' % (W, H))
o('<rect width="%d" height="%d" filter="url(#mottleL)" opacity=".16" clip-path="url(#subA)"/>' % (W, H))

# B horizon: rusty mottles and grey reduction zones
o('<g filter="url(#blur5)">')
for _ in range(55):
    x = R.uniform(0, W)
    y = R.uniform(bAB(x) + 15, bBC(x) - 5)
    col = R.choice(['#b56a35', '#a85d2c', '#c07a43'])
    o('<path d="%s" fill="%s" opacity="%s"/>' % (catmull(blob(x, y, R.uniform(6, 20), 8, .35, sx=R.uniform(1, 2.2)), True),
                                                 col, n(R.uniform(.18, .38))))
o('</g>')
# B horizon: faint prismatic cracks
o('<g fill="none" stroke="#2f1d12" stroke-linecap="round" opacity=".42">')
for _ in range(34):
    x = R.uniform(0, W)
    y = bAB(x) + R.uniform(4, 30)
    ln = R.uniform(30, 110)
    pts = [(x, y)]
    ang = math.pi / 2 + R.uniform(-.25, .25)
    while ln > 0:
        ang += R.gauss(0, .22) + .15 * (math.pi / 2 - ang)
        x += 8 * math.cos(ang)
        y += 8 * math.sin(ang)
        pts.append((x, y))
        ln -= 8
    o('<path d="%s" stroke-width="%s"/>' % (catmull(pts), n(R.uniform(.5, 1.1))))
o('</g>')

# sand and silt grains
o('<rect width="%d" height="%d" filter="url(#grainD)" opacity=".55"/>' % (W, H))
o('<rect width="%d" height="%d" filter="url(#grainL)" opacity=".42"/>' % (W, H))
o('<g clip-path="url(#subA)">')
o('<rect width="%d" height="%d" filter="url(#sandD)" opacity=".35"/>' % (W, H))
o('<rect width="%d" height="%d" filter="url(#sandL)" opacity=".45"/>' % (W, H))
o('</g>')

# A horizon: crumb aggregates with a lit upper edge
agg_cols = ['#4b3425', '#553b28', '#3a281c', '#5f4330', '#2f2017']
small, big = {c: [] for c in agg_cols}, {c: [] for c in agg_cols}
lit = []
for _ in range(800):
    x = R.uniform(-5, W + 5)
    top, bot = bOA(x) - 22, bAB(x) - 6
    y = top + (bot - top) * (R.random() ** 1.3)
    r = R.uniform(1.3, 4.6) * (1.15 if y < 200 else 1)
    col = R.choice(agg_cols)
    if r < 2.4:
        small[col].append('M%sh%s' % (pt((x - r * .5, y)), n(r)))
    else:
        big[col].append(catmull(blob(x, y, r, 5, .3), True))
        lit.append(quad((x - r * .7, y - r * .05), (x - r * .55, y - r * .7), (x + r * .15, y - r * .7)))
o('<g opacity=".8">')
for c in agg_cols:
    o('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linecap="round"/>' % (''.join(small[c]), c))
    o('<path d="%s" fill="%s"/>' % (''.join(big[c]), c))
o('</g>')
o('<path d="%s" fill="none" stroke="#c49a74" stroke-width=".8" stroke-linecap="round" opacity=".3"/>' % ''.join(lit))
# pores
o('<path d="%s" fill="none" stroke="#120b07" stroke-linecap="round" opacity=".4"/>' % ''.join(
    'M%sh%s' % (pt((x, y)), n(R.uniform(.6, 2.2))) for x, y in
    ((x, R.uniform(bOA(x) - 15, bBC(x) + 60)) for x in (R.uniform(0, W) for _ in range(260)))))
# B horizon: iron-manganese nodules
nod, shine = [], []
for _ in range(120):
    x = R.uniform(0, W)
    y = R.uniform(bAB(x) + 8, bBC(x) + 10)
    r = R.uniform(.9, 2.6)
    nod.append('<circle cx="%s" cy="%s" r="%s"/>' % (n(x), n(y), n(r)))
    if r > 1.6:
        shine.append('<circle cx="%s" cy="%s" r="%s"/>' % (n(x - r * .35), n(y - r * .35), n(r * .35)))
o('<g fill="#2a1a12" opacity=".8">%s</g>' % ''.join(nod))
o('<g fill="#d9b48c" opacity=".35">%s</g>' % ''.join(shine))

# ---------------------------------------------------------------- rocks
placed = []


def free(x, y, r, pad=2):
    return all((x - a) ** 2 + (y - b) ** 2 > (r + c + pad) ** 2 for a, b, c in placed)


rock_items = []
for _ in range(14000):
    x = R.uniform(-20, W + 20)
    y = R.uniform(bAB(x) + 25, H + 25)
    if y < bBC(x) - 10:
        if R.random() > 0.006:
            continue
        r = R.uniform(1.8, 4.5)
    else:
        depth = max(0, (y - bBC(x) + 10) / (H - bBC(x) + 10))
        if R.random() > 0.03 + 0.5 * depth ** 1.8:
            continue
        r = R.uniform(2.2, 5.5) + depth ** 1.5 * R.uniform(3, 28)
    if not free(x, y, r, 3 + r * .25):
        continue
    placed.append((x, y, r))
    rock_items.append((x, y, r, R.choices(['rk1', 'rk2', 'rk3', 'rk4', 'rk5'], [4, 3, 2.4, .8, 1.4])[0]))

by_kind = {k: [] for k in rocks}
for x, y, r, kind in rock_items:
    k = R.randint(7, 10) if r > 9 else R.randint(5, 7)
    by_kind[kind].append(catmull(blob(x, y, r, k, .2, sx=R.uniform(1, 1.55)), True))
o('<g filter="url(#drop)" stroke-width=".6" stroke-opacity=".45">')
for kind, ds in by_kind.items():
    o('<path d="%s" fill="url(#%s)" stroke="%s"/>' % (''.join(ds), kind, '#2b2826' if kind == 'rk3' else '#6b5039'))
o('</g>')
# mineral grains in basalt, rim light on the larger fragments
spk = []
rim = []
for x, y, r, kind in rock_items:
    if kind == 'rk3' and r > 5:
        for _ in range(int(r * 1.1)):
            a, rr = R.uniform(0, 2 * math.pi), r * .7 * math.sqrt(R.random())
            spk.append('M%sh.1' % pt((x + rr * math.cos(a), y + rr * math.sin(a) * .8)))
    if r > 5:
        rim.append(quad((x - r * .85, y + r * .05), (x - r * .8, y - r * .75), (x + r * .1, y - r * .82)))
o('<path d="%s" stroke="#e4ddd0" stroke-width="1.1" stroke-linecap="round" opacity=".55"/>' % ''.join(spk))
o('<path d="%s" fill="none" stroke="#fff6e6" stroke-width=".9" stroke-linecap="round" opacity=".32"/>' % ''.join(rim))
o('</g>')  # soil clip

# ---------------------------------------------------------------- plants and their roots
# Every root system belongs to a plant drawn above it: bunchgrasses have fibrous roots, forbs and
# clover have taproots (clover with nitrogen-fixing nodules). The turf in between has a shallow root mat.
FIBROUS = dict(wander=.17, grav=.045, branch=.06, lat_w=(.45, .7), lat_a=(.55, 1.2), lat_l=(.35, .7))
TAP = dict(wander=.07, grav=.12, branch=.2, lat_w=(.35, .5), lat_a=(.95, 1.45), lat_l=(.22, .45), taper=1.15)
root_paths, fine_paths, hairs, tips, nodules = [], [], [], [], []


def grow(x, y, ang, w, length, level, spec, nod=False):
    pts, ws = [(x, y)], [w]
    steps = max(3, int(length / 4))
    for i in range(1, steps + 1):
        if level == 0:
            ang += R.gauss(0, spec['wander']) + spec['grav'] * (math.pi / 2 - ang)
        else:
            ang += R.gauss(0, .22) + .035 * (math.pi / 2 - ang)
        x += 4 * math.cos(ang)
        y += 4 * math.sin(ang)
        if y > H + 10:
            break
        pts.append((x, y))
        ws.append(max(.25, w * (1 - i / steps) ** (spec.get('taper', .75) if level == 0 else .75)))
        if nod and level == 1 and i > 2 and y < surf(x) + 110 and R.random() < .3:
            nodules.append((x, y, R.uniform(1, 1.9)))
        if level < 2 and 3 < i < steps - 3 and R.random() < (spec['branch'] if level == 0 else .05):
            side = R.choice((-1, 1))
            frac = R.uniform(*spec['lat_l']) if level == 0 else R.uniform(.35, .7)
            grow(x, y, ang + side * R.uniform(*spec['lat_a']), ws[-1] * R.uniform(*spec['lat_w']),
                 (steps - i) * 4 * frac, level + 1, spec, nod)
    if len(pts) < 3:
        return
    tips.append((pts[-1], level))
    keep = list(range(0, len(pts), 3))
    if keep[-1] != len(pts) - 1:
        keep.append(len(pts) - 1)
    if w < .7:
        fine_paths.append(catmull([pts[j] for j in keep]))
    else:
        L, Rr = [], []
        for j in keep:
            a, b = pts[max(0, j - 1)], pts[min(len(pts) - 1, j + 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            m = math.hypot(dx, dy) or 1
            h = ws[j] / 2
            L.append((pts[j][0] - dy / m * h, pts[j][1] + dx / m * h))
            Rr.append((pts[j][0] + dy / m * h, pts[j][1] - dx / m * h))
        root_paths.append(catmull(L) + 'L' + catmull(Rr[::-1])[1:] + 'z')
    for p in (pts[-6:-1] if pts[-1][1] < bAB(pts[-1][0]) + 20 else []):
        a, ln = R.uniform(0, 2 * math.pi), R.uniform(1.5, 3.5)
        hairs.append('M%sl%s,%s' % (pt(p), n(ln * math.cos(a)), n(ln * math.sin(a))))


plants = []
x = R.uniform(25, 60)
while x < W - 10:
    plants.append((x, R.choices(['bunch', 'forb', 'clover'], [5, 3, 2])[0], R.uniform(.75, 1.2)))
    x += R.uniform(85, 165)
for px, kind, s in plants:
    y0 = surf(px) + 1
    if kind == 'bunch':
        for _ in range(int(8 * s) + R.randint(0, 3)):
            grow(px + R.uniform(-6, 6), y0, math.pi / 2 + R.uniform(-1.05, 1.05), R.uniform(1.1, 1.6) * s,
                 R.uniform(140, 250) * s, 0, FIBROUS)
    else:
        tap = kind == 'forb'
        grow(px, y0, math.pi / 2 + R.gauss(0, .08), (2.8 if tap else 2.2) * s,
             (R.uniform(240, 320) if tap else R.uniform(150, 210)) * s, 0, TAP, nod=not tap)
        for _ in range(R.randint(2, 3)):   # shallow side roots from the crown
            grow(px + R.uniform(-3, 3), y0, math.pi / 2 + R.choice((-1, 1)) * R.uniform(.7, 1.2), .6,
                 R.uniform(30, 60), 1, TAP)

mat = []   # turf root mat
x = 0
while x < W:
    for _ in range(R.randint(1, 2)):
        px, py, a = x + R.uniform(-4, 4), surf(x) + 1, math.pi / 2 + R.uniform(-.9, .9)
        pts = [(px, py)]
        for _ in range(R.randint(4, 11)):
            a += R.gauss(0, .3) + .1 * (math.pi / 2 - a)
            px, py = px + 4 * math.cos(a), py + 4 * math.sin(a)
            pts.append((px, py))
        mat.append(catmull(pts))
    x += R.uniform(7, 14)

hyphae = []   # mycorrhizal hyphae from root tips in the topsoil
for (tx, ty), lv in tips:
    if ty > bAB(tx) + 10 or R.random() > .45:
        continue
    for _ in range(R.randint(1, 2)):
        a = R.uniform(0, 2 * math.pi)
        seg = ['M' + pt((tx, ty))]
        for _ in range(R.randint(6, 16)):
            a += R.gauss(0, .55)
            seg.append('l%s,%s' % (n(3 * math.cos(a)), n(3 * math.sin(a))))
        hyphae.append(''.join(seg))

# roots are kept quiet: the root gradient fades them with depth
o('<path d="%s" fill="none" stroke="#e9dcc0" stroke-width=".4" opacity=".16"/>' % ''.join(mat))
o('<path d="%s" fill="none" stroke="#efe6d4" stroke-width=".3" stroke-linecap="round" opacity=".22"/>' % ''.join(hyphae))
o('<path d="%s" fill="none" stroke="url(#root)" stroke-width=".45" stroke-linecap="round"/>' % ''.join(fine_paths))
o('<path d="%s" fill="url(#root)"/>' % ''.join(root_paths))
o('<path d="%s" fill="none" stroke="#efe3cb" stroke-width=".25" opacity=".22"/>' % ''.join(hairs))
o('<g fill="#d8b49c" opacity=".55">%s</g>' % ''.join(
    '<circle cx="%s" cy="%s" r="%s"/>' % (n(x), n(y), n(r)) for x, y, r in nodules))

# ---------------------------------------------------------------- data network
def clear_of_rocks(p):
    return all(math.hypot(p[0] - a, p[1] - b) > c + 7 for a, b, c in placed)


cands = [p for p, lv in tips if 180 < p[1] < 470 and 10 < p[0] < W - 10 and lv <= 1]
for _ in range(400):
    x = R.uniform(10, W - 10)
    y = R.uniform(bBC(x) + 5, 560)
    cands.append((x, y))
R.shuffle(cands)
nodes = []
for p in cands:
    if clear_of_rocks(p) and all(math.hypot(p[0] - q[0], p[1] - q[1]) > 88 for q in nodes):
        nodes.append(p)
edges = set()
for i, p in enumerate(nodes):
    near = sorted(range(len(nodes)), key=lambda j: math.hypot(p[0] - nodes[j][0], p[1] - nodes[j][1]))[1:4]
    for j in (near[:2] if R.random() < .55 else near):
        if math.hypot(p[0] - nodes[j][0], p[1] - nodes[j][1]) < 230:
            edges.add((min(i, j), max(i, j)))
solid, dashed, packets = [], [], []
for i, j in sorted(edges):
    a, b = nodes[i], nodes[j]
    dx, dy = b[0] - a[0], b[1] - a[1]
    m = math.hypot(dx, dy)
    bend = R.uniform(-.12, .12) * m
    c = ((a[0] + b[0]) / 2 - dy / m * bend, (a[1] + b[1]) / 2 + dx / m * bend)
    (dashed if R.random() < .28 else solid).append(quad(a, c, b))
    for _ in range(R.randint(0, 2)):
        t = R.uniform(.15, .85)
        packets.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0],
                        (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1]))
o('<g fill="none" stroke-linecap="round">')
o('<path d="%s" stroke="#140d08" stroke-width="3" opacity=".2"/>' % ''.join(solid))
o('<path d="%s" stroke="#e2f8e3" stroke-width="1.25" opacity=".78"/>' % ''.join(solid))
o('<path d="%s" stroke="#e2f8e3" stroke-width="1" stroke-dasharray="1.8 3.4" opacity=".7"/>' % ''.join(dashed))
o('</g>')
o('<path d="%s" stroke="#f4fff2" stroke-width="2.4" stroke-linecap="round" opacity=".85"/>' % ''.join(
    'M%sh.1' % pt(p) for p in packets))
hubs = set(R.sample(range(len(nodes)), max(1, len(nodes) // 6)))
glow, halo, ring, core = [], [], [], []
for i, (x, y) in enumerate(nodes):
    hub = i in hubs
    glow.append('<circle cx="%s" cy="%s" r="%d"/>' % (n(x), n(y), 20 if hub else 13))
    if hub:
        halo.append('<circle cx="%s" cy="%s" r="12"/>' % (n(x), n(y)))
    ring.append('<circle cx="%s" cy="%s" r="%s"/>' % (n(x), n(y), '6' if hub else '4.2'))
    core.append('<circle cx="%s" cy="%s" r="%s"/>' % (n(x), n(y), '2.4' if hub else '1.8'))
o('<g fill="url(#nodeGlow)">%s</g>' % ''.join(glow))
o('<g fill="none" stroke="#e2f8e3" stroke-width=".6" stroke-dasharray="2 2.5" opacity=".55">%s</g>' % ''.join(halo))
o('<g fill="#1d2a20" fill-opacity=".55" stroke="#ecfcec" stroke-width="1.1">%s</g>' % ''.join(ring))
o('<g fill="#f7fff5">%s</g>' % ''.join(core))

# ---------------------------------------------------------------- surface: litter, turf, plants
litter = {}
for _ in range(380):
    x = R.uniform(-5, W + 5)
    y = surf(x) + R.uniform(-1.5, 6)
    ln = R.uniform(3, 9)
    a = R.uniform(-.35, .35)
    wd = ln * R.uniform(.25, .4)
    c, s = math.cos(a), math.sin(a)
    p0, p1 = (x - ln / 2 * c, y - ln / 2 * s), (x + ln / 2 * c, y + ln / 2 * s)
    q1, q2 = (x - wd * s, y + wd * c), (x + wd * s, y - wd * c)
    col = R.choice(['#8a6a3a', '#7a4a2a', '#5a4a2e', '#9a7a45', '#6b3f22', '#4b3b24'])
    litter.setdefault(col, []).append('M%sQ%s %sQ%s %sz' % (pt(p0), pt(q1), pt(p1), pt(q2), pt(p0)))
o('<g opacity=".85">%s</g>' % ''.join('<path d="%s" fill="%s"/>' % (''.join(v), k) for k, v in litter.items()))


def blade(bx, by, h, lean, w):
    b0 = (bx - w / 2, by)
    tip = (bx + math.sin(lean) * h * 1.15, by - math.cos(lean) * h)
    ctl = (bx + math.sin(lean) * h * .25, by - h * .62)
    return 'M%sq%s %sq%s %sz' % (pt(b0), rel(b0, (ctl[0] - w * .3, ctl[1])), rel(b0, tip),
                                 rel(tip, (ctl[0] + w * .3, ctl[1])), rel(tip, (bx + w / 2, by)))


def leaf(p, ang, ln, wd):
    tip = (p[0] + ln * math.cos(ang), p[1] + ln * math.sin(ang))
    m = (p[0] + ln * .45 * math.cos(ang), p[1] + ln * .45 * math.sin(ang))
    nx, ny = -math.sin(ang) * wd, math.cos(ang) * wd
    return 'M%sq%s %sq%s %sz' % (pt(p), rel(p, (m[0] + nx, m[1] + ny)), rel(p, tip),
                                 rel(tip, (m[0] - nx, m[1] - ny)), rel(tip, p))


def bez(p0, c, p1, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1])


def group(d, fmt):
    return ''.join(fmt % (''.join(v), k) for k, v in d.items() if v)


def blades(gap, hmin, hmax, cols, op, wmax):
    by_col = {c: [] for c in cols}
    x = -6
    while x < W + 6:
        for _ in range(R.randint(4, 10)):
            bx = x + R.uniform(-5, 5)
            h = R.uniform(hmin, hmax) * (1.3 if R.random() < .1 else 1)
            by_col[R.choice(cols)].append(blade(bx, surf(bx) + R.uniform(.5, 2.5), h, R.gauss(0, .32), R.uniform(.9, wmax)))
        x += R.uniform(gap * .6, gap * 1.3)
    o('<g opacity="%s">%s</g>' % (n(op), group(by_col, '<path d="%s" fill="%s"/>')))


blades(13, 9, 24, ['#9fb08e', '#aab794', '#b6bb93', '#98ab88'], .9, 1.8)
blades(8, 8, 20, ['#6f8b57', '#7c975f', '#5f7a4b', '#86a067', '#9aa46f'], 1, 2.2)

tuft, leaves, stems, heads, flowers, florets, clover_heads = {}, {}, [], [], [], {}, []
for px, kind, s in plants:
    by = surf(px) + 1
    if kind == 'bunch':
        for _ in range(int(28 * s)):
            off = R.uniform(-7, 7) * s
            tuft.setdefault(R.choice(['#5f7a4b', '#6f8b57', '#7c975f', '#56713f', '#8a9a62', '#a39b66']), []).append(
                blade(px + off, surf(px + off) + 1.5, R.uniform(.45, 1) * 56 * s, off / 7 * .55 + R.gauss(0, .2), R.uniform(1.2, 2.2)))
        oat = R.random() < .5
        for _ in range(R.randint(2, 4)):
            sx = px + R.uniform(-4, 4)
            h = R.uniform(62, 96) * s
            lean = R.gauss(0, .14)
            top = (sx + math.sin(lean) * h, by - h)
            ctl = (sx + R.uniform(-4, 4), by - h * .55)
            stems.append(quad((sx, by), ctl, top))
            heads.append(((sx, by), ctl, top, oat))
    elif kind == 'forb':   # yarrow-like: leafy stem, flat cluster of small flowers
        h = R.uniform(58, 82) * s
        top = (px + R.gauss(0, 4), by - h)
        ctl = (px + R.uniform(-3, 3), by - h * .5)
        stems.append(quad((px, by), ctl, top))
        for k in range(R.randint(4, 6)):
            side = 1 if k % 2 else -1
            leaves.setdefault(R.choice(['#6d8a55', '#5e7a49', '#7a9660']), []).append(
                leaf(bez((px, by), ctl, top, .12 + k * .12), -math.pi / 2 + side * R.uniform(.75, 1), (21 - k * 2.4) * s, 3.4 * s))
        for _ in range(R.randint(5, 7)):   # basal rosette
            leaves.setdefault(R.choice(['#5e7a49', '#56713f']), []).append(
                leaf((px, by - 1), -math.pi / 2 + R.choice((-1, 1)) * R.uniform(.45, 1.05), R.uniform(18, 27) * s, 3.8 * s))
        for _ in range(R.randint(5, 7)):
            a = -math.pi / 2 + R.uniform(-.8, .8)
            ln = R.uniform(5, 11) * s
            end = (top[0] + math.cos(a) * ln * 1.2, top[1] + math.sin(a) * ln * .55)
            flowers.append(quad(top, (top[0], end[1] + 2), end))
            col = R.choice(['#f3ecdc', '#ece2c4', '#f6f0e4'])
            for _ in range(R.randint(8, 12)):
                florets.setdefault(col, []).append('M%sh.1' % pt((end[0] + R.uniform(-4.2, 4.2) * s, end[1] + R.uniform(-1.8, 1.2) * s)))
    else:                  # clover: trifoliate leaves, round flower heads
        for _ in range(R.randint(8, 12)):
            off = R.uniform(-16, 16) * s
            top = (px + off, by - R.uniform(13, 26) * s)
            stems.append(quad((px + off * .3, by), (px + off * .5, top[1] + 4), top))
            for j in range(3):
                a = -math.pi / 2 + (j - 1) * 2.1 + R.uniform(-.15, .15)
                leaves.setdefault(R.choice(['#5d7d4a', '#668652', '#557443']), []).append(
                    leaf(top, a, 8 * s, 3.4 * s))
        for _ in range(R.randint(2, 4)):
            off = R.uniform(-12, 12) * s
            top = (px + off, by - R.uniform(28, 38) * s)
            stems.append(quad((px + off * .3, by), (px + off * .6, top[1] + 8), top))
            clover_heads.append((top, 4.6 * s))

o('<path d="%s" fill="none" stroke="#6f8251" stroke-width=".9" stroke-linecap="round"/>' % ''.join(stems))
o(group(leaves, '<path d="%s" fill="%s"/>'))
o(group(tuft, '<path d="%s" fill="%s"/>'))
awns, spikes = [], {}
for p0, ctl, top, oat in heads:
    for k in range(R.randint(9, 15)):
        px, py = bez(p0, ctl, top, 1 - k * .045)
        side = 1 if k % 2 else -1
        if oat:   # drooping spikelets on short pedicels
            ln = R.uniform(3.5, 5.5)
            e = (px + side * ln * .55, py + ln * .5)
            awns.append(quad((px, py), (px + side * ln * .5, py - .5), e))
            spikes.setdefault('#b7aa76', []).append((e[0], e[1] + 1.4, -side * 18))
        else:     # upright spike
            spikes.setdefault(R.choice(['#a99d67', '#b3a675', '#9c9461']), []).append((px + side * 1.2, py, side * 28))
o('<path d="%s" fill="none" stroke="#8d9061" stroke-width=".5"/>' % ''.join(awns))
for col, es in spikes.items():
    o('<g fill="%s">%s</g>' % (col, ''.join('<ellipse cx="%s" cy="%s" rx="1.1" ry="2.5" transform="rotate(%s %s %s)"/>' % (
        n(x), n(y), n(a), n(x), n(y)) for x, y, a in es)))
o('<path d="%s" fill="none" stroke="#7d8d5c" stroke-width=".55"/>' % ''.join(flowers))
o(group(florets, '<path d="%s" stroke="%s" stroke-width="2.1" stroke-linecap="round"/>'))
o('<g fill="#d9aab3">%s</g>' % ''.join('<circle cx="%s" cy="%s" r="%s"/>' % (n(p[0]), n(p[1]), n(r)) for p, r in clover_heads))
o('<path d="%s" stroke="#f1dde0" stroke-width="1.3" stroke-linecap="round" opacity=".85"/>' % ''.join(
    'M%sh.1' % pt((p[0] + r * .7 * math.cos(a), p[1] + r * .7 * math.sin(a))) for p, r in clover_heads
    for a in [R.uniform(0, 2 * math.pi) for _ in range(12)]))
blades(11, 5, 13, ['#4f6a3e', '#587548', '#486338', '#64804c', '#a69c69'], 1, 2.4)
o('</svg>')

with open(OUT, 'w') as f:
    f.write('\n'.join(out) + '\n')
print(OUT, sum(len(s) + 1 for s in out), 'bytes;', len(nodes), 'nodes,', len(rock_items), 'rocks,',
      len(root_paths) + len(fine_paths), 'roots')
