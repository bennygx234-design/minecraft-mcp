# Light-rail guideway generator. exec()'d inside a build script with origin (0,0,0) => builder coords = world.
# Expects globals: b, world_block, math.  Set SELECT = [line names] before exec.
import math

# ---------------------------------------------------------------- network (world coords, y = rider feet)
LINES = {
    # name: (points, style, extra)
    'LR1': ([(-43.5, 73, 84), (-43.5, 86, 60), (-43.5, 86, -30), (20, 86, -78), (83, 86, -88),
             (83, 78, -95), (83, 75, -97)], 'main', dict(skip_s=7.5, portal=[('z', 33, 85, 2.0)],
                                                         road_portal=[('z', -99, -86.5, 5.0)])),
    'LR2': ([(83, 86, -88), (130, 86, -92), (145, 78, -108), (145, 69, -122)], 'main', dict(skip_s=2.5)),
    'HAN': ([(-43.5, 73, 84), (-43.5, 80, 40), (4, 74, 10), (4, 64, 5)], 'spur', dict()),
    'CAR': ([(-43.5, 73, 270), (-43.5, 82, 285), (-10, 82, 280), (-10, 70, 278), (-10, 64, 278)], 'spur', dict()),
}
PRIORITY = {'HAN': 0, 'CAR': 0, 'LR1': 1, 'LR2': 2}
STEEP = 1.8             # segments steeper than this get no deck (lift shaft instead)

# never place anything in these boxes (x1,x2,z1,z2)
NOGO = [
    (54, 112, -148, -98),     # manor
    (-40, -15, 264, 291),     # FedEx cargo warehouse (cargo spur passes through it)
    (-40, 40, -40, 1),        # hangar block (deck flies over the roof: handled by REPLACEABLE check)
]
NOGO_DECK_OK = {1, 2}            # index into NOGO where deck-level blocks are fine if the cell is air

REPLACEABLE = {'air', 'cave_air', 'short_grass', 'tall_grass', 'fern', 'large_fern', 'dead_bush', 'vine',
               'snow', 'leaf_litter', 'short_dry_grass', 'tall_dry_grass', 'bush', 'firefly_bush', 'poppy',
               'dandelion', 'cornflower', 'oxeye_daisy', 'azure_bluet', 'allium', 'sunflower', 'lilac',
               'rose_bush', 'peony', 'sugar_cane', 'sweet_berry_bush', 'pink_petals', 'wildflowers'}
WATERISH = {'water', 'seagrass', 'tall_seagrass', 'kelp', 'kelp_plant', 'bubble_column'}
NATURAL_BASE = {'grass_block', 'dirt', 'coarse_dirt', 'podzol', 'rooted_dirt', 'mud', 'sand', 'red_sand',
                'sandstone', 'stone', 'gravel', 'clay', 'andesite', 'diorite', 'granite', 'deepslate', 'tuff',
                'moss_block', 'mycelium', 'suspicious_sand', 'suspicious_gravel', 'calcite', 'dripstone_block'}

def bname(x, y, z):
    w = world_block(x, y, z) or 'minecraft:air'
    return w.replace('minecraft:', '').split('[')[0]

def is_leafy(n):
    return n.endswith('_leaves') or n in REPLACEABLE or n.endswith('_sapling') or n.endswith('_tulip') or \
        n.endswith('flower') or n == 'mangrove_propagule'

def free(n):
    return is_leafy(n)

def nogo(x, z, deck=False):
    for i, (x1, x2, z1, z2) in enumerate(NOGO):
        if x1 <= x <= x2 and z1 <= z <= z2:
            if deck and i in NOGO_DECK_OK:
                continue
            return True
    return False

# ---------------------------------------------------------------- geometry
def segs(name):
    pts = LINES[name][0]
    out, s0 = [], 0.0
    for i in range(len(pts) - 1):
        (x1, y1, z1), (x2, y2, z2) = pts[i], pts[i + 1]
        L = math.hypot(x2 - x1, z2 - z1)
        out.append(dict(i=i, a=(x1, y1, z1), b=(x2, y2, z2), L=L, s0=s0,
                        steep=abs(y2 - y1) / max(L, 1e-6) > STEEP))
        s0 += L
    return out, s0

