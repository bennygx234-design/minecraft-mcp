exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\whitehouse\lib.py").read())
# THE OVAL OFFICE (rebuilt at true scale): interior 15 x 17 blocks (~9 x 10.5 m), 10 high (~6 m)
# long axis north-south: fireplace (north) <-> Resolute Desk before three south windows
CX, CZ = 21, 87
AI, BI = 7.4, 8.9                    # interior
def ev(x, z, a, b_):
    return ((x - CX) / a) ** 2 + ((z - CZ) / b_) ** 2
def inside(x, z):  return ev(x, z, AI, BI) <= 1
def ring1(x, z):   return not inside(x, z) and ev(x, z, AI + 1, BI + 1) <= 1     # inner (cream) wall
def ring2(x, z):   return not inside(x, z) and not ring1(x, z) and ev(x, z, AI + 2, BI + 2) <= 1   # outer white wall
def ang(x, z):
    return math.degrees(math.atan2((z - CZ) / BI, (x - CX) / AI)) % 360
WALL, CREAM, TRIM = 'smooth_quartz', 'smooth_sandstone', 'cut_sandstone'
X1, X2, Z1, Z2 = 13, 31, 75, 98

# ---- 1. reset the whole oval block (x 13..31, z 75..98) and the hall/study strip (x 9..12, z 75..92, ground floor only)
for x in range(X1, X2 + 1):
    for z in range(Z1, Z2 + 1):
        for y in range(-1, 19):
            b.set(x, y, z, 'air')
        b.set(x, -1, z, 'grass_block')
for x in range(9, 13):
    for z in range(75, 92):
        for y in range(0, 9):
            b.set(x, y, z, 'air')
        b.set(x, -1, z, 'polished_diorite')
# wall between Roosevelt/Cabinet rooms (z 66..73) and the new hall / secretary (z 75..)
b.box(9, -1, 74, 29, 9, 74, WALL)
# rebuild the West Wing rectangle part x 13..29, z 75..84 (second floor + roof above the oval's north half)
for x in range(13, 30):
    for z in range(75, 85):
        b.set(x, -1, z, 'polished_diorite')
        for y in range(9, 16):
            b.set(x, y, z, WALL)
        b.set(x, 16, z, 'light_gray_concrete' if x < 29 else WALL)
for z in range(75, 85):
    for y in range(-1, 9):
        b.set(29, y, z, WALL)
    b.set(29, 17, z, 'diorite_wall' if z % 5 else 'smooth_quartz'); b.set(29, 18, z, 'smooth_quartz_slab')
    b.set(30, 16, z, 'smooth_quartz_stairs[facing=west,half=top]'); b.set(30, 9, z, 'smooth_quartz_slab[type=top]')
for x in range(13, 30):
    b.set(x, 17, 84, 'diorite_wall' if x % 5 else 'smooth_quartz'); b.set(x, 18, 84, 'smooth_quartz_slab')
    b.set(x, 16, 85, 'smooth_quartz_stairs[facing=north,half=top]')
for z in range(75, 85):           # solid fill in the rectangle's ground floor; rooms carved below
    for x in range(13, 29):
        for y in range(0, 9):
            b.set(x, y, z, WALL)

# ---- 2. the oval: shell, cream walls, ceiling, roof
for x in range(X1 - 1, X2 + 1):
    for z in range(Z1, Z2 + 1):
        if ring2(x, z):
            for y in range(-1, 11):
                b.set(x, y, z, WALL)
            if z > 84:
                b.set(x, 11, z, 'smooth_quartz'); b.set(x, 12, z, 'diorite_wall' if (x + z) % 4 else 'smooth_quartz'); b.set(x, 13, z, 'smooth_quartz_slab')
        elif ring1(x, z):
            b.set(x, -1, z, 'oak_planks')
            for y in range(0, 10):
                b.set(x, y, z, CREAM)
            b.set(x, 0, z, TRIM); b.set(x, 9, z, TRIM); b.set(x, 5, z, 'smooth_sandstone_slab[type=top]') if False else None
            b.set(x, 10, z, WALL)
            if z > 84:
                b.set(x, 11, z, 'smooth_quartz')
        elif inside(x, z):
            b.set(x, -1, z, 'oak_planks' if (x + z) % 2 else 'spruce_planks')
            for y in range(0, 10):
                b.set(x, y, z, 'air')
            e = ev(x, z, AI, BI)
            b.set(x, 10, z, 'shroomlight' if 0.62 < e <= 0.78 else 'smooth_quartz')     # warm cove light ring
            if z > 84:
                b.set(x, 11, z, 'smooth_quartz')
