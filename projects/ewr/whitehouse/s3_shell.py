exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\whitehouse\lib.py").read())
# Executive Residence shell. Local view r: rx 0..84 (west->east), rz 0..42 (north->south)
r = b.at(RX0, 0, RZ0)
XN, ZN = 84, 42
WALL, BASE = 'smooth_quartz', 'quartz_bricks'
Y_GF, Y_SF, Y_2F, Y_RF = -1, 7, 18, 26        # floor slabs (ground, state, second, roof)

# ---- solid shell: walls + floors, interior cleared
for y in range(-1, 27):
    blk = BASE if y <= 7 else WALL
    for x in range(0, XN + 1):
        r.set(x, y, 0, blk); r.set(x, y, ZN, blk)
    for z in range(0, ZN + 1):
        r.set(0, y, z, blk); r.set(XN, y, z, blk)
for y in (Y_GF, Y_SF, Y_2F, Y_RF):
    r.box(1, y, 1, XN - 1, y, ZN - 1, 'smooth_quartz' if y != Y_GF else 'smooth_stone')
for (y1, y2) in ((0, 6), (8, 17), (19, 25)):
    r.box(1, y1, 1, XN - 1, y2, ZN - 1, 'air')
# base course / string courses
for y, blk in ((7, 'smooth_quartz_slab[type=top]'), (18, 'smooth_quartz_slab[type=top]')):
    for x in range(-1, XN + 2):
        r.set(x, y, -1, blk); r.set(x, y, ZN + 1, blk)
    for z in range(0, ZN + 1):
        r.set(-1, y, z, blk); r.set(XN + 1, y, z, blk)

# ---- facades
def face_map(face):
    if face == 'n':
        return (lambda u, d: (u, -d)), 'east', 'south', XN
    if face == 's':
        return (lambda u, d: (u, ZN + d)), 'east', 'north', XN
    if face == 'w':
        return (lambda u, d: (-d, u)), 'south', 'east', ZN
    return (lambda u, d: (XN + d, u)), 'south', 'west', ZN

def fset(face, u, y, d, blk):
    m = face_map(face)[0]
    x, z = m(u, d)
    r.set(x, y, z, blk)

def window_bay(face, c, i, ground=True):
    m, up, inward, _ = face_map(face)
    dn = OPPOSITE[up]
    if ground:
        for u in range(c - 1, c + 2):
            for y in range(1, 5):
                fset(face, u, y, 0, 'glass_pane')
        fset(face, c, 5, 0, 'chiseled_quartz_block')
    # state floor: tall windows + alternating pediments
    for u in range(c - 1, c + 2):
        for y in range(9, 15):
            fset(face, u, y, 0, 'glass_pane')
        fset(face, u, 8, 1, 'smooth_quartz_slab[type=top]')
    fset(face, c - 2, 15, 1, f'smooth_quartz_stairs[facing={up}]'); fset(face, c + 2, 15, 1, f'smooth_quartz_stairs[facing={dn}]')
    for u in range(c - 1, c + 2):
        fset(face, u, 15, 1, 'smooth_quartz')
    if i % 2 == 0:   # triangular pediment
        fset(face, c - 1, 16, 1, f'smooth_quartz_stairs[facing={up}]'); fset(face, c + 1, 16, 1, f'smooth_quartz_stairs[facing={dn}]')
        fset(face, c, 16, 1, 'smooth_quartz'); fset(face, c, 17, 1, 'smooth_quartz_slab')
    else:            # segmental (arched) pediment
        for u in range(c - 1, c + 2):
            fset(face, u, 16, 1, 'smooth_quartz_slab')
        fset(face, c, 16, 1, 'smooth_quartz_stairs[facing=%s,half=bottom]' % inward) if False else None
    # second floor
    for u in range(c - 1, c + 2):
        for y in range(20, 24):
            fset(face, u, y, 0, 'glass_pane')
        fset(face, u, 24, 1, f'smooth_quartz_stairs[facing={inward},half=top]')
        fset(face, u, 19, 1, 'smooth_quartz_slab[type=top]')

BAYS = [6 + 6 * i for i in range(13)]          # 13 bays on north & south fronts
for face in ('n', 's'):
    for i, c in enumerate(BAYS):
        window_bay(face, c, i)
for face in ('w', 'e'):
    for i, c in enumerate([6, 13, 21, 29, 36]):
        window_bay(face, c, i)

# pilasters between bays on the south front + corners (Ionic pilasters)
for face in ('n', 's', 'w', 'e'):
    L = face_map(face)[3]
    for u in (0, L):
        for y in range(8, 25):
            fset(face, u, y, 1, 'quartz_pillar')
        fset(face, u, 25, 1, 'chiseled_quartz_block')