def at_s(name, s):
    sg, tot = segs(name)
    s = max(0, min(tot, s))
    for g in sg:
        if s <= g['s0'] + g['L'] + 1e-9:
            t = (s - g['s0']) / max(g['L'], 1e-9)
            (x1, y1, z1), (x2, y2, z2) = g['a'], g['b']
            dx, dz = (x2 - x1) / max(g['L'], 1e-9), (z2 - z1) / max(g['L'], 1e-9)
            return x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, z1 + (z2 - z1) * t, dx, dz, g
    g = sg[-1]
    return g['b'][0], g['b'][1], g['b'][2], 0, 0, g

def claims_for(name):
    """cell -> (d, h, s, seg) nearest point of this line"""
    sg, tot = segs(name)
    cl = {}
    for g in sg:
        (x1, y1, z1), (x2, y2, z2) = g['a'], g['b']
        xa, xb = int(math.floor(min(x1, x2) - 3)), int(math.floor(max(x1, x2) + 3))
        za, zb = int(math.floor(min(z1, z2) - 3)), int(math.floor(max(z1, z2) + 3))
        L = g['L']
        for x in range(xa, xb + 1):
            for z in range(za, zb + 1):
                cx, cz = x + 0.5, z + 0.5
                if L < 1e-9:
                    t = 0
                else:
                    t = ((cx - x1) * (x2 - x1) + (cz - z1) * (z2 - z1)) / (L * L)
                    t = max(0.0, min(1.0, t))
                px, pz = x1 + (x2 - x1) * t, z1 + (z2 - z1) * t
                d = math.hypot(cx - px, cz - pz)
                if d > 2.6:
                    continue
                h = y1 + (y2 - y1) * t
                s = g['s0'] + t * L
                old = cl.get((x, z))
                if old is None or d < old[0] - 1e-9:
                    cl[(x, z)] = (d, h, s, g)
    return cl, tot

def path_cells(name):
    """ordered 4-connected centre path"""
    sg, tot = segs(name)
    out = []
    n = int(tot / 0.1) + 1
    for k in range(n + 1):
        x, y, z, dx, dz, g = at_s(name, k * 0.1)
        c = (int(math.floor(x)), int(math.floor(z)))
        if out and c == out[-1]:
            continue
        if out:
            px, pz = out[-1]
            if c[0] != px and c[1] != pz:
                # insert the intermediate cell closer to the line
                cand = [(c[0], pz), (px, c[1])]
                def dd(cc):
                    return math.hypot(cc[0] + 0.5 - x, cc[1] + 0.5 - z)
                out.append(min(cand, key=dd))
        if c not in out[-3:]:
            out.append(c)
    return out

def q2(h):
    return math.floor(h * 2 + 0.5) / 2.0

# ---------------------------------------------------------------- resolution across lines
ALL = {}
for nm in LINES:
    cl, tot = claims_for(nm)
    skip = LINES[nm][2].get('skip_s', 0)
    for c, (d, h, s, g) in cl.items():
        if s < skip or g['steep']:
            continue
        if s > tot - 0.01 and d > 0.5 and False:
            continue
        ALL.setdefault(c, []).append((nm, d, h, s, g))

def winners(c):
    """claims surviving at cell c (stacked claims at different heights all survive)"""
    lst = ALL.get(c, [])
    out = []
    for cl in sorted(lst, key=lambda r: (r[1], PRIORITY[r[0]])):
        nm, d, h, s, g = cl
        style = LINES[nm][1]
        kind = 'deck' if d <= 1.6 else 'rail'
        if style == 'spur' and kind == 'rail':
            continue
        clash = False
        for o in out:
            if abs(o[2] - h) < 4.0:
                clash = True
                break
        if not clash:
            out.append(cl)
    return out

# ---------------------------------------------------------------- emitter
PLAN = {}            # (x,y,z) -> block (later writes win unless protected)

def plan(x, y, z, blk, deck=True, force=False):
    if nogo(x, z, deck=deck):
        return
    if not force:
        n = bname(x, y, z)
        if not free(n):
            return
    PLAN[(x, y, z)] = blk

