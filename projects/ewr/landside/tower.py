exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())

# FAA air traffic control tower, landside between Terminals B and C. zone s 138..162, t -115..-108
pbox(138, 162, -115, -108, 0, 60, "air")
rect(138, 162, -115, -108, -1, "smooth_stone")

# ---- base building (TRACON / equipment), one storey, walk 0, roof y=5
pbox(140, 160, -115, -108, 0, 4, "white_concrete", hollow=True)
rect(140, 160, -115, -108, 5, "light_gray_concrete")
rect(141, 159, -114, -109, -1, "polished_diorite")
for s in range(141, 160):
    if (s - 140) % 3:
        pbox(s, s, -108, -108, 1, 3, "light_blue_stained_glass")
        pbox(s, s, -115, -115, 1, 3, "light_blue_stained_glass")
x, z = P(144, -108); b.door(x, 0, z, "west", "birch_door", "left")
x, z = P(145, -108); b.door(x, 0, z, "west", "birch_door", "right")
x, z = P(146, -108); b.sign(x, 2, z, ["FAA", "Newark ATCT", "Staff only"], facing="east")
for s in (143, 157):
    for t in (-113, -110):
        put(s, t, 4, "sea_lantern")
# equipment racks / desk
pbox(156, 159, -114, -114, 0, 2, "smooth_stone")
for s in (156, 158):
    put(s, -114, 1, "observer[facing=east]")
pbox(141, 143, -112, -110, 0, 0, "spruce_planks")
put(142, -111, 1, "lectern[facing=east]")

# ---- shaft: 5x5 with chamfered corners, y 0..42
SS1, SS2, ST1, ST2 = 148, 152, -114, -110
TOP = 42
for y in range(0, TOP + 1):
    for s in range(SS1, SS2 + 1):
        for t in range(ST1, ST2 + 1):
            edge = s in (SS1, SS2) or t in (ST1, ST2)
            corner = s in (SS1, SS2) and t in (ST1, ST2)
            if corner:
                continue
            if edge:
                blk = "white_concrete"
                if t == ST2 and s == 150 and y % 6 == 3:
                    blk = "light_blue_stained_glass"       # slit windows facing the airfield
                if s == SS1 and t == -112 and y % 6 == 3:
                    blk = "light_blue_stained_glass"
                put(s, t, y, blk)
            elif y > 0:
                put(s, t, y, "air")
    for (s, t) in ((SS1, ST1), (SS1, ST2), (SS2, ST1), (SS2, ST2)):
        put(s, t, y, "smooth_quartz" if y < TOP - 2 else "light_gray_concrete")
# vertical grey fins on the shaft faces
for y in range(6, TOP - 2):
    put(SS1 - 1, -112, y, "light_gray_concrete")
    put(SS2 + 1, -112, y, "light_gray_concrete")
# doorway from base into shaft (east face)
put(150, ST2, 0, "air"); put(150, ST2, 1, "air")
# ladder up the west inner wall to the cab floor
for y in range(0, TOP + 2):
    put(150, -113, y, "ladder[facing=east]")

# ---- junction / equipment floor y 40..42, wider
pbox(147, 153, -114, -110, 40, 42, "light_gray_concrete", hollow=True)
pbox(148, 152, -113, -111, 40, 42, "air")
for y in range(40, 43):
    put(150, -113, y, "ladder[facing=east]")
pbox(147, 153, -114, -110, 41, 41, "black_stained_glass", hollow=True)
pbox(148, 152, -113, -111, 41, 41, "air")
put(150, -113, 41, "ladder[facing=east]")

# ---- cab: floor y=43, glass y 44..47, roof y 48 (octagonal 8 x 10)
CS1, CS2, CT1, CT2 = 145, 155, -115, -108


def in_cab(s, t, inset=0):
    a, bb = CS1 + inset, CS2 - inset
    c, d = CT1 + inset, CT2 - inset
    if not (a <= s <= bb and c <= t <= d):
        return False
    # chamfer: cut 2 off each corner
    ds = min(s - a, bb - s); dt = min(t - c, d - t)
    return ds + dt >= 2