# ---- entablature, cornice, roof balustrade
for x in range(-1, XN + 2):
    r.set(x, 25, -1, 'smooth_quartz'); r.set(x, 25, ZN + 1, 'smooth_quartz')
    r.set(x, 26, -2, 'smooth_quartz_stairs[facing=south,half=top]'); r.set(x, 26, ZN + 2, 'smooth_quartz_stairs[facing=north,half=top]')
    r.set(x, 26, -1, 'smooth_quartz'); r.set(x, 26, ZN + 1, 'smooth_quartz')
for z in range(-1, ZN + 2):
    r.set(-1, 25, z, 'smooth_quartz'); r.set(XN + 1, 25, z, 'smooth_quartz')
    r.set(-2, 26, z, 'smooth_quartz_stairs[facing=east,half=top]'); r.set(XN + 2, 26, z, 'smooth_quartz_stairs[facing=west,half=top]')
    r.set(-1, 26, z, 'smooth_quartz'); r.set(XN + 1, 26, z, 'smooth_quartz')
for (x1, z1, x2, z2) in [(-1, -1, XN + 1, -1), (-1, ZN + 1, 28, ZN + 1), (56, ZN + 1, XN + 1, ZN + 1),
                         (-1, -1, -1, ZN + 1), (XN + 1, -1, XN + 1, ZN + 1)]:
    balustrade(r.at(0, 0, 0) and x1, z1, x2, z2, 27) if False else None
def rbal(x1, z1, x2, z2, y=27):
    n = 0
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for z in range(min(z1, z2), max(z1, z2) + 1):
            r.set(x, y, z, 'smooth_quartz' if n % 6 == 0 else 'diorite_wall'); r.set(x, y + 1, z, 'smooth_quartz_slab')
            n += 1
rbal(-1, -1, XN + 1, -1); rbal(-1, ZN + 1, 29, ZN + 1); rbal(55, ZN + 1, XN + 1, ZN + 1)
rbal(-1, -1, -1, ZN + 1); rbal(XN + 1, -1, XN + 1, ZN + 1)
r.box(0, 26, 0, XN, 26, ZN, 'smooth_quartz')

# ---- third (attic) floor, set back behind the balustrade
r.box(5, 27, 5, XN - 5, 31, ZN - 5, 'white_concrete', hollow=True)
r.box(6, 27, 6, XN - 6, 31, ZN - 6, 'air')
for x in range(9, XN - 6, 6):
    for y in (28, 29):
        r.set(x, y, 5, 'glass_pane'); r.set(x, y, ZN - 5, 'glass_pane')
for z in range(10, ZN - 6, 6):
    for y in (28, 29):
        r.set(5, y, z, 'glass_pane'); r.set(XN - 5, y, z, 'glass_pane')
r.box(4, 32, 4, XN - 4, 32, ZN - 4, 'light_gray_concrete')
r.box(8, 33, 8, XN - 8, 33, ZN - 8, 'smooth_stone_slab')
r.box(14, 33, 14, XN - 14, 33, ZN - 14, 'smooth_stone')
r.box(20, 34, 17, XN - 20, 34, ZN - 17, 'smooth_stone_slab')
# chimneys
for (cx, cz) in [(12, 3), (71, 3), (12, 37), (71, 37), (30, 19), (53, 19)]:
    r.box(cx, 27, cz, cx + 1, 38, cz + 2, 'quartz_bricks')
    r.box(cx, 39, cz, cx + 1, 39, cz + 2, 'polished_blackstone_slab')
    r.box(cx - 1, 37, cz - 1, cx + 2, 37, cz + 3, 'smooth_quartz_slab[type=top]')
# roof flagpole
for y in range(35, 49):
    r.set(42, y, 21, 'iron_bars')
r.set(42, 34, 21, 'smooth_quartz'); r.set(42, 49, 21, 'end_rod')
r.set(43, 46, 21, 'white_wall_banner[facing=east]', nbt=FLAG_NBT)

# ---- columns
def column(x, z, y0, y1, cap=True):
    for dx, dz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        for y in range(y0 + 1, y1):
            r.set(x + dx, y, z + dz, 'quartz_pillar')
    r.box(x - 1, y0, z - 1, x + 1, y0, z + 1, 'smooth_quartz')
    r.box(x - 1, y1, z - 1, x + 1, y1, z + 1, 'chiseled_quartz_block')
    if cap:
        r.set(x - 2, y1, z, 'smooth_quartz_stairs[facing=east,half=top]'); r.set(x + 2, y1, z, 'smooth_quartz_stairs[facing=west,half=top]')
        r.set(x, y1, z - 2, 'smooth_quartz_stairs[facing=south,half=top]'); r.set(x, y1, z + 2, 'smooth_quartz_stairs[facing=north,half=top]')

