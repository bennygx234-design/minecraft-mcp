# Burj Khalifa at ~1:3.3 scale (828 m -> 248 blocks), the tallest that fits under the y=319 build limit.
# Origin = centre of the tower at plaza floor level. Run through the `build` tool.
#
# Plan: the real "Y" (desert flower) footprint: three wings around a round core. The 27 setbacks spiral
# clockwise, one wing at a time, until the wings have merged into the core; the core then tapers into
# the spire. The body takes ~70% of the height and the spire the rest, like the real tower.

H = 248            # spire tip
BODY = 172         # top of the occupied tower
DECK = 152         # "At the Top" observation deck floor
L0, W, RC = 26, 6, 8.5          # wing length (centre to tip), wing half-width, core radius
NSET, SET_LO, SET_HI = 27, 10, 136
GLASS = "light_blue_stained_glass"
FIN = "iron_block"
TERRACE = "smooth_quartz"
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))

dirs = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in (-90, 30, 150)]  # N, SE, SW
step = (L0 - RC) / 9
setbacks = [SET_LO + i * (SET_HI - SET_LO) / (NSET - 1) for i in range(NSET)]


def wing_len(k, y):
    return L0 - step * sum(1 for i, h in enumerate(setbacks) if i % 3 == k and h <= y)


def core_r(y):
    return RC if y < 140 else max(4.5, RC - ((y - 140) // 8 + 1))


def inside(x, z, y):
    r = core_r(y)
    if x * x + z * z <= r * r:
        return True
    for k, (dx, dz) in enumerate(dirs):
        L = wing_len(k, y)
        if L <= r:
            continue
        t, s = x * dx + z * dz, -x * dz + z * dx
        if abs(s) <= W and 0 <= t <= L - W:
            return True
        tx, tz = dx * (L - W), dz * (L - W)
        if (x - tx) ** 2 + (z - tz) ** 2 <= W * W:
            return True
    return False


R = L0 + 2
levels = [{(x, z) for x in range(-R, R + 1) for z in range(-R, R + 1) if inside(x, z, y)} for y in range(BODY + 1)]


def interior(S, x, z):
    return all((x + dx, z + dz) in S for dx, dz in N4)


# ---- plaza: cleared, levelled, reflecting pool ring, lamp posts --------------------------
RP = 46
b.cylinder(0, 0, 0, RP, 30, "air")
b.cylinder(0, -8, 0, RP, 7, "sandstone")
b.cylinder(0, -1, 0, RP, 1, {"smooth_sandstone": 4, "cut_sandstone": 1})
ez_path = round(dirs[2][1] * (L0 + 1))            # entrance on the south-west wing, facing the manor
for x in range(-RP, RP + 1):
    for z in range(-RP, RP + 1):
        d2 = x * x + z * z
        if 30 * 30 <= d2 <= 31 * 31 or 40 * 40 <= d2 <= 41 * 41:
            b.set(x, -1, z, "polished_diorite")
        if 34 * 34 <= d2 <= 37 * 37 and abs(z - ez_path) > 2:
            b.set(x, -1, z, "water")                  # all neighbours are solid plaza, so it stays put
for i in range(16):
    a = i * math.pi / 8
    b.lamp(round(math.cos(a) * 43), 0, round(math.sin(a) * 43), post="iron_bars")
for x in range(-RP, round(dirs[2][0] * L0) + 1):  # walkway from the plaza edge to the entrance
    for dz in (-1, 0, 1):
        b.set(x, -1, ez_path + dz, "polished_andesite")

# ---- tower body --------------------------------------------------------------------------
for y, S in enumerate(levels):
    above = levels[y + 1] if y + 1 < len(levels) else set()
    for (x, z) in S:
        out = sum((x + dx, z + dz) not in S for dx, dz in N4)
        if out:
            if DECK + 1 <= y <= DECK + 4:
                b.set(x, y, z, "glass")                       # clear wraparound deck windows
            elif out >= 3 or (3 * x + 5 * z) % 4 == 0:
                b.set(x, y, z, FIN)                           # vertical silver fins
            else:
                b.set(x, y, z, GLASS)
        elif (x, z) not in above:
            b.set(x, y, z, TERRACE)                           # setback terrace / roof
        elif y % 4 == 0 and y != 4:
            # floor plate every 4 blocks (the lobby is double height), lights set into the floor
            b.set(x, y, z, "sea_lantern" if x % 5 == 0 and z % 5 == 0 else "white_concrete")

# ---- lobby -------------------------------------------------------------------------------
for (x, z) in levels[0]:
    if interior(levels[0], x, z):
        b.set(x, 0, z, "quartz_block" if (x + z) % 2 else "polished_diorite")
ex, ez = round(dirs[2][0] * (L0 - 1)), round(dirs[2][1] * (L0 - 1))
for x in range(ex - 3, ex + 4):                    # open the entrance in the wing tip
    for z in range(ez - 3, ez + 4):
        if (x, z) in levels[1] and (x - ex) ** 2 + (z - ez) ** 2 <= 8 and not interior(levels[1], x, z):
            for y in range(1, 6):
                b.set(x, y, z, "air")
b.box(-3, 1, 6, 3, 1, 6, "polished_blackstone")   # reception desk
b.box(-3, 2, 6, 3, 2, 6, "smooth_quartz_slab[type=bottom]")
b.sign(0, 1, 8, ["BURJ KHALIFA", "", "Scale 1:3.3", "828 m = 248 blocks"], facing="south", wall=False)
for dx, dz in dirs:                               # a seating area in each wing
    v = b.at(round(dx * 15), 0, round(dz * 15))
    v.sofa(-1, 1, 0, "south", length=3, seat="quartz_stairs", arm="birch_trapdoor")
    v.plant(-3, 1, 0, "potted_bamboo"); v.plant(3, 1, 0, "potted_bamboo")
for (x, z) in [(6, 0), (-6, 0), (0, -6), (12, 7), (-12, 7), (0, -14)]:
    b.lamp(x, 7, z, hanging=True)

# lift shaft: glass core with a ladder from the lobby to the deck (climb it, or just /tp)
for y in range(1, DECK + 1):
    for (x, z) in ((-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (-1, 0), (1, 0)):
        b.set(x, y, z, "white_stained_glass")
    b.set(0, y, 0, "ladder[facing=south]")
    b.set(0, y, 1, "air")
b.set(0, DECK + 1, 1, "air")

# ---- observation deck "At the Top" ---------------------------------------------------------
deck = levels[DECK + 1]
for (x, z) in deck:
    if interior(deck, x, z) and not all(interior(deck, x + dx, z + dz) for dx, dz in N4):
        b.set(x, DECK + 1, z, "light_blue_carpet")     # carpet ring along the windows
b.sign(0, DECK + 1, 3, ["AT THE TOP", "", "(scaled)"], facing="south", wall=False)
for (x, z) in [(4, 3), (-4, 3), (4, -4), (-4, -4)]:
    b.lamp(x, DECK + 3, z, hanging=True)

# ---- spire ---------------------------------------------------------------------------------
for y in range(BODY + 1, H - 6):
    t = (y - BODY) / (H - BODY)
    blk = FIN if (y - BODY) % 6 == 0 else {"smooth_quartz": 3, "iron_block": 1}
    b.cylinder(0, y, 0, 4.2 * (1 - t) + 0.4, 1, blk)
b.set(0, H - 7, 0, "sea_lantern")
for y in range(H - 6, H):
    b.set(0, y, 0, "end_rod[facing=up]")
b.set(0, H, 0, "lightning_rod")
print("levels", len(levels), "base footprint", len(levels[0]), "deck footprint", len(deck), "top", H)