# ceiling plaster seal medallion (seen from below): white ring, blue field, gold eagle
for x in range(CX - 4, CX + 5):
    for z in range(CZ - 4, CZ + 5):
        d = math.hypot(x - CX, z - CZ)
        if d <= 3.6:
            b.set(x, 10, z, 'white_concrete' if d > 2.7 else 'blue_concrete')
EAGLE = ["..Y..",
         "Y.Y.Y",
         "YYRYY",
         ".YYY.",
         "Y...Y"]
SZ = CZ + 1
for j, row in enumerate(EAGLE):
    for i, ch in enumerate(row):
        if ch != '.':
            pass
for j, row in enumerate([".Y.", "YYY", "Y.Y"]):          # small gold eagle in the ceiling medallion
    for i, ch in enumerate(row):
        if ch == 'Y':
            b.set(CX - 1 + i, 10, CZ - 1 + j, 'gold_block')
b.set(CX, 9, CZ, 'iron_chain') if False else None

# ---- 3. doors (four, through both wall layers) + eagle over the hallway door
def door_through(a_deg, width=2, h=3, frame=True, eagle=False):
    a = math.radians(a_deg)
    ux, uz = math.cos(a), math.sin(a)
    px, pz = -uz, ux
    cells = set()
    for k in range(0, 40):
        s = 0.8 + k * 0.02
        bx, bz = CX + ux * AI * s, CZ + uz * BI * s
        for w in range(width):
            off = w - (width - 1) / 2
            cx_, cz_ = round(bx + px * off), round(bz + pz * off)
            if not inside(cx_, cz_):
                cells.add((cx_, cz_))
    for (x, z) in cells:
        for y in range(0, h):
            b.set(x, y, z, 'air')
        b.set(x, -1, z, 'oak_planks')
        if frame:
            b.set(x, h, z, 'chiseled_quartz_block' if ring1(x, z) else b.get(x, h, z) or WALL)
    if eagle:
        r1 = [c for c in cells if ring1(*c)]
        for (x, z) in r1:
            b.set(x, h + 1, z, 'gold_block'); b.set(x, h + 2, z, 'yellow_terracotta')
    return cells
DOOR_HALL = door_through(232, eagle=True)      # NW: West Wing hallway
DOOR_SEC = door_through(308)                   # NE: President's secretary
DOOR_STUDY = door_through(180)                 # W : private study & dining room
DOOR_GARDEN = door_through(0, width=3)         # E : Rose Garden colonnade
for (x, z) in DOOR_GARDEN:
    b.set(x, -1, z, 'smooth_sandstone') if x >= 29 else None
for x in range(29, 34):
    for z in range(85, 90):
        if not ring2(x, z) and not ring1(x, z) and not inside(x, z):
            b.set(x, -1, z, 'smooth_sandstone')
            for y in range(0, 3):
                b.set(x, y, z, 'air')

# ---- 4. rooms around the oval: NW hallway, NE secretary, W study + private dining room
def carve(x1, x2, z1, z2, floor='polished_diorite', h=9):
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            if inside(x, z) or ring1(x, z) or ring2(x, z):
                continue
            for y in range(0, h):
                b.set(x, y, z, 'air')
            b.set(x, -1, z, floor)
carve(9, 16, 75, 84)          # hallway (from the West Wing corridor door at x 8, z 79..81)
carve(22, 28, 75, 82)         # secretary
carve(9, 12, 86, 91)          # private study + dining
b.box(9, 0, 85, 12, 8, 85, WALL)
for x in range(9, 13):
    b.set(x, 9, 85, WALL)
b.carpet(9, 75, 12, 84, 0, 'red', border='yellow')
for (x, z) in [(10, 76), (11, 76)]:
    b.set(x, 8, z, 'lantern[hanging=true]')
b.set(14, 8, 76, 'lantern[hanging=true]')
b.sign(9, 2, 75, ['', 'To the', 'Oval Office', '-->'], 'south') if False else b.sign(12, 3, 75, ['', 'THE OVAL', 'OFFICE', ''], 'south')
# secretary: desk + computer, door to the Cabinet Room
b.carpet(22, 75, 28, 82, 0, 'light_blue')
b.set(26, 0, 76, 'spruce_slab[type=top]'); b.set(26, 1, 76, 'black_stained_glass_pane'); b.chair(26, 0, 77, 'north', 'spruce_stairs')
b.set(28, 0, 79, 'potted_fern'); b.set(25, 8, 78, 'lantern[hanging=true]')
b.box(27, 0, 74, 28, 2, 74, 'air')
b.sign(23, 2, 75, ['', "President's", 'Secretary', ''], 'south') if False else None
# study + private dining
b.carpet(9, 86, 12, 92, 0, 'green')
b.long_table(10, 89, 11, 90, 0, 'dark_oak_slab')
b.chair(10, 0, 88, 'south', 'dark_oak_stairs'); b.chair(11, 0, 91, 'north', 'dark_oak_stairs') if False else b.chair(10, 0, 91, 'north', 'dark_oak_stairs')
b.bookshelves(9, 0, 91, 12, 2, 91); b.set(12, 0, 86, 'spruce_slab[type=top]'); b.set(12, 1, 86, 'lantern')
b.set(10, 8, 89, 'lantern[hanging=true]')
b.sign(9, 3, 86, ['', 'Private Study', '& Dining Room', ''], 'east') if False else None

