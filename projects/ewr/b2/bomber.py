# B-2 Spirit, ~1:1.6 (span 33, length 13), nose pointing west toward the hangar door.
# World origin (0,64,0). Nose tip at x=NX, centreline z=CZ. v = blocks aft of the nose (+x), u = +z.
NX, CZ, BY = 163, 70, 2          # BY = belly block y (gear below at y 0..1)
HS = 16.5                        # half span
K = 10.4 / HS                    # leading-edge slope (33 deg sweep)
# trailing edge (u>=0), all edges parallel to the leading edges -> double-W sawtooth
TE = [(0.0, 13.0), (3.6, 10.0), (7.2, 13.0), (11.6, 9.7), (HS, 13.0)]


def v_te(u):
    u = abs(u)
    for (u1, v1), (u2, v2) in zip(TE, TE[1:]):
        if u1 <= u <= u2:
            return v1 + (v2 - v1) * (u - u1) / (u2 - u1)
    return -1


def inside(u, v):
    au = abs(u)
    return au <= HS and v >= K * au and v <= v_te(au)


def lerp_tab(tab, x):
    for (x1, y1), (x2, y2) in zip(tab, tab[1:]):
        if x1 <= x <= x2:
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    return tab[-1][1]


TC = [(0, 3.2), (2.5, 3.0), (3.5, 2.6), (6, 2.1), (8, 1.4), (10, 1.1), (13, 0.8), (HS, 0.6)]


def thick(u, v):
    au = abs(u)
    vle = K * au
    xc = max(0.0, min(1.0, (v - vle) / (13.0 - vle)))
    if xc < 0.3:
        f = (xc / 0.3) ** 0.55
    elif xc > 0.5:
        f = 1 - 0.5 * ((xc - 0.5) / 0.5) ** 1.4
    else:
        f = 1.0
    t = lerp_tab(TC, au) * f
    # engine humps: A at |u| 3..4 (v 4..9), B at |u| 5..6 (v 5..10)
    if 2.5 <= au <= 4.4 and 4.0 <= v <= 9.5:
        t += 1.0
    if 4.6 <= au <= 6.5 and 5.0 <= v <= 10.5:
        t += 0.9
    return max(0.5, t)


# ---------- rasterise ----------
cols = {}   # (iv, iu) -> half-block height (0 = none)
for iv in range(0, 13):
    for iu in range(-17, 18):
        n = 0
        for a in range(4):
            for c in range(4):
                if inside(iu - 0.375 + 0.25 * c, iv + 0.125 + 0.25 * a):
                    n += 1
        cov = n / 16
        if cov >= 0.55:
            cols[(iv, iu)] = max(1, int(round(thick(iu, iv + 0.5) * 2)))
        elif cov >= 0.35:
            cols[(iv, iu)] = 1           # thin edge: a single slab
# cockpit / centre-body hump over the nose
CK = {0: 3, 1: 5, 2: 7, 3: 8, 4: 8, 5: 8, 6: 7, 7: 7}
for iv, h in CK.items():
    for iu in range(-2, 3):
        if (iv, iu) in cols:
            hh = h - (1 if abs(iu) == 2 and iv in (0, 1, 2, 6, 7) else 0)
            cols[(iv, iu)] = max(cols[(iv, iu)], hh)
for iv in (3, 4, 5, 6):
    for iu in (-3, 3):
        if (iv, iu) in cols:
            cols[(iv, iu)] = max(cols[(iv, iu)], 7 if iv < 6 else 6)

# intakes / exhaust troughs
intake = set()
trough = set()
for s in (-1, 1):
    for au in (3, 4):
        intake.add((4, s * au))
        for iv in (9, 10):
            trough.add((iv, s * au))
    for au in (5, 6):
        intake.add((5, s * au))
        for iv in (10, 11):
            trough.add((iv, s * au))

FULL = "gray_concrete"
SLAB = "polished_deepslate_slab[type=bottom]"
STAIR = "polished_deepslate_stairs"
DIRS4 = {"east": (1, 0), "west": (-1, 0), "south": (0, 1), "north": (0, -1)}

print("planform (half-block heights):")
for iu in range(-17, 18):
    print("".join((str(min(9, cols[(iv, iu)])) if (iv, iu) in cols else ".") for iv in range(13)))

for (iv, iu), h2 in cols.items():
    x, z = NX + iv, CZ + iu
    if (iv, iu) in trough:
        h2 = min(h2, 2)
        b.set(x, BY, z, "polished_blackstone_slab[type=top]" if h2 >= 2 else "polished_blackstone_slab[type=bottom]")
        continue
    full = h2 // 2
    for k in range(full):
        b.set(x, BY + k, z, "polished_deepslate" if (k == full - 1 and h2 % 2 == 0) else FULL)
    if h2 % 2:
        y = BY + full
        stair = None
        # stair toward a taller neighbour (prefer aft, then inboard, then the sides)
        for d in ("east", "west"):
            dx, dz = DIRS4[d]
            if cols.get((iv + dx, iu + dz), 0) >= h2 + 1 and (iv + dx, iu + dz) not in trough:
                stair = d
                break
        if stair:
            b.set(x, y, z, f"{STAIR}[facing={stair},half=bottom]")
        else:
            b.set(x, y, z, SLAB)
    if (iv, iu) in intake:
        top = BY + (h2 - 1) // 2
        b.set(x, top, z, "black_concrete")                          # recessed intake mouth
        b.set(x, top + 1, z, "air")
        b.set(x - 1, top, z, "polished_blackstone_slab[type=top]") if (iv - 1, iu) in cols and cols[(iv - 1, iu)] >= h2 - 1 else None

