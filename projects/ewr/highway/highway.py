# Newark airport <-> city highway. World coordinates (build origin 0,0,0).
# PART: 1 = inside airport strip (z >= -42), 2 = west/bridge (z < -42, x < 0), 3 = east (x >= 0, z < -42)
PART = globals().get('PART', 0)
R = 14.0
A1, A2, A3, A4, A5 = 121.0, 121.0 + R * math.pi / 2, 0, 0, 0
A2 = A1 + R * math.pi / 2          # end arc1
A3 = A2 + 114.0                    # end S2 (x -45..69)
A4 = A3 + R * math.pi / 2          # end arc2
A5 = A4 + 23.0                     # end S3 (z -74..-97)
L = int(A5)

def center(a):
    """centre point and unit right-normal at along a"""
    if a <= A1:
        return (-59.0, 75.0 - a), (1.0, 0.0)
    if a <= A2:
        th = math.pi + (a - A1) / R
        cx, cz = -45.0, -46.0
        px, pz = cx + R * math.cos(th), cz + R * math.sin(th)
        return (px, pz), ((cx - px) / R, (cz - pz) / R)
    if a <= A3:
        return (-45.0 + (a - A2), -60.0), (0.0, 1.0)
    if a <= A4:
        th = math.pi / 2 - (a - A3) / R
        cx, cz = 69.0, -74.0
        px, pz = cx + R * math.cos(th), cz + R * math.sin(th)
        return (px, pz), ((px - cx) / R, (pz - cz) / R)
    return (83.0, -74.0 - (a - A4)), (1.0, 0.0)

def locate(x, z):
    best = None
    c = []
    if -46 <= z <= 75: c.append((75 - z, x + 59))
    dx, dz = x + 45, z + 46
    th = math.atan2(dz, dx)
    if th < 0: th += 2 * math.pi
    if math.pi <= th <= 1.5 * math.pi:
        c.append((A1 + R * (th - math.pi), R - math.hypot(dx, dz)))
    if -45 <= x <= 69: c.append((A2 + x + 45, z + 60))
    dx, dz = x - 69, z + 74
    th = math.atan2(dz, dx)
    if 0 <= th <= math.pi / 2:
        c.append((A3 + R * (math.pi / 2 - th), math.hypot(dx, dz) - R))
    if -97 <= z <= -74: c.append((A4 + (-74 - z), x - 83))
    for a, lat in c:
        if best is None or abs(lat) < abs(best[1]): best = (a, lat)
    return best

def in_airport(x, z):
    return -82 <= x <= 129 and -42 <= z <= 324

def allowed(x, z):
    if in_airport(x, z):
        return -62 <= x <= -56 and z <= 75
    if 54 <= x <= 112 and -148 <= z <= -98: return False
    if 124 <= x <= 216 and -181 <= z <= -89: return False
    return True

def in_part(x, z):
    if PART == 0: return True
    if PART == 1: return z >= -42
    if PART == 2: return z < -42 and x < 0
    return z < -42 and x >= 0

def put(x, y, z, blk):
    x, z = int(x), int(z)
    if allowed(x, z) and in_part(x, z):
        b.set(x, y, z, blk)

def iswater(x, z, g):
    w = world_block(x, g + 1, z) or ''
    return 'water' in w

# ---- profile ----
st = []
for a in range(L + 1):
    (px, pz), (nx, nz) = center(a)
    gs, wet = [], False
    for lat in (-3, 0, 3):
        cx, cz = int(round(px + nx * lat)), int(round(pz + nz * lat))
        g = ground(cx, cz)
        gs.append(g)
        if iswater(cx, cz, g): wet = True
    gs.sort()
    st.append((gs[1], wet, pz >= -42))