# ---- 5. walls: built-in bookcases flanking the fireplace, niches with busts, drapes at the three south windows
def ring_cells(a0, a1, layer=1):
    out = []
    for x in range(X1 - 1, X2 + 1):
        for z in range(Z1, Z2 + 1):
            if (ring1(x, z) if layer == 1 else ring2(x, z)):
                a = ang(x, z)
                if (a0 <= a <= a1) or (a0 > a1 and (a >= a0 or a <= a1)):
                    out.append((x, z))
    return out
for (a0, a1) in [(244, 258), (282, 296)]:                 # bookcases
    for (x, z) in ring_cells(a0, a1):
        for y in range(0, 6):
            b.set(x, y, z, 'bookshelf')
        b.set(x, 6, z, TRIM)
for a in (150, 30):                                         # niches with busts
    for (x, z) in ring_cells(a - 4, a + 4):
        b.set(x, 0, z, 'quartz_pillar'); b.set(x, 1, z, f'skeleton_skull[rotation={4 if a > 90 else 12}]')
        for y in (2, 3):
            b.set(x, y, z, 'air')
        b.set(x, 4, z, 'smooth_sandstone_stairs[facing=%s,half=top]' % ('west' if a > 90 else 'east')) if False else b.set(x, 4, z, TRIM)
for a in (204, 336):                                        # art niches (gold-framed)
    for (x, z) in ring_cells(a - 3, a + 3):
        b.set(x, 3, z, 'yellow_glazed_terracotta'); b.set(x, 4, z, 'orange_glazed_terracotta')
# three tall south windows with gold drapes and valances
for a in (68, 90, 112):
    for layer in (1, 2):
        for (x, z) in ring_cells(a - 5, a + 5, layer):
            for y in range(1, 8):
                b.set(x, y, z, 'glass_pane')
    for side in (-1, 1):
        for (x, z) in ring_cells(a + side * 8 - 2, a + side * 8 + 2):
            for y in range(1, 9):
                b.set(x, y, z, 'yellow_wool')
    for (x, z) in ring_cells(a - 6, a + 6):
        b.set(x, 8, z, 'yellow_wool')

# ---- 6. fireplace (north) with mantel; portrait above
FZ = CZ - 9                                  # 78: inner wall at the north tip
for x in range(CX - 2, CX + 3):
    for y in range(0, 3):
        b.set(x, y, FZ, 'white_concrete')
    b.set(x, 3, FZ + 1, 'smooth_quartz_slab[type=bottom]')      # mantel shelf
    b.set(x, 3, FZ, 'white_concrete')
b.set(CX, 0, FZ, 'campfire[lit=true,signal_fire=false]'); b.set(CX, 1, FZ, 'air')
b.set(CX, 0, FZ - 1, 'white_concrete'); b.set(CX, 1, FZ - 1, 'white_concrete')
for x in range(CX - 1, CX + 2):
    for y in range(4, 10):
        b.set(x, y, FZ, 'smooth_quartz')
b.set(CX - 2, 4, FZ + 1, 'candle[lit=true,candles=3]') if False else None
b.set(CX - 2, 4, FZ, 'white_concrete'); b.set(CX + 2, 4, FZ, 'white_concrete')
b.painting(CX, 5, FZ + 1, 'south', 'minecraft:wanderer')     # portrait over the mantel
b.set(CX - 2, 4, FZ + 1, 'candle[lit=true,candles=2]'); b.set(CX + 2, 4, FZ + 1, 'candle[lit=true,candles=2]')
# armchairs either side of the fireplace (facing each other) + side tables
b.chair(CX - 2, 0, FZ + 2, 'east', 'smooth_sandstone_stairs'); b.chair(CX + 2, 0, FZ + 2, 'west', 'smooth_sandstone_stairs')

