exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\whitehouse\lib.py").read())
# Executive Residence interiors (local view r: rx 0..84, rz 0..42)
r = b.at(RX0, 0, RZ0)
PW = 'smooth_quartz'        # partition walls
MARBLE = {'polished_diorite': 1, 'calcite': 1}

def wx(x, z1, z2, y1, y2, blk=PW):        # wall along z at x
    r.box(x, y1, min(z1, z2), x, y2, max(z1, z2), blk)
def wz(z, x1, x2, y1, y2, blk=PW):        # wall along x at z
    r.box(min(x1, x2), y1, z, max(x1, x2), y2, z, blk)
def opening(x1, z1, x2, z2, y, h=3):
    r.box(x1, y, z1, x2, y + h - 1, z2, 'air')
def label(x, y, z, lines, facing):
    r.sign(x, y, z, lines, facing)
def chandelier(x, z, ytop, big=True):
    r.set(x, ytop, z, 'iron_chain'); r.set(x, ytop - 1, z, 'iron_chain')
    y = ytop - 2
    r.set(x, y, z, 'gold_block')
    arms = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if big:
        arms += [(2, 0), (-2, 0), (0, 2), (0, -2)]
    for dx, dz in arms:
        r.set(x + dx, y, z + dz, 'gold_block' if abs(dx) + abs(dz) == 1 else 'end_rod[facing=up]')
    for dx, dz in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
        r.set(x + dx, y, z + dz, 'glowstone')
    for dx, dz in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        r.set(x + dx, y - 1, z + dz, 'lantern[hanging=true]')
    r.set(x, y - 1, z, 'iron_chain'); r.set(x, y - 2, z, 'glowstone')
def ceiling_lights(x1, z1, x2, z2, y, step=6):
    for x in range(x1, x2 + 1, step):
        for z in range(z1, z2 + 1, step):
            r.set(x, y, z, 'lantern[hanging=true]')
def oval(cx, cz, ax, az, y1, y2, wall, floor_y, carpet=None, border=None):
    for x in range(int(cx - ax - 1), int(cx + ax + 2)):
        for z in range(int(cz - az - 1), int(cz + az + 2)):
            e = ((x - cx) / (ax + .5)) ** 2 + ((z - cz) / (az + .5)) ** 2
            ei = ((x - cx) / (ax - .5)) ** 2 + ((z - cz) / (az - .5)) ** 2
            if e <= 1 and ei > 1:
                r.box(x, y1, z, x, y2, z, wall)
            elif ei <= 1:
                r.box(x, y1, z, x, y2, z, 'air')
                if carpet:
                    eb = ((x - cx) / (ax - 1.5)) ** 2 + ((z - cz) / (az - 1.5)) ** 2
                    r.set(x, floor_y + 1, z, f'{border if (border and eb > 1) else carpet}_carpet')
def curtains(face, c, y1=9, y2=15, color='yellow'):
    # gold curtains either side of a 3-wide window at u=c on the inner face
    m = {'n': lambda u: (u, 1), 's': lambda u: (u, 41), 'w': lambda u: (1, u), 'e': lambda u: (83, u)}[face]
    for u in (c - 2, c + 2):
        x, z = m(u)
        for y in range(y1, y2 + 1):
            r.set(x, y, z, f'{color}_wool')
    for u in range(c - 1, c + 2):
        x, z = m(u)
        r.set(x, y2, z, f'{color}_wool')
def fireplace(x, z, y, facing):
    # facing = direction the fire faces into the room
    dx, dz = DIRS[facing]
    px, pz = DIRS[right_of(facing)]
    for k in (-1, 0, 1):
        r.set(x + px * k, y, z + pz * k, 'white_concrete' if k else 'campfire[lit=true,signal_fire=false]')
        r.set(x + px * k, y + 1, z + pz * k, 'white_concrete' if k else 'air')
        r.set(x + px * k + dx, y + 2, z + pz * k + dz, f'smooth_quartz_slab[type=bottom]')
    r.set(x, y + 2, z, 'white_concrete'); r.set(x - px * 2, y, z - pz * 2, 'white_concrete')
    r.set(x + px * 2, y, z + pz * 2, 'white_concrete')
    for yy in range(y + 3, y + 7):
        r.set(x, yy, z, 'white_concrete')