MAT = {
    'main': dict(deck='smooth_quartz', slab='smooth_quartz_slab[type=bottom]', mid='light_gray_concrete',
                 midslab='smooth_stone_slab[type=bottom]', edge='smooth_quartz', fascia='light_gray_concrete',
                 rail='light_gray_stained_glass_pane', beam='light_gray_concrete'),
    'spur': dict(deck='light_gray_concrete', slab='smooth_stone_slab[type=bottom]', mid='light_gray_concrete',
                 midslab='smooth_stone_slab[type=bottom]', edge='light_gray_concrete', fascia='light_gray_concrete',
                 rail='iron_bars', beam='light_gray_concrete'),
}

def emit_line(nm):
    pts, style, extra = LINES[nm]
    M = MAT[style]
    path = path_cells(nm)
    pset = set(path)
    cl, tot = claims_for(nm)
    skip = extra.get('skip_s', 0)
    top_of = {}        # cell -> (q, fl) for this line, for rails/pillars
    railing = {}       # (x,y,z) -> True  (pane cells)
    for c, lst in ALL.items():
        for w in winners(c):
            if w[0] != nm:
                continue
            _, d, h, s, g = w
            x, z = c
            q = q2(h)
            fl = int(math.floor(q))
            half = q != fl
            kind = 'deck' if d <= 1.6 else 'rail'
            if kind == 'deck':
                mid = c in pset
                if half:
                    plan(x, fl - 1, z, M['mid'] if mid else M['deck'])
                    plan(x, fl, z, M['midslab'] if mid else M['slab'])
                else:
                    plan(x, fl - 1, z, M['mid'] if mid else M['deck'])
                topfull = fl - 1
                if mid:
                    plan(x, topfull - 1, z, M['beam'])
                top_of[c] = (q, topfull)
                # clear leaves in the rider envelope
                for yy in range(int(math.ceil(q)), int(math.ceil(q)) + 3):
                    n = bname(x, yy, z)
                    if n != 'air' and is_leafy(n) and not nogo(x, z):
                        PLAN[(x, yy, z)] = 'air'
                if style == 'spur' and d >= 0.95 and not mid:
                    ry = int(math.ceil(q))
                    if half:
                        plan(x, fl, z, M['edge'])
                    railing[(x, ry, z)] = True
            else:
                ry = int(math.ceil(q))
                plan(x, ry - 1, z, M['edge'])
                plan(x, ry - 2, z, M['fascia'])
                railing[(x, ry, z)] = True
    # lights every 10 along the line: the railing cell nearest each side point
    lights = set()
    s = 5.0
    while s < tot - 1:
        x, y, z, dx, dz, g = at_s(nm, s)
        if not g['steep'] and s >= skip:
            nx, nz = -dz, dx
            off = 2.1 if style == 'main' else 1.0
            for sd in (1, -1):
                tx, tz = x + nx * off * sd, z + nz * off * sd
                best = None
                for (rx, ry, rz) in railing:
                    dd = math.hypot(rx + 0.5 - tx, rz + 0.5 - tz)
                    if dd < 1.2 and (best is None or dd < best[0]):
                        best = (dd, (rx, ry, rz))
                if best:
                    lights.add(best[1])
        s += 10.0
    # panes with connection states
    for (x, y, z) in railing:
        if (x, y, z) in lights:
            plan(x, y, z, 'sea_lantern')
            continue
        st = []
        for dn, (ddx, ddz) in (('north', (0, -1)), ('south', (0, 1)), ('east', (1, 0)), ('west', (-1, 0))):
            if (x + ddx, y, z + ddz) in railing:
                st.append(dn + '=true')
        blk = M['rail'] + ('[' + ','.join(st) + ']' if st else '')
        plan(x, y, z, blk)
    # rails on flat centre cells
    for i, c in enumerate(path):
        if c not in top_of:
            continue
        q, topfull = top_of[c]
        if q != int(q):
            continue
        nb = []
        for j in (i - 1, i + 1):
            if 0 <= j < len(path) and path[j] in top_of and top_of[path[j]][0] == q:
                nb.append(path[j])
        if len(nb) == 0:
            continue
        dirs = set()
        for (nx_, nz_) in nb:
            ddx, ddz = nx_ - c[0], nz_ - c[1]
            dirs.add({(0, -1): 'north', (0, 1): 'south', (1, 0): 'east', (-1, 0): 'west'}[(ddx, ddz)])
        if len(dirs) == 1:
            dn = dirs.pop()
            shape = 'north_south' if dn in ('north', 'south') else 'east_west'
        elif dirs in ({'north', 'south'},):
            shape = 'north_south'
        elif dirs == {'east', 'west'}:
            shape = 'east_west'
        else:
            a = 'north' if 'north' in dirs else 'south'
            bb = 'east' if 'east' in dirs else 'west'
            shape = a + '_' + bb
        plan(c[0], int(q), c[1], 'rail[shape=%s]' % shape)
    return top_of, path