for s in range(CS1, CS2 + 1):
    for t in range(CT1, CT2 + 1):
        if not in_cab(s, t):
            continue
        rim = not in_cab(s, t, 1) or not all(in_cab(s + ds, t + dt) for ds, dt in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        put(s, t, 43, "gray_concrete" if rim else "polished_andesite")
        put(s, t, 48, "gray_concrete")
        put(s, t, 49, "smooth_stone_slab[type=bottom]" if not rim else "light_gray_concrete")
        if rim:
            put(s, t, 44, "black_concrete")
            for y in (45, 46, 47):
                put(s, t, y, "light_blue_stained_glass")
# underside lip below the cab
for s in range(CS1 + 1, CS2):
    for t in range(CT1 + 1, CT2):
        if in_cab(s, t, 0) and not in_cab(s, t, 1):
            put(s, t, 42, "light_gray_concrete")
# ladder hatch into cab
put(150, -113, 43, "ladder[facing=east]")
put(150, -113, 44, "air")
put(150, -114, 44, "iron_bars"); put(151, -113, 44, "iron_bars"); put(149, -113, 44, "iron_bars")
# consoles around the glass: smooth stone desks with lecterns (flight strips) and screens
for s in range(CS1 + 1, CS2):
    for t in range(CT1 + 1, CT2):
        if in_cab(s, t) and in_cab(s, t, 1) and not in_cab(s, t, 2):
            if (s, t) in ((150, -114), (149, -114), (151, -114)):
                continue
            put(s, t, 44, "smooth_stone")
            put(s, t, 45, "smooth_stone_slab[type=bottom]")
for (s, t, f) in ((154, -112, "north"), (154, -111, "north"), (146, -112, "south"), (146, -111, "south"),
                  (150, -109, "east"), (148, -109, "east"), (152, -109, "east")):
    put(s, t, 45, f"lectern[facing={f}]")
for (s, t) in ((153, -110), (147, -110), (153, -113), (147, -113)):
    put(s, t, 45, "daylight_detector")
# controller chairs facing out toward the runways and along the field
for (s, t, f) in ((150, -110, "east"), (148, -110, "east"), (152, -110, "east"),
                  (153, -111, "north"), (147, -111, "south")):
    x, z = P(s, t); b.chair(x, 44, z, f, "quartz_stairs")
# supervisor desk in the middle
put(151, -112, 44, "spruce_fence"); put(151, -112, 45, "white_carpet")
# ceiling lights
for (s, t) in ((148, -112), (152, -112), (150, -111)):
    put(s, t, 48, "sea_lantern")
for (s, t) in ((147, -111), (153, -111)):
    put(s, t, 47, "lantern[hanging=true]")

# ---- roof equipment, antenna, red aviation light
pbox(149, 151, -113, -111, 50, 50, "light_gray_concrete")
put(150, -112, 50, "iron_block")
for y in range(51, 57):
    put(150, -112, y, "lightning_rod" if y == 56 else "iron_bars" if y > 52 else "iron_block")
put(150, -112, 56, "redstone_block")
put(150, -112, 57, "redstone_lamp[lit=true]")
put(150, -112, 58, "red_stained_glass")
put(150, -112, 59, "lightning_rod")
# radar dish & secondary antennas
put(148, -110, 50, "iron_bars"); put(148, -110, 51, "iron_bars"); put(148, -110, 52, "daylight_detector")
put(152, -114, 50, "iron_bars"); put(152, -114, 51, "end_rod")
# red obstruction lights on the cab roof corners
for (s, t) in ((146, -114), (154, -109), (146, -109), (154, -114)):
    put(s, t, 50, "redstone_block"); put(s, t, 51, "redstone_lamp[lit=true]")
# grounds: lamp posts and a sign
for (s, t) in ((139, -109), (161, -109)):
    put(s, t, 0, "stone_brick_wall"); put(s, t, 1, "iron_bars"); put(s, t, 2, "iron_bars"); put(s, t, 3, "lantern")
x, z = P(139, -111); b.sign(x, 1, z, ["FAA", "Air Traffic", "Control Tower", "EWR"], facing="east", wall=False)