# ===================================================================== GROUND FLOOR (y 0..6)
G = 0
r.box(1, -1, 1, 83, -1, 41, MARBLE)
for x in range(1, 84):                                      # Center Hall with red runner
    for z in range(18, 21):
        r.set(x, 0, z, 'red_carpet')
wz(17, 1, 83, 0, 6); wz(21, 1, 83, 0, 6)
for x in range(4, 84, 8):                                   # groin-vault ribs
    r.box(x, 6, 18, x, 6, 20, 'smooth_quartz_stairs[facing=east,half=top]')
ceiling_lights(6, 19, 80, 19, 6, 8)
# north side rooms: kitchen (W), service stair, ushers, storage (E)
wx(19, 1, 16, 0, 6); wx(25, 1, 16, 0, 6); wx(60, 1, 16, 0, 6)
opening(10, 17, 12, 17, 0); opening(22, 17, 23, 17, 0, 3); opening(40, 17, 44, 17, 0); opening(70, 17, 72, 17, 0)
r.box(2, 0, 2, 2, 0, 12, 'smooth_stone_slab[type=top]'); r.kitchen(2, 1, 2, 'east', 1)
for z in range(2, 15, 3):
    r.set(2, 0, z, 'smoker[facing=east]'); r.set(2, 0, z + 1, 'furnace[facing=east]'); r.set(2, 0, z + 2, 'water_cauldron[level=3]')
r.long_table(7, 6, 15, 10, 0, 'smooth_stone_slab'); r.box(7, -1, 6, 15, -1, 10, 'smooth_stone')
label(14, 2, 18, ['', 'White House', 'Kitchen', ''], 'south')
r.bookshelves(26, 0, 1, 58, 1, 1)
for x in range(28, 58, 6):
    r.set(x, 0, 8, 'barrel[facing=up]'); r.set(x + 1, 0, 8, 'barrel[facing=up]')
for x in range(62, 83, 4):
    r.long_table(x, 3, x + 1, 12, 0, 'dark_oak_slab')
label(68, 2, 18, ['', 'China Room', '', ''], 'south')
# south side rooms
wx(19, 22, 41, 0, 6); wx(31, 22, 41, 0, 6); wx(53, 22, 41, 0, 6); wx(65, 22, 41, 0, 6)
opening(10, 21, 12, 21, 0); opening(24, 21, 26, 21, 0); opening(58, 21, 60, 21, 0); opening(73, 21, 75, 21, 0)
r.bookshelves(20, 0, 23, 30, 4, 23); r.bookshelves(20, 0, 24, 20, 4, 40)       # Library
r.carpet(22, 26, 29, 38, 0, 'brown', border='orange'); r.long_table(24, 30, 27, 33, 0, 'dark_oak_slab')
r.chair(25, 0, 29, 'south'); r.chair(26, 0, 34, 'north')
label(28, 2, 20, ['', 'Library', '', ''], 'north')
r.carpet(55, 24, 63, 40, 0, 'gray', border='light_gray'); r.long_table(57, 30, 61, 33, 0, 'spruce_slab')  # Map Room
r.set(59, 1, 30, 'light_gray_banner[rotation=0]'); label(62, 2, 20, ['', 'Map Room', '', ''], 'north')
r.carpet(67, 23, 82, 40, 0, 'yellow', border='orange')                        # Vermeil / East Garden Room
r.sofa(70, 0, 28, 'south', 3); r.sofa(78, 0, 36, 'north', 3) if False else r.sofa(72, 0, 36, 'north', 3)
label(77, 2, 20, ['', 'Vermeil Room', '', ''], 'north')
r.carpet(2, 23, 18, 40, 0, 'green', border='lime')                            # Palm / West Garden Room
for (x, z) in [(3, 24), (17, 24), (3, 39), (17, 39)]:
    r.plant(x, 0, z, 'potted_fern')