# ---- NORTH PORTICO (Ionic, pediment) rx 29..55, rz -9..-1
r.box(28, 0, -9, 56, 7, -1, BASE)
r.box(28, 7, -9, 56, 7, -1, 'smooth_quartz')
for x in range(30, 55):
    r.set(x, 7, -9, 'polished_diorite')
for cx in (33, 39, 45, 51):
    column(cx, -7, 8, 24)
for cx in (33, 51):
    column(cx, -3, 8, 24)
for cx in (33, 39, 45, 51):                    # engaged pilasters on the wall
    for y in range(8, 25):
        r.set(cx, y, -1, 'quartz_pillar')
r.box(29, 25, -9, 55, 25, -1, 'smooth_quartz')
r.box(29, 26, -10, 55, 26, -1, 'smooth_quartz')
for x in range(28, 57):
    r.set(x, 26, -11, 'smooth_quartz_stairs[facing=south,half=top]')
for z in range(-10, 0):
    r.set(28, 26, z, 'smooth_quartz_stairs[facing=east,half=top]'); r.set(56, 26, z, 'smooth_quartz_stairs[facing=west,half=top]')
# pediment: gable over the portico, ridge along z
for k in range(0, 8):
    y = 27 + k
    xa, xb = 28 + 2 * k, 56 - 2 * k
    if xa > xb:
        break
    for z in range(-11, 1):
        r.set(xa, y, z, 'smooth_quartz_stairs[facing=east]'); r.set(xb, y, z, 'smooth_quartz_stairs[facing=west]')
        if xa + 1 <= xb - 1:
            r.set(xa + 1, y, z, 'smooth_quartz_slab'); r.set(xb - 1, y, z, 'smooth_quartz_slab')
        for x in range(xa + 2, xb - 1):
            r.set(x, y, z, 'smooth_quartz' if z == -10 else ('smooth_quartz' if z == -11 else 'air'))
    for x in range(xa + 1, xb):
        r.set(x, y, -10, 'smooth_quartz')
r.set(42, 30, -11, 'chiseled_quartz_block')    # oculus/ornament in the tympanum
r.set(42, 31, -11, 'chiseled_quartz_block')
# fill the pediment roof (top slabs only, hollow below)
for k in range(0, 8):
    y = 27 + k
    for z in range(-10, 1):
        for x in range(28 + 2 * k + 2, 56 - 2 * k - 1):
            pass
# portico lantern + entrance
for y in (23, 24):
    r.set(42, y, -4, 'iron_chain')
r.set(42, 22, -4, 'lantern[hanging=true]')
r.box(41, 8, 0, 43, 10, 0, 'air')
r.box(41, 11, 0, 43, 12, 0, 'glass_pane'); r.set(42, 13, 0, 'glass_pane')
for x in (40, 44):
    for y in range(8, 13):
        r.set(x, y, -1, 'quartz_pillar')
r.box(40, 13, -1, 44, 13, -1, 'chiseled_quartz_block')
for (x, z) in [(36, -8), (48, -8), (36, -2), (48, -2)]:
    r.set(x, 8, z, 'potted_fern') if False else r.set(x, 8, z, 'lantern')

# ---- SOUTH PORTICO (curved, Truman Balcony, twin curved stairs); centre (42, 42)
SCX, SCZ = 42, 42
def polar(rr, a):
    return SCX + rr * math.cos(a), SCZ + rr * math.sin(a)
for x in range(SCX - 15, SCX + 16):
    for z in range(SCZ + 1, SCZ + 16):
        d = math.hypot(x - SCX, z - SCZ)
        if d <= 13.4:
            for y in range(-1, 7):
                r.set(x, y, z, BASE if d > 10.5 else 'air')
            r.set(x, -1, z, 'smooth_stone')
            r.set(x, 7, z, 'smooth_quartz')
            if d > 12.6:
                r.set(x, 7, z, 'smooth_quartz_slab[type=top]') if False else None
        if 10.5 < d <= 13.4:
            pass
# arched openings in the base ring (centre + diagonals) and the Diplomatic Reception Room door
for ang in (90, 50, 130):
    a = math.radians(ang)
    for rr in (10.6, 11.5, 12.4, 13.2):
        for w in (-1, 0, 1):
            px, pz = polar(rr, a)
            tx, tz = -math.sin(a) * w, math.cos(a) * w
            for y in range(0, 5):
                r.set(round(px + tx), y, round(pz + tz), 'air')