# ---- 7. floor: dark blue oval rug with gold border and the Presidential Seal
for x in range(X1, X2):
    for z in range(Z1, Z2):
        if not inside(x, z):
            continue
        e = ev(x, z, 5.8, 7.2)
        if e <= 1:
            c = 'yellow' if e > 0.78 else 'blue'
            d = math.hypot(x - CX, z - SZ)
            if 2.9 < d <= 3.8 and c == 'blue':
                c = 'white'
            b.set(x, 0, z, f'{c}_carpet')
for j, row in enumerate(EAGLE):                 # gold eagle with red/white shield
    for i, ch in enumerate(row):
        if ch == 'Y':
            b.set(CX - 2 + i, 0, SZ - 2 + j, 'yellow_carpet')
        elif ch == 'R':
            b.set(CX - 2 + i, 0, SZ - 2 + j, 'red_carpet')
for (dx, dz) in [(0, -4), (3, -3), (4, 0), (3, 3), (0, 4), (-3, 3), (-4, 0), (-3, -3)]:   # stars in the white ring
    b.set(CX + dx, 0, CZ + dz, 'light_gray_carpet') if False else None

# ---- 8. the Resolute Desk before the south windows, the President's chair, flags
DZ = CZ + 6                                   # 93
for x in range(CX - 2, CX + 3):
    b.set(x, 0, DZ, 'dark_oak_planks' if abs(x - CX) == 2 else 'stripped_dark_oak_wood')
    b.set(x, 1, DZ, 'dark_oak_pressure_plate') if False else None
b.set(CX, 0, DZ, 'dark_oak_trapdoor[facing=north,half=bottom,open=true]')      # the presidential kneehole panel
b.box(CX - 2, 1, DZ, CX + 2, 1, DZ, 'brown_carpet')
b.set(CX - 2, 1, DZ, 'lantern'); b.set(CX + 2, 1, DZ, 'potted_white_tulip')
b.set(CX, 0, DZ + 1, 'spruce_stairs[facing=south,half=bottom]')                  # chair, sitter faces north
b.set(CX + 2, 0, DZ + 1, 'dark_oak_slab[type=top]'); b.set(CX + 2, 1, DZ + 1, 'decorated_pot')
b.set(CX - 3, 0, DZ + 2, 'white_banner[rotation=8]', nbt=FLAG_NBT)               # US flag
b.set(CX + 3, 0, DZ + 2, 'blue_banner[rotation=8]',                                # President's flag
      nbt='{patterns:[{pattern:"minecraft:border",color:"white"},{pattern:"minecraft:circle",color:"white"},{pattern:"minecraft:flower",color:"yellow"}]}')
for (x, z) in [(CX - 4, DZ + 1), (CX + 4, DZ + 1)]:
    b.set(x, 0, z, 'potted_fern') if inside(x, z) else None
# sofas facing each other across the coffee table (cream), lamps on side tables at their ends
b.sofa(CX - 4, 0, 82, 'east', 4, 'smooth_sandstone_stairs', None)
b.sofa(CX + 4, 0, 85, 'west', 4, 'smooth_sandstone_stairs', None)
for (x, z) in [(CX - 4, 81), (CX - 4, 86), (CX + 4, 81), (CX + 4, 86)]:
    b.set(x, 0, z, 'dark_oak_slab[type=top]'); b.set(x, 1, z, 'lantern')
b.box(CX - 1, 0, 83, CX + 1, 0, 84, 'dark_oak_slab[type=top]')               # coffee table
b.set(CX, 1, 83, 'potted_red_tulip'); b.set(CX - 1, 1, CZ - 1, 'decorated_pot') if False else None
# Remington-style bronze on a side table behind the west sofa; grandfather clock; more side tables
b.set(CX - 5, 0, CZ, 'dark_oak_slab[type=top]'); b.set(CX - 5, 1, CZ, 'exposed_cut_copper_stairs[facing=north]')
b.set(CX + 5, 0, CZ, 'dark_oak_slab[type=top]'); b.set(CX + 5, 1, CZ, 'lantern')
gx, gz = CX - 6, CZ - 3
b.set(gx, 0, gz, 'dark_oak_planks'); b.set(gx, 1, gz, 'dark_oak_planks'); b.set(gx, 2, gz, 'dark_oak_planks'); b.set(gx, 3, gz, 'dark_oak_slab')
b.sign(gx, 2, gz + 1, ['', 'XII', 'IX   III', 'VI'], 'south')
# a few chairs facing the desk for visitors

# exterior name plates
b.sign(30, 3, 84, ['', 'THE OVAL', 'OFFICE', ''], 'east')