label(14, 2, 20, ['', 'Palm Room', '', ''], 'north')
# Diplomatic Reception Room (oval) under the Blue Room - South Lawn entrance
oval(42, 33, 9, 7, 0, 6, 'light_gray_terracotta', -1, carpet='light_blue', border='yellow')
opening(41, 41, 43, 42, 0, 4); opening(41, 25, 43, 26, 0, 3)
r.box(32, 0, 22, 52, 6, 24, PW); opening(41, 22, 43, 26, 0, 3)
r.sofa(37, 0, 30, 'east', 3); r.sofa(47, 0, 34, 'west', 3)
chandelier(42, 33, 6, big=False)
label(38, 2, 20, ['', 'Diplomatic', 'Reception Room', ''], 'north')
# ground -> state service stair (rx 21..23, climbing north from rz 12 to rz 6)
for i in range(7):
    for x in range(21, 24):
        r.set(x, i, 12 - i, 'quartz_stairs[facing=north]')
        for yy in range(0, i):
            r.set(x, yy, 12 - i, 'quartz_bricks')
r.box(21, 7, 6, 23, 7, 11, 'air')
r.box(20, 0, 13, 24, 6, 16, 'air')

# ===================================================================== STATE FLOOR (y 8..17)
S0 = 8
r.box(1, 7, 1, 83, 7, 41, MARBLE)
# Entrance Hall (rx 26..58, rz 1..15), checkerboard marble, column screen at rz 16
for x in range(26, 59):
    for z in range(1, 16):
        r.set(x, 7, z, 'polished_diorite' if (x + z) % 2 else 'polished_andesite')
wx(25, 1, 16, 8, 17); wx(59, 1, 16, 8, 17)
for x in range(26, 59, 4):
    r.box(x, 8, 16, x, 17, 16, 'quartz_pillar')