# exhaust trough side walls / blackstone lips at the trough ends
for (iv, iu) in trough:
    if (iv - 1, iu) in cols and (iv - 1, iu) not in trough:
        b.set(NX + iv - 1, BY + max(0, (cols[(iv - 1, iu)] - 1) // 2), CZ + iu, "polished_blackstone")

# ---------- cockpit (interior x 163..165, z 69..71, y 3..4) ----------
b.box(NX + 3, BY + 1, CZ - 1, NX + 5, BY + 2, CZ + 1, "air")
b.box(NX + 3, BY, CZ - 1, NX + 5, BY, CZ + 1, "polished_deepslate")          # floor
b.box(NX + 3, BY + 3, CZ - 1, NX + 5, BY + 3, CZ + 1, "polished_deepslate")   # roof
# windows: 2 front + 2 side, dark tinted
b.set(NX + 2, BY + 2, CZ - 1, "black_stained_glass"); b.set(NX + 2, BY + 2, CZ + 1, "black_stained_glass")
b.set(NX + 2, BY + 2, CZ, "polished_deepslate")                               # centre post
b.set(NX + 2, BY + 2, CZ - 2, "gray_stained_glass"); b.set(NX + 2, BY + 2, CZ + 2, "gray_stained_glass")
for dz in (-2, -1, 0, 1, 2):
    b.set(NX + 2, BY + 3, CZ + dz, "air")           # windscreen open to the sky, on the upper nose
# instrument panel: two lit screens (powered lamps) + centre display
b.box(NX + 1, BY + 1, CZ - 1, NX + 1, BY + 1, CZ + 1, "redstone_block")       # hidden power behind the panel
b.set(NX + 2, BY + 1, CZ - 1, "redstone_lamp[lit=true]")
b.set(NX + 2, BY + 1, CZ + 1, "redstone_lamp[lit=true]")
b.set(NX + 2, BY + 1, CZ, "black_stained_glass")
b.set(NX + 1, BY + 1, CZ, "sea_lantern")                                       # glows through the centre display
# side consoles under the side windows
b.set(NX + 3, BY + 1, CZ - 2, "polished_blackstone"); b.set(NX + 3, BY + 1, CZ + 2, "polished_blackstone")
# seats (sitter looks west / forward), control sticks in front
b.chair(NX + 4, BY + 1, CZ - 1, "west", "polished_blackstone_stairs")
b.chair(NX + 4, BY + 1, CZ + 1, "west", "polished_blackstone_stairs")
b.set(NX + 3, BY + 1, CZ - 1, "lever[face=floor,facing=west,powered=false]")
b.set(NX + 3, BY + 1, CZ + 1, "lever[face=floor,facing=west,powered=false]")
# overhead switch panel
for dz in (-1, 0, 1):
    b.set(NX + 3, BY + 2, CZ + dz, "polished_blackstone_button[face=ceiling,facing=west]") if dz == 0 else None
b.set(NX + 4, BY + 2, CZ, "polished_blackstone_button[face=ceiling,facing=west]")
b.set(NX + 5, BY + 2, CZ - 1, "lantern[hanging=true]")                      # cabin light
# crew hatch + ladder (x 165, z 70) from the ground up into the cockpit aisle
b.set(NX + 5, BY, CZ, "air")
b.set(NX + 6, 0, CZ, "polished_blackstone"); b.set(NX + 6, 1, CZ, "polished_blackstone")   # hatch frame / ladder backing
b.ladder(NX + 5, 0, CZ, 4, "west")
b.set(NX + 5, BY + 2, CZ, "air")

# ---------- landing gear ----------
def gear(x, z, doors):
    b.set(x, 0, z, "black_concrete")                     # wheels
    b.set(x, 1, z, "polished_blackstone_wall")           # strut
    for (dx, dz, f) in doors:
        b.set(x + dx, 1, z + dz, f"iron_trapdoor[facing={f},open=true,half=top]")

gear(NX + 3, CZ, [(0, -1, "south"), (0, 1, "north")])                        # nose gear
for s in (-1, 1):
    zc = CZ + 5 * s
    for x in (NX + 7, NX + 8):
        b.set(x, 0, zc, "black_concrete")
    b.set(NX + 7, 1, zc, "polished_blackstone_wall"); b.set(NX + 8, 1, zc, "polished_blackstone_wall")
    for x in (NX + 7, NX + 8):
        b.set(x, 1, zc + s, f"iron_trapdoor[facing={'north' if s > 0 else 'south'},open=true,half=top]")
        b.set(x, 1, zc - s, f"iron_trapdoor[facing={'south' if s > 0 else 'north'},open=true,half=top]")
# wheel chocks
for x, z in ((NX + 2, CZ), (NX + 6, CZ + 5), (NX + 6, CZ - 5), (NX + 9, CZ + 5), (NX + 9, CZ - 5)):
    pass
for dz in (-1, 1):
    b.set(NX + 3, BY + 2, CZ + dz, "stone_button[face=ceiling,facing=west]")