tgt = []
for i, (gm, wet, ap) in enumerate(st):
    if ap: tgt.append(63)
    elif wet: tgt.append(67)
    else:
        win = sorted(st[j][0] for j in range(max(0, i - 3), min(L, i + 3) + 1) if not st[j][1] and not st[j][2])
        tgt.append(max(63, win[len(win) // 2]))
hh = []
for i in range(L + 1):
    hh.append(max(2 * tgt[j] - abs(i - j) for j in range(max(0, i - 40), min(L, i + 40) + 1)))
bridge = []
for i in range(L + 1):
    gm, wet, ap = st[i]
    nearwet = any(st[j][1] for j in range(max(0, i - 2), min(L, i + 2) + 1))
    bridge.append((nearwet or (hh[i] // 2 - gm) >= 6) and not ap)
print('profile', ''.join('B' if bridge[i] else '.' for i in range(0, L + 1, 2)))
print('heights', [hh[i] / 2 for i in range(0, L + 1, 10)])

GANTRY_A = 97     # z = -22 inside the strip
GANTRY_C = 290    # z = -85 near the manor gate
lamp_cells = {}

# ---- road cells ----
for x in range(-66, 92):
    for z in range(-98, 77):
        r = locate(x, z)
        if r is None: continue
        a, lat = r
        li = int(round(lat))
        if abs(lat) > 4.5 or a < 0 or a > A5: continue
        if in_airport(x, z) and abs(li) > 3: continue
        ai = min(L, max(0, int(round(a))))
        v = hh[ai]; H = v // 2; half = v % 2
        top = H + half
        g = ground(x, z)
        br = bridge[ai]
        # surface
        if li == 0:
            full, slab = 'yellow_concrete', 'smooth_sandstone_slab[type=bottom]'
        elif abs(li) == 3 and (int(a) // 3) % 2 == 0:
            full, slab = 'white_concrete', 'smooth_quartz_slab[type=bottom]'
        elif abs(li) == 4:
            full, slab = 'smooth_stone', 'smooth_stone_slab[type=bottom]'
        else:
            full, slab = 'gray_concrete', 'polished_deepslate_slab[type=bottom]'
        if half:
            put(x, H, z, 'gray_concrete' if full != 'smooth_stone' else 'smooth_stone')
            put(x, H + 1, z, slab)
        else:
            put(x, H, z, full)
        # clear above
        for y in range(top + 1, max(top + 8, g + 1)):
            put(x, y, z, 'air')
        # below
        if br:
            put(x, H - 1, z, 'light_gray_concrete')
            if ai % 12 in (0, 1) and abs(li) in (2, 3):
                for y in range(g + 1, H - 1):
                    put(x, y, z, 'stone_bricks')
            if abs(li) == 4:
                put(x, top + 1, z, 'andesite_wall')
        else:
            for y in range(g + 1, H):
                put(x, y, z, 'stone_bricks' if (abs(li) == 4 or in_airport(x, z)) else 'dirt')
        lamp_cells[(x, z)] = (a, li, top)

# ---- lamps every 16 (staggered sides) ----
for a in range(8, L, 16):
    if abs(a - GANTRY_A) < 5 or abs(a - GANTRY_C) < 5: continue
    side = 1 if (a // 16) % 2 == 0 else -1
    (px, pz), (nx, nz) = center(a)
    ap = pz >= -42
    off = 3 if ap else 4
    x, z = int(round(px + nx * off * side)), int(round(pz + nz * off * side))
    ix, iz = int(round(px + nx * (off - 1) * side)), int(round(pz + nz * (off - 1) * side))
    v = hh[a]; top = v // 2 + v % 2
    for y in range(top + 1, top + 5): put(x, y, z, 'andesite_wall')
    put(x, top + 5, z, 'smooth_stone')
    put(ix, top + 5, iz, 'smooth_stone_slab[type=bottom]')
    put(ix, top + 4, iz, 'lantern[hanging=true]')
    put(x, top + 6, z, 'smooth_stone_slab[type=bottom]')

# ---- sign gantries ----
def gantry(a, w, face, back, lines_face, lines_back):
    (px, pz), (nx, nz) = center(a)
    v = hh[a]; top = v // 2 + v % 2
    px, pz = int(round(px)), int(round(pz))
    for y in range(top + 1, top + 8):
        put(px - w, y, pz, 'light_gray_concrete'); put(px + w, y, pz, 'light_gray_concrete')
    for xx in range(px - w, px + w + 1):
        for y in (top + 5, top + 6, top + 7):
            put(xx, y, pz, 'green_concrete' if abs(xx - px) < w else 'light_gray_concrete')
        put(xx, top + 8, pz, 'light_gray_concrete')
    for i, ln in enumerate(lines_face):
        if ln: s(px + ln[0], top + 6, pz + face, ln[1], 'south' if face > 0 else 'north')
    for i, ln in enumerate(lines_back):
        if ln: s(px + ln[0], top + 6, pz + back, ln[1], 'south' if back > 0 else 'north')

def s(x, y, z, lines, facing):
    if allowed(x, z) and in_part(x, z):
        b.sign(x, y, z, lines, facing=facing, wall=True, wood='birch')

gantry(GANTRY_A, 3, 1, -1,
       [(-2, ['', 'EXIT 1', 'NORTH']), (0, ['', 'City ->', '']), (2, ['', 'Manor', 'Burj Khalifa'])],
       [(0, ['Welcome to', 'Newark Liberty', 'Intl Airport']), (-2, ['', 'Terminals', 'A  B  C']), (2, ['', 'Parking', 'AirTrain'])])
gantry(GANTRY_C, 4, -1, 1,
       [(0, ['Newark', 'Airport ->', 'EWR']), (-2, ['', 'Terminals', 'A  B  C']), (2, ['', 'AirTrain', 'Rental Cars'])],
       [(0, ['', 'City ->', 'Manor Gate']), (-2, ['', 'Welcome', '']), (2, ['', 'Burj', 'Khalifa'])])