# ---------------------------------------------------------------- pillars
def column_ok(x, z, ytop):
    """scan down from ytop; returns base y (solid natural block) or None"""
    y = ytop
    while y > -10:
        n = bname(x, y, z)
        if free(n) or n in WATERISH:
            y -= 1
            continue
        return y, n
    return None

def pillar_line(nm, top_of, path, spacing=9.0, start=4.0):
    pts, style, extra = LINES[nm]
    sg, tot = segs(name=nm) if False else segs(nm)
    skip = extra.get('skip_s', 0)
    portals = extra.get('portal', [])
    road_portals = extra.get('road_portal', [])
    s = max(start, skip + 2)
    placed = []
    while s < tot - 2.5:
        done = False
        for shift in (0, 1, -1, 2, -2, 3, -3, 4, -4):
            ss = s + shift
            x, y, z, dx, dz, g = at_s(nm, ss)
            if g['steep']:
                continue
            c = (int(math.floor(x)), int(math.floor(z)))
            if c not in top_of:
                continue
            q, topfull = top_of[c]
            ptop = topfull - 2
            nx, nz = -dz, dx
            mode, off = 'single', 0
            for (ax, a1, a2, o) in portals:
                v = z if ax == 'z' else x
                if a1 <= v <= a2:
                    mode, off = 'portal', o
            for (ax, a1, a2, o) in road_portals:
                v = z if ax == 'z' else x
                if a1 <= v <= a2:
                    mode, off = 'portal', o
            if mode == 'single':
                legs = [c]
            else:
                legs = [(int(math.floor(x + nx * off * sd)), int(math.floor(z + nz * off * sd))) for sd in (1, -1)]
            ok = True
            bases = []
            for (lx, lz) in legs:
                if nogo(lx, lz):
                    ok = False; break
                r = column_ok(lx, lz, ptop)
                if r is None:
                    ok = False; break
                by, bn = r
                if bn not in NATURAL_BASE and not (bn in ('smooth_sandstone', 'cut_sandstone') and lx > 120) and not (nm == 'CAR' and bn == 'smooth_stone'):
                    ok = False; break
                if ptop - by < 2:
                    ok = False; break
                bases.append(by)
            if not ok:
                continue
            for (lx, lz), by in zip(legs, bases):
                for yy in range(by + 1, ptop + 1):
                    plan(lx, yy, lz, 'light_gray_concrete', deck=False)
                plan(lx, ptop + 1, lz, 'light_gray_concrete')
            if mode == 'single':
                # T-head under the deck
                for sd in (1, -1):
                    hx, hz = int(math.floor(x + nx * 1.2 * sd)), int(math.floor(z + nz * 1.2 * sd))
                    plan(hx, topfull - 1, hz, 'light_gray_concrete')
                plan(c[0], ptop, c[1], 'polished_andesite')
            else:
                # crossbeam between the legs at beam level
                steps = int(off * 2 * 3) + 1
                for k in range(steps + 1):
                    f = -off + 2 * off * k / steps
                    hx, hz = int(math.floor(x + nx * f)), int(math.floor(z + nz * f))
                    plan(hx, topfull - 1, hz, 'light_gray_concrete')
            placed.append((round(ss, 1), c, mode))
            done = True
            break
        s += spacing
    return placed

def flush():
    for (x, y, z), blk in PLAN.items():
        b.set(x, y, z, blk)