r.carpet(41, 1, 43, 15, 8, 'red')
chandelier(42, 8, 17)
label(38, 11, 1, ['', 'Entrance Hall', '', ''], 'south')
# Cross Hall (rx 19..65, rz 17..21) red carpet
for x in range(19, 66):
    for z in range(17, 22):
        r.set(x, 7, z, 'polished_diorite' if (x // 2 + z) % 2 else 'calcite')
r.carpet(19, 18, 65, 20, 8, 'red', border=None)
for x in (27, 42, 57):
    chandelier(x, 19, 17, big=False)
wz(22, 19, 65, 8, 17)
for x in range(20, 65, 4):
    r.box(x, 8, 21, x, 17, 21, 'quartz_pillar') if x not in (40, 44) else None
# East Room (rx 66..83, full depth)
wx(65, 1, 41, 8, 17)
opening(65, 18, 65, 20, 8, 5); opening(65, 9, 65, 11, 8, 5); opening(65, 30, 65, 32, 8, 4)
for x in range(66, 84):
    for z in range(1, 42):
        r.set(x, 7, z, 'oak_planks' if (x + z // 2) % 2 else 'spruce_planks')
for z in (9, 21, 33):
    chandelier(74, z, 17, big=True)
for c in (6, 13, 21, 29, 36):
    curtains('e', c)
for c in (72, 78):
    curtains('n', c); curtains('s', c)
r.box(80, 8, 4, 82, 8, 6, 'black_concrete'); r.set(80, 9, 4, 'black_carpet'); r.set(79, 8, 5, 'dark_oak_stairs[facing=east]')  # piano
r.set(81, 9, 5, 'black_carpet'); r.set(82, 9, 6, 'black_carpet')
fireplace(66, 15, 8, 'east') if False else None
fireplace(83, 25, 8, 'west')
for z in (15, 27):
    r.painting(66, 12, z, 'east', 'minecraft:kebab') if False else None
label(64, 13, 19, ['', 'East Room', '', ''], 'west')
for z in range(4, 39, 3):
    r.chair(67, 8, z, 'east', 'birch_stairs') if z % 2 else None
# Grand Staircase (rx 60..64, rz 1..16): climbs north from rz 15 to rz 6, up to the second floor
r.box(60, 7, 1, 64, 7, 16, 'polished_diorite')
for i in range(10):
    for x in range(61, 64):
        r.set(x, 8 + i, 15 - i, 'red_carpet' if False else 'quartz_stairs[facing=north]')
        for yy in range(8, 8 + i):
            r.set(x, yy, 15 - i, 'quartz_bricks')
r.box(61, 18, 6, 63, 18, 14, 'air')
for z in range(4, 16):
    r.set(60, 8 + max(0, 15 - z), z, 'smooth_quartz') if False else None
opening(59, 8, 59, 12, 8, 4)
label(60, 11, 13, ['', 'Grand', 'Staircase', ''], 'east')
# Usher's office (rx 20..24) with the service stair hole; Family Dining Room (rx 1..18, rz 1..15)
wx(19, 1, 41, 8, 17); wz(16, 1, 18, 8, 17)
opening(19, 18, 19, 20, 8, 4); opening(19, 8, 19, 10, 8, 3); opening(10, 16, 12, 16, 8, 3)
r.box(20, 8, 4, 24, 8, 4, 'air') if False else None
r.box(20, 7, 5, 24, 7, 12, 'polished_diorite'); r.box(21, 7, 6, 23, 7, 11, 'air')
for x in (20, 24):
    for z in range(5, 12):
        r.set(x, 8, z, 'diorite_wall')
r.long_table(6, 6, 13, 9, 8, 'dark_oak_slab')
for x in range(6, 14):
    r.chair(x, 8, 5, 'south', 'dark_oak_stairs'); r.chair(x, 8, 10, 'north', 'dark_oak_stairs')
chandelier(9, 8, 17, big=False)
label(11, 10, 15, ['', 'Family', 'Dining Room', ''], 'north')
# State Dining Room (rx 1..18, rz 17..41)
for x in range(1, 19):
    for z in range(17, 42):
        r.set(x, 7, z, 'oak_planks' if (x + z) % 2 else 'birch_planks')
r.carpet(3, 20, 16, 39, 8, 'light_gray', border='yellow')
r.long_table(8, 22, 10, 37, 8, 'spruce_slab')
for z in range(22, 38):
    r.chair(7, 8, z, 'east', 'dark_oak_stairs'); r.chair(11, 8, z, 'west', 'dark_oak_stairs')
r.chair(9, 8, 21, 'south', 'dark_oak_stairs'); r.chair(9, 8, 38, 'north', 'dark_oak_stairs')
for z in (24, 35):
    chandelier(9, z, 17, big=True)
fireplace(1, 29, 8, 'east')
r.painting(2, 13, 29, 'east', 'minecraft:wanderer')
for z in range(24, 36, 3):
    r.set(9, 9, z, 'candle[lit=true,candles=3]')
for c in (6, 12):
    curtains('s', c, color='yellow')
label(20, 13, 19, ['', 'State', 'Dining Room', ''], 'east')
# Red Room (rx 20..30), Blue Room (oval, rx 33..51), Green Room (rx 54..64)
wx(31, 23, 41, 8, 17); wx(53, 23, 41, 8, 17)
opening(24, 22, 26, 22, 8, 4); opening(41, 22, 43, 22, 8, 4); opening(58, 22, 60, 22, 8, 4)
opening(31, 30, 31, 32, 8, 3); opening(53, 30, 53, 32, 8, 3)
for z in range(23, 42):                      # Red Room fabric walls
    r.box(20, 8, z, 20, 15, z, 'red_wool')
for x in range(21, 31):
    r.box(x, 8, 23, x, 15, 23, 'red_wool')
r.carpet(21, 24, 30, 40, 8, 'red', border='yellow')
r.sofa(23, 8, 38, 'north', 4, 'red_terracotta' if False else 'mangrove_stairs', 'mangrove_trapdoor')
r.table(26, 8, 33); r.chair(24, 8, 33, 'east', 'mangrove_stairs'); r.chair(28, 8, 33, 'west', 'mangrove_stairs')
chandelier(25, 32, 17, big=False)
label(25, 12, 21, ['', 'Red Room', '', ''], 'north')
for z in range(23, 42):                      # Green Room
    r.box(64, 8, z, 64, 15, z, 'green_wool')
for x in range(54, 64):
    r.box(x, 8, 23, x, 15, 23, 'green_wool')
r.carpet(54, 24, 63, 40, 8, 'green', border='lime')
r.sofa(56, 8, 38, 'north', 4, 'birch_stairs', 'birch_trapdoor')
r.table(59, 8, 32); r.chair(57, 8, 32, 'east', 'birch_stairs'); r.chair(61, 8, 32, 'west', 'birch_stairs')
chandelier(59, 31, 17, big=False)
label(59, 12, 21, ['', 'Green Room', '', ''], 'north')
r.box(32, 8, 23, 52, 17, 41, PW)            # fill between oval and rectangle, then carve the oval
oval(42, 33, 9, 8, 8, 17, 'blue_terracotta', 7, carpet='light_blue', border='yellow')
for x in range(33, 52):
    for z in range(24, 42):
        e = ((x - 42) / 8.5) ** 2 + ((z - 33) / 7.5) ** 2
        if e <= 1:
            r.set(x, 17, z, 'smooth_quartz')
opening(41, 23, 43, 25, 8, 4)               # door from the Cross Hall
opening(32, 30, 33, 32, 8, 3); opening(51, 30, 52, 32, 8, 3)
opening(41, 40, 43, 42, 8, 4)               # doors onto the South Portico
r.box(41, 12, 41, 43, 14, 41, 'glass_pane')
r.table(42, 8, 33, 'gold_block' if False else 'dark_oak_fence', 'yellow_carpet'); r.set(42, 10, 33, 'potted_red_tulip') if False else None
for (x, z, f) in [(39, 30, 'south'), (45, 30, 'south'), (39, 36, 'north'), (45, 36, 'north'), (37, 33, 'east'), (47, 33, 'west')]:
    r.chair(x, 8, z, f, 'birch_stairs')
chandelier(42, 33, 16, big=True)
label(42, 12, 21, ['', 'Blue Room', '', ''], 'north')

# ===================================================================== SECOND FLOOR - residence (y 19..25)
r.box(1, 18, 1, 83, 18, 41, 'oak_planks')
r.box(61, 18, 6, 63, 18, 14, 'air')         # grand staircase well
r.box(21, 18, 5, 23, 18, 11, 'oak_planks')  # (service stair stops at the state floor)
for z in range(6, 15):
    r.set(60, 19, z, 'diorite_wall'); r.set(64, 19, z, 'diorite_wall')
# Center Hall rz 17..22
wz(16, 1, 83, 19, 25); wz(23, 1, 83, 19, 25)
r.carpet(1, 18, 83, 21, 19, 'yellow', border='orange')
ceiling_lights(6, 19, 80, 19, 25, 8)
opening(61, 16, 63, 16, 19, 3)              # stair arrives into the hall
for x in range(59, 66):
    for z in range(1, 16):
        if not (61 <= x <= 63 and 6 <= z <= 14):
            r.set(x, 18, z, 'oak_planks')
wx(59, 1, 15, 19, 25); wx(66, 1, 15, 19, 25)
# north rooms (rz 1..15): family kitchen, bedrooms, third-floor stair hall, Queens' Bedroom
for x in (14, 30, 51):
    wx(x, 1, 15, 19, 25)
r.kitchen(2, 19, 2, 'south', 6); r.long_table(5, 7, 9, 9, 19, 'birch_slab')
for x in range(5, 10):
    r.chair(x, 19, 6, 'south', 'birch_stairs'); r.chair(x, 19, 10, 'north', 'birch_stairs')
opening(7, 16, 8, 16, 19, 3); label(10, 21, 17, ['', 'Family', 'Kitchen', ''], 'south')
def bedroom(x1, z1, x2, z2, y, color, door, title, bed_at, facing):
    opening(door[0], door[1], door[0] + (1 if door[2] == 'x' else 0), door[1] + (1 if door[2] == 'z' else 0), y, 3)
    r.carpet(x1, z1, x2, z2, y, color)
    bx, bz = bed_at
    px, pz = DIRS[right_of(facing)]
    r.bed(bx, y, bz, facing, color if color not in ('light_gray',) else 'white')
    r.bed(bx + px, y, bz + pz, facing, color if color not in ('light_gray',) else 'white')
    r.set(bx - px, y, bz - pz, 'oak_trapdoor[half=top]') if False else r.set(bx - px, y, bz - pz, 'spruce_slab[type=top]')
    r.set(bx + 2 * px, y, bz + 2 * pz, 'spruce_slab[type=top]')
    r.set(bx - px, y + 1, bz - pz, 'lantern'); r.set(bx + 2 * px, y + 1, bz + 2 * pz, 'potted_azure_bluet')
    r.set((x1 + x2) // 2, 25, (z1 + z2) // 2, 'lantern[hanging=true]')
    if title:
        lx, lz, lf = title[1]
        label(door[0] + 3, 21, lz + (1 if lf == 'south' else -1), ['', title[0], '', ''], lf)
bedroom(15, 1, 29, 15, 19, 'light_blue', (22, 16, 'x'), ('Bedroom', (22, 16, 'south')), (22, 2), 'north')
bedroom(52, 1, 58, 15, 19, 'pink', (54, 16, 'x'), ('Bedroom', (54, 16, 'south')), (55, 2), 'north')
bedroom(67, 1, 83, 15, 19, 'pink', (74, 16, 'x'), ("Queens' Bedroom", (75, 16, 'south')), (75, 2), 'north')
for z in (2, 3):
    for x in (74, 77):
        r.set(x, 20, z, 'dark_oak_fence'); r.set(x, 21, z, 'dark_oak_fence')
r.box(74, 22, 2, 77, 22, 3, 'pink_wool')
# third-floor stair (rx 40..42 climbing north from rz 15 to rz 9) in the stair hall rx 31..50
opening(40, 16, 42, 16, 19, 3)
for i in range(7):
    for x in range(40, 43):
        r.set(x, 19 + i, 15 - i, 'oak_stairs[facing=north]')
        for yy in range(19, 19 + i):
            r.set(x, yy, 15 - i, 'oak_planks')
r.box(40, 26, 9, 42, 26, 14, 'air')
r.bookshelves(31, 19, 1, 50, 21, 1); r.sofa(33, 19, 8, 'east', 3); r.sofa(47, 19, 6, 'west', 3)
label(44, 21, 17, ['', 'Stairs to', 'Third Floor', ''], 'south')
# south rooms (rz 24..41)
for x in (14, 31, 53, 66):
    wx(x, 24, 41, 19, 25)
bedroom(1, 24, 13, 41, 19, 'blue', (7, 23, 'x'), ("President's", (7, 23, 'north')), (6, 39), 'south')
label(8, 22, 23, ['', 'Bedroom', '', ''], 'north') if False else None
opening(20, 23, 22, 23, 19, 3); label(24, 21, 22, ['', 'Private', 'Dining Room', ''], 'north')
r.carpet(15, 24, 30, 41, 19, 'light_gray', border='yellow'); r.long_table(20, 30, 25, 33, 19, 'dark_oak_slab')
for x in range(20, 26):
    r.chair(x, 19, 29, 'south', 'dark_oak_stairs'); r.chair(x, 19, 34, 'north', 'dark_oak_stairs')
r.chair(19, 19, 31, 'east', 'dark_oak_stairs'); r.chair(26, 19, 32, 'west', 'dark_oak_stairs')
for x in range(21, 25, 2):
    r.set(x, 20, 31, 'candle[lit=true,candles=3]')
r.kitchen(16, 19, 41, 'north', 5) if False else None
r.box(16, 19, 41, 29, 19, 41, 'dark_oak_slab[type=top]'); r.set(18, 20, 41, 'potted_white_tulip'); r.set(27, 20, 41, 'potted_white_tulip')
r.bookshelves(15, 19, 41, 30, 21, 41) if False else None
r.box(32, 19, 24, 52, 25, 41, PW)
oval(42, 33, 9, 8, 19, 25, 'yellow_terracotta', 18, carpet='yellow', border='orange')
opening(41, 23, 43, 25, 19, 3); opening(41, 40, 43, 42, 19, 3)
r.sofa(38, 19, 30, 'south', 3) if False else r.sofa(37, 19, 31, 'east', 3)
r.sofa(47, 19, 35, 'west', 3); r.table(42, 19, 33); chandelier(42, 33, 25, big=False)
label(45, 21, 22, ['', 'Yellow Oval', 'Room', ''], 'north')
r.carpet(54, 24, 65, 41, 19, 'green', border='lime'); r.long_table(57, 30, 62, 33, 19, 'dark_oak_slab')
for x in range(57, 63):
    r.chair(x, 19, 29, 'south', 'dark_oak_stairs'); r.chair(x, 19, 34, 'north', 'dark_oak_stairs')
opening(59, 23, 60, 23, 19, 3); label(62, 21, 22, ['', 'Treaty Room', '', ''], 'north')
# Lincoln Bedroom (rx 67..83, rz 24..41): carved rosewood bed, Gettysburg Address
opening(74, 23, 75, 23, 19, 3)
r.carpet(67, 24, 83, 41, 19, 'purple', border='yellow')
for x in (74, 75):
    r.bed(x, 19, 38, 'south', 'purple')
for (x, z) in [(73, 37), (76, 37), (73, 40), (76, 40)]:
    for yy in range(19, 23):
        r.set(x, yy, z, 'dark_oak_fence')
r.box(73, 23, 37, 76, 23, 40, 'dark_oak_slab')
r.box(73, 19, 41, 76, 22, 41, 'dark_oak_planks')
r.set(72, 19, 40, 'dark_oak_slab[type=top]'); r.set(72, 20, 40, 'lantern')
r.set(77, 19, 40, 'dark_oak_slab[type=top]'); r.set(77, 20, 40, 'lantern')
r.chair(69, 19, 27, 'south', 'dark_oak_stairs'); r.chair(71, 19, 27, 'south', 'dark_oak_stairs'); r.table(70, 19, 28)
r.set(68, 19, 30, 'lectern[facing=east]')
r.sign(67, 21, 32, ['Gettysburg', 'Address', '"Four score and', 'seven years ago"'], 'east')
r.sign(67, 21, 34, ['Lincoln', 'Bedroom', 'Lincoln Cabinet', 'Room 1861-65'], 'east')
r.set(75, 25, 32, 'lantern[hanging=true]')
label(77, 21, 22, ['', 'Lincoln', 'Bedroom', ''], 'north')
fireplace(83, 31, 19, 'west')

# ===================================================================== THIRD FLOOR (y 27..31)
r.box(6, 26, 6, 78, 26, 36, 'birch_planks')
r.box(40, 26, 9, 42, 26, 14, 'air')
opening(44, 18, 45, 18, 27, 3)
for x in (39, 43):
    for z in range(9, 15):
        r.set(x, 27, z, 'birch_fence')
wz(18, 6, 78, 27, 31, 'white_concrete'); wz(24, 6, 78, 27, 31, 'white_concrete')
r.carpet(6, 19, 78, 23, 27, 'light_gray')
for x in (18, 30, 54, 66):
    wx(x, 6, 17, 27, 31, 'white_concrete'); wx(x, 25, 36, 27, 31, 'white_concrete')
for (x1, x2) in [(6, 17), (19, 29), (55, 65), (67, 78)]:
    m = (x1 + x2) // 2
    opening(m, 18, m + 1, 18, 27, 3); opening(m, 24, m + 1, 24, 27, 3)
    r.bed(m, 27, 7, 'north', 'white'); r.bed(m, 27, 35, 'south', 'light_gray')
    r.set(m, 31, 12, 'lantern[hanging=true]'); r.set(m, 31, 30, 'lantern[hanging=true]')
# Solarium (south, rx 31..53) with glass
opening(41, 24, 43, 24, 27, 3)
r.box(31, 28, 37, 53, 30, 37, 'light_blue_stained_glass_pane')
r.carpet(31, 25, 53, 36, 27, 'white', border='light_blue')
r.sofa(35, 27, 33, 'south', 4); r.sofa(45, 27, 33, 'south', 4)
for x in (32, 52):
    r.plant(x, 27, 26, 'potted_bamboo')
label(45, 29, 23, ['', 'Solarium', '', ''], 'north')
ceiling_lights(10, 21, 76, 21, 31, 10)
for x in range(31, 54, 7):
    r.set(x, 31, 30, 'lantern[hanging=true]')

# ===================================================================== extra furnishing pass
# East Room: grand piano (black wool + quartz keys), portraits
r.box(79, 8, 3, 82, 8, 6, 'air'); r.box(80, 8, 3, 82, 8, 5, 'black_wool'); r.set(80, 8, 6, 'black_wool')
r.box(80, 9, 3, 82, 9, 4, 'black_carpet'); r.box(79, 8, 3, 79, 8, 5, 'quartz_slab[type=top]'); r.set(78, 8, 4, 'dark_oak_stairs[facing=west]')
for (z, v) in [(4, 'minecraft:graham'), (14, 'minecraft:wanderer'), (24, 'minecraft:graham'), (36, 'minecraft:wanderer')]:
    r.painting(66, 12, z, 'east', v)
for z in (2, 40):
    r.plant(82, 8, z, 'potted_fern')
# Red & Green Rooms: fireplaces with mantels + portraits
fireplace(21, 32, 8, 'east'); r.painting(21, 13, 27, 'east', 'minecraft:wanderer'); r.painting(21, 13, 37, 'east', 'minecraft:graham')
fireplace(63, 32, 8, 'west'); r.painting(63, 13, 27, 'west', 'minecraft:wanderer'); r.painting(63, 13, 37, 'west', 'minecraft:graham')
for (x, z) in [(22, 25), (29, 25), (55, 25), (62, 25)]:
    r.plant(x, 8, z, 'potted_red_tulip' if x < 40 else 'potted_fern')
# State Dining Room: Lincoln portrait over the fireplace (already), candelabras on sideboards
for z in (19, 40):
    r.box(5, 8, z, 13, 8, z, 'dark_oak_slab[type=top]')
    for x in (6, 9, 12):
        r.set(x, 9, z, 'candle[lit=true,candles=4]')
# Blue Room: gilded chairs ring (gold accents)
for (x, z) in [(40, 31), (44, 31), (40, 35), (44, 35)]:
    r.set(x, 8, z, 'gold_block' if False else 'birch_stairs[facing=%s]' % ('south' if z < 33 else 'north'))
r.set(42, 9, 33, 'potted_blue_orchid') if False else None
# Cross Hall lanterns on the columns
for x in range(20, 65, 8):
    r.set(x, 14, 17, 'lantern') if False else None
# Bathrooms (cauldron sinks, quartz tubs) on the second and third floors
def bathroom(x1, z1, x2, z2, y, door, dface):
    r.box(x1, y - 1, z1, x2, y - 1, z2, 'smooth_quartz')
    r.box(x1, y, z1, x2, y + 5, z2, 'air')
    for x in (x1 - 1, x2 + 1):
        r.box(x, y, z1 - 1, x, y + 5, z2 + 1, PW)
    for z in (z1 - 1, z2 + 1):
        r.box(x1 - 1, y, z, x2 + 1, y + 5, z, PW)
    r.box(door[0], y, door[1], door[0], y + 2, door[1], 'air')
    r.set(x1, y, z1, 'water_cauldron[level=3]'); r.set(x1 + 1, y, z1, 'smooth_quartz_slab[type=top]')
    r.set(x2, y, z2, 'quartz_stairs[facing=north]') if False else r.set(x2, y, z2, 'quartz_stairs[facing=%s]' % dface)
    r.box(x1, y, z2, x1 + 1, y, z2, 'smooth_quartz_slab[type=bottom]')
    r.set(x1, y + 2, z1 + 1 if z1 + 1 <= z2 else z1, 'glass_pane')
    r.set((x1 + x2) // 2, y + 5, (z1 + z2) // 2, 'lantern[hanging=true]')
bathroom(2, 25, 4, 28, 19, (5, 27), 'east')          # President's bath
bathroom(80, 25, 82, 28, 19, (79, 27), 'west')       # Lincoln bath
bathroom(80, 10, 82, 13, 19, (79, 12), 'west')       # Queens' bath
bathroom(26, 2, 28, 5, 19, (26, 6), 'south') if False else bathroom(26, 2, 28, 4, 19, (27, 5), 'south')
for (x1, x2) in [(7, 9), (68, 70)]:
    bathroom(x1, 27, x2, 29, 27, (x1 + 1, 30), 'south') if False else bathroom(x1, 30, x2, 32, 27, (x1 + 1, 29), 'south')
# Lincoln Bedroom desk
r.box(68, 19, 36, 70, 19, 36, 'dark_oak_slab[type=top]'); r.chair(69, 19, 35, 'south', 'dark_oak_stairs')
r.set(68, 20, 36, 'lantern'); r.set(70, 20, 36, 'potted_fern')
# hidden ceiling lights: sea lanterns in slabs, under the carpets of the floor above
for (yc, xs, zs) in [(7, range(3, 82, 6), range(3, 41, 6)), (18, range(3, 82, 6), range(3, 41, 6)), (26, range(9, 78, 6), range(9, 35, 6))]:
    for x in xs:
        for z in zs:
            above = r.get(x, yc + 1, z) or ''
            below = r.get(x, yc - 1, z)
            if above.endswith('_carpet') or above.startswith('minecraft:') and above.endswith('_carpet'):
                r.set(x, yc, z, 'sea_lantern')
# wall lights in the second-floor Center Hall and the ground-floor Center Hall
for x in range(4, 82, 8):
    for (z, y) in [(17, 23), (22, 23), (18, 4), (20, 4)]:
        pass