r.box(41, 0, 42, 43, 4, 42, 'air')
# rectangular deck strips for the curved stairs
r.box(21, -1, 43, 30, 7, 46, BASE); r.box(54, -1, 43, 63, 7, 46, BASE)
r.box(21, 7, 43, 30, 7, 46, 'smooth_quartz'); r.box(54, 7, 43, 63, 7, 46, 'smooth_quartz')
for z in range(43, 47):
    pass
# columns on the curve
for ang in (14, 42, 70, 110, 138, 166):
    px, pz = polar(12, math.radians(ang))
    column(round(px), round(pz), 8, 24)
# Truman Balcony (second floor) inside the columns
for x in range(SCX - 11, SCX + 12):
    for z in range(SCZ + 1, SCZ + 12):
        d = math.hypot(x - SCX, z - SCZ)
        if d <= 10.2:
            r.set(x, 18, z, 'smooth_quartz_slab[type=top]')
        if 9.4 < d <= 10.2:
            r.set(x, 19, z, 'diorite_wall'); r.set(x, 20, z, 'smooth_quartz_slab')
# entablature + roof + balustrade on the bow
for x in range(SCX - 15, SCX + 16):
    for z in range(SCZ + 1, SCZ + 16):
        d = math.hypot(x - SCX, z - SCZ)
        if d <= 14.2:
            r.set(x, 26, z, 'smooth_quartz')
        if 12.5 < d <= 14.2:
            r.set(x, 25, z, 'smooth_quartz')
        if 14.2 < d <= 15.0:
            r.set(x, 26, z, 'smooth_quartz_slab[type=top]')
        if 13.2 < d <= 14.2:
            ang = math.degrees(math.atan2(z - SCZ, x - SCX))
            r.set(x, 27, z, 'smooth_quartz' if int(ang) % 12 < 2 else 'diorite_wall'); r.set(x, 28, z, 'smooth_quartz_slab')
# portico openings: Blue Room doors + Yellow Oval Room onto the balcony
r.box(40, 8, 42, 44, 11, 42, 'air'); r.box(40, 12, 42, 44, 14, 42, 'glass_pane')
r.box(41, 19, 42, 43, 21, 42, 'air'); r.box(41, 22, 42, 43, 23, 42, 'glass_pane')
# curved staircases: west (centre 21,52 sweeping W->S) and east (centre 63,52 sweeping E->S)
def curved_stair(ccx, ccz, a0, a1):
    cells = {}
    for x in range(ccx - 10, ccx + 11):
        for z in range(ccz - 10, ccz + 11):
            d = math.hypot(x - ccx, z - ccz)
            a = math.degrees(math.atan2(z - ccz, x - ccx))
            lo, hi = min(a0, a1), max(a0, a1)
            if a0 < -90 or a1 < -90:   # west stair: angles -180..-90 (also +180)
                if a > 0:
                    a -= 360
            if not (lo <= a <= hi):
                continue
            t = (a - a0) / (a1 - a0)
            if 4.5 <= d <= 7.5:
                h = max(0, min(6, int(7 - t * 7.6)))
                # ascent direction = towards a0
                aa = math.radians(a)
                sgn = 1 if a1 > a0 else -1
                ux, uz = sgn * math.sin(aa), -sgn * math.cos(aa)
                if abs(ux) > abs(uz):
                    fac = 'east' if ux > 0 else 'west'
                else:
                    fac = 'south' if uz > 0 else 'north'
                for y in range(-1, h):
                    r.set(x, y, z, BASE)
                r.set(x, h, z, f'quartz_stairs[facing={fac}]')
                for y in range(h + 1, 9):
                    r.set(x, y, z, 'air')
                cells[(x, z)] = h
            elif 7.5 < d <= 8.4 or 3.7 <= d < 4.5:
                h = max(0, min(6, int(7 - t * 7.6)))
                for y in range(-1, h + 1):
                    r.set(x, y, z, BASE)
                r.set(x, h + 1, z, 'diorite_wall'); r.set(x, h + 2, z, 'smooth_quartz_slab')
    return cells
curved_stair(21, 51, -90, -180)
curved_stair(63, 51, -90, 0)
# ground-floor openings to the colonnades (west + east ends)
r.box(0, 0, 18, 0, 4, 20, 'air'); r.box(XN, 0, 18, XN, 4, 20, 'air')
# keep doorways clear of sills
r.box(41, 8, -1, 43, 10, -1, 'air')
r.box(40, 8, 43, 44, 11, 43, 'air'); r.box(40, 19, 43, 44, 21, 43, 'air')
