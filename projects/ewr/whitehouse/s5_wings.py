exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\whitehouse\lib.py").read())
# West Wing (x 4..29, z 46..92 incl. the Oval Office bulge), East Wing (x 147..170, z 48..84), colonnades
WALL = 'smooth_quartz'

def opening(x1, z1, x2, z2, y, h=3):
    b.box(min(x1, x2), y, min(z1, z2), max(x1, x2), y + h - 1, max(z1, z2), 'air')
def wx(x, z1, z2, y1, y2, blk=WALL):
    b.box(x, y1, min(z1, z2), x, y2, max(z1, z2), blk)
def wz(z, x1, x2, y1, y2, blk=WALL):
    b.box(min(x1, x2), y1, z, max(x1, x2), y2, z, blk)
def lights(x1, z1, x2, z2, y, step=4):
    for x in range(x1 + 1, x2, step):
        for z in range(z1 + 1, z2, step):
            b.set(x, y, z, 'lantern[hanging=true]')
def fireplace(x, z, y, facing):
    dx, dz = DIRS[facing]; px, pz = DIRS[right_of(facing)]
    for k in (-2, -1, 0, 1, 2):
        b.set(x + px * k, y, z + pz * k, 'white_concrete' if k else 'campfire[lit=true,signal_fire=false]')
        b.set(x + px * k, y + 1, z + pz * k, 'white_concrete' if k else 'air')
        b.set(x + px * k, y + 2, z + pz * k, 'white_concrete')
        if abs(k) <= 2:
            b.set(x + px * k + dx, y + 2, z + pz * k + dz, 'smooth_quartz_slab[type=bottom]')
def desk(x, z, y, facing, monitor=True):
    """desk at (x,z) with a computer; chair on the `facing` side looking back at the desk"""
    b.set(x, y, z, 'spruce_slab[type=top]')
    if monitor:
        b.set(x, y + 1, z, 'black_stained_glass_pane')
    dx, dz = DIRS[facing]
    b.chair(x + dx, y, z + dz, OPPOSITE[facing], 'spruce_stairs')
def office(x1, z1, x2, z2, y, title, sign, carpet='light_gray', desks=None):
    b.carpet(x1, z1, x2, z2, y, carpet)
    for (x, z, f) in (desks or []):
        desk(x, z, y, f)
    b.bookshelves(x1, y, z1, x1, y + 2, z1 + 2) if z2 - z1 > 3 else None
    b.plant(x2, y, z1, 'potted_fern'); b.plant(x2, y, z2, 'potted_azalea_bush')
    b.set((x1 + x2) // 2, y + 5, (z1 + z2) // 2, 'lantern[hanging=true]')
    if sign:
        b.sign(sign[0], y + 2, sign[1], ['', title[0], title[1] if len(title) > 1 else '', ''], sign[2])
def ext_windows_x(x, z1, z2, ys, step=4, skip=()):
    for z in range(z1, z2 + 1, step):
        if any(a <= z <= c for a, c in skip):
            continue
        for y in ys:
            b.set(x, y, z, 'glass_pane'); b.set(x, y, z + 1, 'glass_pane')
def ext_windows_z(z, x1, x2, ys, step=4, skip=()):
    for x in range(x1, x2 + 1, step):
        if any(a <= x <= c for a, c in skip):
            continue
        for y in ys:
            b.set(x, y, z, 'glass_pane'); b.set(x + 1, y, z, 'glass_pane')
def wing_shell(x1, z1, x2, z2):
    b.box(x1, -1, z1, x2, 16, z2, WALL)
    b.box(x1 + 1, 0, z1 + 1, x2 - 1, 8, z2 - 1, 'air')
    b.box(x1 + 1, 10, z1 + 1, x2 - 1, 15, z2 - 1, 'air')
    b.box(x1 + 1, -1, z1 + 1, x2 - 1, -1, z2 - 1, 'polished_diorite')
    b.box(x1 + 1, 9, z1 + 1, x2 - 1, 9, z2 - 1, 'smooth_quartz')
    for x in range(x1, x2 + 1):
        b.set(x, 9, z1 - 1, 'smooth_quartz_slab[type=top]'); b.set(x, 9, z2 + 1, 'smooth_quartz_slab[type=top]')
        b.set(x, 16, z1 - 1, 'smooth_quartz_stairs[facing=south,half=top]'); b.set(x, 16, z2 + 1, 'smooth_quartz_stairs[facing=north,half=top]')
    for z in range(z1, z2 + 1):
        b.set(x1 - 1, 9, z, 'smooth_quartz_slab[type=top]'); b.set(x2 + 1, 9, z, 'smooth_quartz_slab[type=top]')
        b.set(x1 - 1, 16, z, 'smooth_quartz_stairs[facing=east,half=top]'); b.set(x2 + 1, 16, z, 'smooth_quartz_stairs[facing=west,half=top]')
    n = 0
    for (xa, za, xb, zb) in [(x1, z1, x2, z1), (x1, z2, x2, z2), (x1, z1, x1, z2), (x2, z1, x2, z2)]:
        for x in range(xa, xb + 1):
            for z in range(za, zb + 1):
                b.set(x, 17, z, 'smooth_quartz' if n % 5 == 0 else 'diorite_wall'); b.set(x, 18, z, 'smooth_quartz_slab'); n += 1
    b.box(x1 + 1, 16, z1 + 1, x2 - 1, 16, z2 - 1, 'light_gray_concrete')

# ============================================================= WEST WING
wing_shell(4, 46, 29, 84)
wing_shell(4, 77, 12, 92)
b.box(5, 0, 77, 11, 8, 91, 'air'); b.box(5, 10, 77, 11, 15, 91, 'air')
b.box(5, 0, 84, 11, 8, 84, 'air'); b.box(5, 10, 84, 11, 15, 84, 'air')
b.box(5, 16, 77, 11, 16, 91, 'light_gray_concrete')
for x in range(5, 12):
    b.set(x, 17, 84, 'air'); b.set(x, 18, 84, 'air')
for x in range(5, 12):
    b.set(x, 17, 77, 'air'); b.set(x, 18, 77, 'air'); b.set(x, 16, 77, 'light_gray_concrete')
for z in range(77, 84):
    b.set(4, 17, z, 'diorite_wall'); b.set(12, 17, z, 'air') if False else None
# exterior windows
ext_windows_z(46, 6, 27, (2, 3, 4, 5, 6), skip=((23, 27),)); ext_windows_z(46, 6, 27, (11, 12, 13, 14))
ext_windows_x(4, 48, 90, (2, 3, 4, 5, 6), skip=((60, 65),)); ext_windows_x(4, 48, 90, (11, 12, 13, 14))
ext_windows_x(29, 48, 75, (2, 3, 4, 5, 6), skip=((60, 65),)); ext_windows_x(29, 48, 75, (11, 12, 13, 14))
ext_windows_z(92, 6, 10, (2, 3, 4, 5, 6)); ext_windows_z(92, 6, 10, (11, 12, 13, 14))
# north entrance (West Wing lobby) with a small portico
opening(24, 46, 26, 46, 0, 4)
for x in (23, 27):
    b.box(x, 0, 44, x, 4, 44, 'quartz_pillar') if False else b.box(x, 0, 45, x, 4, 45, 'quartz_pillar')
b.box(22, 5, 45, 28, 5, 45, 'smooth_quartz_slab')
# ---------- OVAL OFFICE: centre (21, 84), x 13..29, z 76..92
OX_, OZ_, AX, AZ = 21, 84, 7.6, 7.6
for x in range(13, 30):
    for z in range(76, 93):
        e = ((x - OX_) / (AX + .5)) ** 2 + ((z - OZ_) / (AZ + .5)) ** 2
        ei = ((x - OX_) / (AX - .5)) ** 2 + ((z - OZ_) / (AZ - .5)) ** 2
        if z > 84:
            for y in range(-1, 19):
                b.set(x, y, z, 'air')
            b.set(x, -1, z, 'grass_block')
        if e <= 1 and ei > 1:
            for y in range(-1, 10):
                b.set(x, y, z, WALL)
            b.set(x, 10, z, 'smooth_quartz_slab'); b.set(x, 9, z, 'smooth_quartz')
            if z > 84:
                b.set(x, 11, z, 'diorite_wall'); b.set(x, 12, z, 'smooth_quartz_slab')
            if z >= 86 and (x + z) % 3 != 0:      # tall curved south windows
                for y in range(1, 7):
                    b.set(x, y, z, 'glass_pane')
        elif ei <= 1:
            b.set(x, -1, z, 'oak_planks')
            for y in range(0, 9):
                b.set(x, y, z, 'air')
            b.set(x, 9, z, 'smooth_quartz')
            if z > 84:
                b.set(x, 10, z, 'smooth_quartz_slab')
            d = math.hypot(x - OX_, z - OZ_)
            if 5.5 < d < 6.3:
                b.set(x, 9, z, 'sea_lantern')
for z in range(76, 85):                  # fill corners between oval and rectangle
    for x in range(13, 30):
        e = ((x - OX_) / (AX + .5)) ** 2 + ((z - OZ_) / (AZ + .5)) ** 2
        if e > 1:
            for y in range(-1, 9):
                b.set(x, y, z, WALL)
# carpet: cream with the Presidential Seal (blue disc, gold ring, white stars, eagle)
for x in range(14, 29):
    for z in range(77, 92):
        ei = ((x - OX_) / (AX - .5)) ** 2 + ((z - OZ_) / (AZ - .5)) ** 2
        if ei <= 1:
            d = math.hypot(x - OX_, z - OZ_ + 1)
            c = 'white'
            if ei > 0.8:
                c = 'yellow'
            if d <= 4.6:
                c = 'yellow' if d > 3.9 else 'blue'
                if 2.6 < d <= 3.4 and (x + z) % 2 == 0:
                    c = 'white'
            b.set(x, 0, z, f'{c}_carpet')
SX, SZ = OX_, OZ_ - 1           # eagle in the seal centre
for (dx, dz, c) in [(0, 0, 'brown'), (0, -1, 'white'), (-1, 0, 'brown'), (1, 0, 'brown'), (-2, -1, 'brown'), (2, -1, 'brown'),
                    (0, 1, 'red'), (-1, 1, 'yellow'), (1, 1, 'white')]:
    b.set(SX + dx, 0, SZ + dz, f'{c}_carpet')
# Resolute Desk before the south windows, flags behind
for x in range(19, 24):
    b.set(x, 0, 88, 'dark_oak_planks' if x in (19, 23) else 'dark_oak_trapdoor[facing=south,half=bottom,open=true]')
    b.set(x, 1, 88, 'dark_oak_slab[type=bottom]') if False else None
b.box(19, 1, 88, 23, 1, 88, 'dark_oak_slab[type=bottom]') if False else None
b.box(19, 0, 88, 23, 0, 88, 'dark_oak_planks'); b.box(20, 0, 88, 22, 0, 88, 'dark_oak_trapdoor[facing=north,half=top,open=true]') if False else None
b.box(20, 1, 88, 22, 1, 88, 'green_carpet'); b.set(19, 1, 88, 'potted_white_tulip'); b.set(23, 1, 88, 'lantern')
b.set(21, 0, 89, 'dark_oak_stairs[facing=south]')          # the President's chair (sitter looks north)
b.set(21, 0, 89, 'spruce_stairs[facing=south,half=bottom]')
for (x, pat) in [(18, FLAG_NBT), (24, '{patterns:[{pattern:"minecraft:circle",color:"white"},{pattern:"minecraft:border",color:"yellow"}]}')]:
    b.set(x, 0, 90, 'white_banner[rotation=8]' if pat == FLAG_NBT else 'blue_banner[rotation=8]', nbt=pat)
# sofas facing each other, coffee table, armchairs by the fireplace
b.sofa(17, 0, 82, 'east', 4, 'birch_stairs', 'birch_trapdoor')
b.sofa(25, 0, 85, 'west', 4, 'birch_stairs', 'birch_trapdoor')
b.box(20, 0, 83, 22, 0, 84, 'dark_oak_slab[type=top]'); b.set(21, 1, 83, 'potted_red_tulip')
fireplace(21, 77, 0, 'south')
b.box(20, 3, 77, 22, 8, 77, 'white_concrete')
b.chair(18, 0, 79, 'east', 'birch_stairs'); b.chair(24, 0, 79, 'west', 'birch_stairs')
b.painting(21, 4, 78, 'south', 'minecraft:wanderer')
for (x, z) in [(15, 80), (27, 80)]:          # busts on pedestals
    b.set(x, 0, z, 'quartz_pillar'); b.set(x, 1, z, 'skeleton_skull[rotation=%d]' % (4 if x < 21 else 12))
for (x, z) in [(15, 88), (27, 88)]:
    b.plant(x, 0, z, 'potted_fern')
b.set(16, 0, 86, 'dark_oak_fence'); b.set(16, 1, 86, 'dark_oak_fence'); b.set(16, 2, 86, 'clock') if False else None
b.box(16, 0, 86, 16, 2, 86, 'dark_oak_planks'); b.set(16, 3, 86, 'dark_oak_slab')   # grandfather clock
opening(12, 83, 14, 85, 0, 3)               # door to the Outer Oval
opening(28, 83, 30, 85, 0, 3)               # door to the Rose Garden colonnade walk
b.sign(14, 3, 82, ['', 'THE OVAL', 'OFFICE', ''], 'west') if False else b.sign(12, 3, 82, ['', 'THE OVAL', 'OFFICE', ''], 'west')
b.sign(30, 3, 82, ['', 'THE OVAL', 'OFFICE', ''], 'east')
for x in (30, 31, 32):
    for z in (83, 84, 85):
        b.set(x, -1, z, 'smooth_sandstone'); b.set(x, 0, z, 'air'); b.set(x, 1, z, 'air'); b.set(x, 2, z, 'air')
# ---------- ground floor rooms
wz(60, 5, 28, 0, 8); wz(65, 5, 28, 0, 8); wx(8, 47, 59, 0, 8); wx(21, 47, 59, 0, 8)
wx(8, 66, 91, 0, 8); wx(16, 66, 75, 0, 8); wz(76, 9, 28, 0, 8)
opening(5, 60, 7, 60, 0, 3); opening(19, 60, 20, 60, 0, 3); opening(24, 60, 25, 60, 0, 3)
opening(5, 65, 7, 65, 0, 3); opening(11, 65, 12, 65, 0, 3); opening(22, 65, 23, 65, 0, 3); opening(8, 79, 8, 81, 0, 3)
opening(4, 62, 4, 64, 0, 3); opening(29, 62, 29, 64, 0, 3)   # West Exec Ave door, colonnade door
b.carpet(5, 61, 28, 64, 0, 'red', border='yellow'); b.carpet(5, 66, 7, 91, 0, 'blue')
lights(5, 62, 28, 65, 8, 5); lights(5, 66, 7, 91, 8, 6)
b.sign(5, 3, 67, ['', 'West Wing', 'Corridor', ''], 'east')
# Press Briefing Room x 9..20, z 47..59
b.box(9, 0, 47, 20, 6, 47, 'blue_concrete')
for (dx, dy, c) in [(0, 0, 'gold_block'), (1, 0, 'gold_block'), (-1, 1, 'gold_block'), (2, 1, 'gold_block'), (-1, 2, 'gold_block'),
                    (2, 2, 'gold_block'), (0, 3, 'gold_block'), (1, 3, 'gold_block'), (0, 1, 'light_blue_concrete'), (1, 1, 'light_blue_concrete'),
                    (0, 2, 'white_concrete'), (1, 2, 'white_concrete')]:
    b.set(14 + dx, 2 + dy, 47, c)
b.sign(14, 1, 48, ['THE WHITE HOUSE', 'WASHINGTON', '', ''], 'south'); b.sign(15, 1, 48, ['THE WHITE HOUSE', 'WASHINGTON', '', ''], 'south')
b.box(13, -1, 48, 16, -1, 50, 'dark_oak_planks')
b.set(14, 0, 50, 'lectern[facing=north]'); b.set(15, 0, 50, 'lectern[facing=north]')
b.set(12, 0, 48, 'white_banner[rotation=0]', nbt=FLAG_NBT); b.set(17, 0, 48, 'white_banner[rotation=0]', nbt=FLAG_NBT)
for z in range(52, 58):
    for x in range(9, 21):
        if x in (14, 15):
            continue
        b.chair(x, 0, z, 'north', 'dark_prismarine_stairs')
for x in (10, 13, 16, 19):               # cameras at the back
    b.set(x, 0, 59, 'iron_bars'); b.set(x, 1, 59, 'black_concrete'); b.set(x, 2, 59, 'observer[facing=south]')
b.carpet(9, 51, 20, 59, 0, 'blue') if False else None
lights(8, 47, 21, 59, 8, 4)
b.sign(21, 2, 61, ['', 'James S. Brady', 'Press Briefing', 'Room'], 'south')
# Lobby x 22..28
b.carpet(22, 47, 28, 59, 0, 'red', border='yellow')
b.box(22, 0, 55, 25, 0, 55, 'dark_oak_planks'); b.box(22, 1, 55, 25, 1, 55, 'dark_oak_slab')
b.chair(23, 0, 56, 'north', 'spruce_stairs')
b.sofa(28, 0, 49, 'west', 3, 'oak_stairs') if False else b.sofa(27, 0, 50, 'west', 3)
b.painting(23, 4, 48, 'south', 'minecraft:kebab') if False else None
b.plant(22, 0, 47, 'potted_fern'); b.plant(28, 0, 59, 'potted_fern')
b.sign(27, 2, 61, ['', 'West Wing', 'Lobby', ''], 'south')
lights(21, 47, 29, 59, 8, 4)
# Roosevelt Room x 9..15, z 66..75
b.carpet(9, 66, 15, 75, 0, 'brown', border='orange')
b.long_table(11, 68, 13, 73, 0, 'dark_oak_slab')
for z in range(68, 74):
    b.chair(10, 0, z, 'east', 'dark_oak_stairs'); b.chair(14, 0, z, 'west', 'dark_oak_stairs')
b.chair(12, 0, 67, 'south', 'dark_oak_stairs'); b.chair(12, 0, 74, 'north', 'dark_oak_stairs')
b.painting(12, 4, 75, 'north', 'minecraft:wanderer')
b.set(9, 0, 75, 'white_banner[rotation=8]', nbt=FLAG_NBT); b.set(15, 0, 75, 'blue_banner[rotation=8]')
lights(8, 65, 16, 76, 8, 3)
b.sign(13, 2, 64, ['', 'Roosevelt', 'Room', ''], 'north')
# Cabinet Room x 17..28: oval table, ~20 chairs, windows on the Rose Garden
b.carpet(17, 66, 28, 75, 0, 'light_gray', border='yellow')
TCX, TCZ, TAX, TAZ = 22.5, 70.5, 4.2, 1.8
for x in range(17, 29):
    for z in range(66, 76):
        e = ((x - TCX) / TAX) ** 2 + ((z - TCZ) / TAZ) ** 2
        if e <= 1:
            b.set(x, 0, z, 'dark_oak_slab[type=top]')
n = 0
for x in range(17, 29):
    for z in range(66, 76):
        e = ((x - TCX) / TAX) ** 2 + ((z - TCZ) / TAZ) ** 2
        if 1 < e <= 1.9 and b.get(x, 0, z) and 'slab' not in b.get(x, 0, z):
            dx, dz = TCX - x, TCZ - z
            f = ('east' if dx > 0 else 'west') if abs(dx) / TAX > abs(dz) / TAZ else ('south' if dz > 0 else 'north')
            b.chair(x, 0, z, f, 'dark_oak_stairs'); n += 1
print('cabinet chairs', n)
fireplace(22, 66, 0, 'south') if False else None
b.painting(22, 4, 66, 'south', 'minecraft:graham') if False else None
b.set(17, 0, 75, 'white_banner[rotation=8]', nbt=FLAG_NBT)
lights(16, 65, 29, 76, 8, 3)
b.sign(24, 2, 64, ['', 'Cabinet', 'Room', ''], 'north')
# Outer Oval (secretaries) x 9..12, z 77..91
b.carpet(9, 77, 12, 91, 0, 'light_blue')
desk(10, 80, 0, 'west') if False else desk(11, 79, 0, 'south'); desk(11, 89, 0, 'north')
b.sign(9, 2, 82, ['', 'Outer Oval', 'Office', ''], 'east') if False else None
lights(8, 76, 13, 92, 8, 4)
# up-stair (ground -> second floor) along the corridor, climbing east x 10..18 at z 61..62
for i in range(9):
    for z in (61, 62):
        b.set(10 + i, i, z, 'quartz_stairs[facing=east]')
        for y in range(0, i):
            b.set(10 + i, y, z, 'quartz_bricks')
b.box(12, 9, 61, 18, 9, 62, 'air')
for x in range(10, 19):
    b.set(x, 10, 63, 'diorite_wall')
b.set(9, 10, 61, 'diorite_wall'); b.set(9, 10, 62, 'diorite_wall')
# basement stair (stair hall x 5..7, z 47..59) to the Situation Room
for i in range(5):
    for x in range(5, 8):
        b.set(x, -2 - i, 58 - i, 'quartz_stairs[facing=south]')
        for y in range(-1 - i, 1):
            b.set(x, y, 58 - i, 'air') if y > -2 - i else None
b.box(5, -6, 54, 7, -1, 58, 'air')
for i in range(5):
    for x in range(5, 8):
        b.set(x, -2 - i, 58 - i, 'quartz_stairs[facing=south]')
        b.box(x, -8, 58 - i, x, -3 - i, 58 - i, 'stone_bricks')
for z in range(54, 59):
    b.set(8, 0, z, WALL)
b.box(5, 0, 53, 7, 0, 53, 'diorite_wall')
# Situation Room (basement) x 4..21, z 46..59, floor y -7, interior y -6..-2
b.box(4, -8, 46, 21, -1, 59, 'deepslate_tiles')
b.box(5, -7, 47, 20, -7, 58, 'gray_carpet') if False else b.box(5, -7, 47, 20, -7, 58, 'polished_deepslate')
b.box(5, -6, 47, 7, -2, 53, 'air'); b.box(5, -6, 54, 7, -2, 58, 'air')
for i in range(5):
    for x in range(5, 8):
        b.set(x, -2 - i, 58 - i, 'quartz_stairs[facing=south]')
b.box(9, -6, 47, 20, -2, 58, 'air'); opening(8, 49, 8, 51, -6, 3)
b.box(5, -1, 54, 7, -1, 58, 'air')
b.box(5, -1, 47, 20, -1, 53, 'polished_diorite'); b.box(8, -1, 54, 20, -1, 59, 'polished_diorite'); b.box(5, -1, 59, 7, -1, 59, 'polished_diorite')
for x in range(10, 20, 3):
    b.set(x, -1, 50, 'sea_lantern'); b.set(x, -1, 56, 'sea_lantern')
b.long_table(12, 50, 17, 55, -6, 'polished_blackstone_slab')
for z in range(50, 56):
    b.chair(11, -6, z, 'east', 'blackstone_stairs'); b.chair(18, -6, z, 'west', 'blackstone_stairs')
b.chair(14, -6, 49, 'south', 'blackstone_stairs'); b.chair(15, -6, 56, 'north', 'blackstone_stairs')
b.box(10, -5, 47, 19, -3, 47, 'black_stained_glass'); b.box(12, -4, 47, 17, -4, 47, 'light_blue_stained_glass')
b.box(20, -5, 49, 20, -3, 56, 'black_stained_glass'); b.box(20, -4, 51, 20, -4, 54, 'cyan_stained_glass')
b.box(10, -5, 58, 19, -3, 58, 'tinted_glass')
for (x, txt) in [(11, 'WASHINGTON'), (14, 'ZULU'), (17, 'LOCAL')]:
    b.sign(x, -2, 48, ['', txt, '12:00', ''], 'south')
b.sign(9, -4, 52, ['', 'SITUATION', 'ROOM', 'Restricted'], 'east') if False else b.sign(7, -4, 50, ['', 'SITUATION', 'ROOM', ''], 'east') if False else None
for (x, z) in [(12, 52), (17, 52), (12, 54), (17, 54)]:
    b.set(x, -2, z, 'lantern[hanging=true]')
for x in range(10, 20, 3):
    b.set(x, -1, 50, 'sea_lantern'); b.set(x, -1, 56, 'sea_lantern')
b.sign(5, 2, 59, ['', 'Situation Room', 'downstairs', ''], 'east')
# ---------- second floor: staff offices
wz(60, 5, 28, 10, 15); wz(65, 5, 28, 10, 15); wx(13, 47, 59, 10, 15); wx(21, 47, 59, 10, 15)
wx(13, 66, 76, 10, 15); wx(21, 66, 76, 10, 15); wz(77, 5, 28, 10, 15) if False else wz(77, 13, 28, 10, 15)
for x in range(13, 29):
    for z in range(77, 85):
        b.box(x, 10, z, x, 16, z, WALL) if ((x - OX_) / (AX + .5)) ** 2 + ((z - OZ_) / (AZ + .5)) ** 2 > 1 or True else None
b.box(13, 10, 77, 28, 15, 84, WALL)
b.box(14, 16, 77, 28, 16, 84, 'light_gray_concrete')
b.carpet(5, 61, 28, 64, 10, 'blue', border='light_blue')
for x in range(12, 19):
    for z in (61, 62):
        b.set(x, 10, z, 'air')
opening(9, 60, 10, 60, 10, 3); opening(16, 60, 17, 60, 10, 3); opening(24, 60, 25, 60, 10, 3)
opening(9, 65, 10, 65, 10, 3); opening(16, 65, 17, 65, 10, 3); opening(24, 65, 25, 65, 10, 3)
office(5, 47, 12, 59, 10, ('Chief of', 'Staff'), (11, 66 - 5, 'south') if False else (11, 61, 'south'), 'gray',
       [(8, 50, 'south'), (6, 56, 'east'), (11, 56, 'west')])
office(14, 47, 20, 59, 10, ('Vice', 'President'), (18, 61, 'south'), 'blue', [(17, 50, 'south'), (15, 56, 'east')])
office(22, 47, 28, 59, 10, ('National Security', 'Advisor'), (26, 61, 'south'), 'gray', [(25, 50, 'south'), (27, 56, 'west')])
office(5, 66, 12, 91, 10, ('Press', 'Office'), (11, 64, 'north'), 'light_gray',
       [(7, 69, 'east'), (10, 69, 'west'), (7, 74, 'east'), (10, 74, 'west'), (7, 80, 'east'), (10, 80, 'west'), (7, 86, 'east'), (10, 86, 'west')])
office(14, 66, 20, 76, 10, ('Communications', ''), (18, 64, 'north'), 'gray', [(16, 69, 'south'), (18, 73, 'north')])
office(22, 66, 28, 76, 10, ('White House', 'Counsel'), (26, 64, 'north'), 'brown', [(24, 69, 'south'), (26, 73, 'north')])
lights(4, 60, 29, 65, 15, 5)

# ============================================================= WEST COLONNADE x 30..47, z 61..66
def colonnade(x1, x2):
    b.box(x1, -1, 61, x2, -1, 66, 'polished_diorite')
    b.box(x1, 0, 62, x2, 6, 66, 'air')
    wz(61, x1, x2, -1, 7)
    for x in range(x1 + 1, x2, 3):
        b.box(x, 1, 61, x, 4, 61, 'glass_pane')
        b.set(x, 5, 61, 'chiseled_quartz_block')
    for x in range(x1, x2 + 1):
        if (x - x1) % 3 == 0:
            b.box(x, 0, 66, x, 5, 66, 'quartz_pillar')
        else:
            b.set(x, 5, 66, 'smooth_quartz_stairs[facing=north,half=top]')
        b.set(x, 6, 66, 'smooth_quartz')
    b.box(x1, 7, 61, x2, 7, 66, 'smooth_quartz')
    b.box(x1, 6, 62, x2, 6, 65, 'smooth_quartz')
    for x in range(x1, x2 + 1):
        b.set(x, 8, 66, 'smooth_quartz' if x % 4 == 0 else 'diorite_wall'); b.set(x, 9, 66, 'smooth_quartz_slab')
    b.carpet(x1, 63, x2, 64, 0, 'red')
    for x in range(x1 + 2, x2, 4):
        b.set(x, 5, 63, 'lantern[hanging=true]')
    for x in range(x1, x2 + 1):
        b.set(x, 0, 67, 'air'); b.set(x, 1, 67, 'air'); b.set(x, -1, 67, 'smooth_sandstone')
colonnade(30, 47)
colonnade(133, 146)

# ============================================================= EAST WING x 147..170, z 48..84
wing_shell(147, 48, 170, 84)
ext_windows_z(48, 149, 168, (2, 3, 4, 5, 6)); ext_windows_z(48, 149, 168, (11, 12, 13, 14))
ext_windows_z(84, 149, 168, (11, 12, 13, 14)); ext_windows_z(84, 161, 168, (2, 3, 4, 5, 6))
ext_windows_x(170, 50, 82, (11, 12, 13, 14)); ext_windows_x(170, 66, 82, (2, 3, 4, 5, 6))
ext_windows_x(147, 50, 58, (2, 3, 4, 5, 6)); ext_windows_x(147, 50, 82, (11, 12, 13, 14), skip=((60, 66),))
# visitors' entrance (east) with canopy
opening(170, 56, 170, 60, 0, 4)
b.box(171, 5, 55, 173, 5, 61, 'smooth_quartz_slab')
for z in (55, 61):
    b.box(173, 0, z, 173, 4, z, 'quartz_pillar')
b.sign(171, 3, 54, ['', 'East Wing', "Visitors'", 'Entrance'], 'east') if False else b.sign(171, 6, 58, ['', 'EAST WING', "VISITORS'", 'ENTRANCE'], 'east')
# rooms
wz(65, 148, 169, 0, 8); wz(60, 148, 159, 0, 8); wx(159, 49, 59, 0, 8); wx(159, 66, 83, 0, 8)
opening(147, 62, 147, 64, 0, 3)
opening(160, 61, 160, 64, 0, 3) if False else None
opening(152, 65, 153, 65, 0, 3); opening(159, 52, 159, 53, 0, 3); opening(163, 65, 164, 65, 0, 3)
b.carpet(148, 61, 159, 64, 0, 'red', border='yellow')
lights(147, 60, 160, 65, 8, 4)
# visitors lobby + security screening x 160..169, z 49..64
b.carpet(160, 49, 169, 64, 0, 'light_gray')
for z in (55, 59):
    b.box(164, 0, z, 164, 2, z, 'iron_block'); b.box(164, 0, z + 2, 164, 2, z + 2, 'iron_block'); b.box(164, 3, z, 164, 3, z + 2, 'iron_block')
    b.set(164, 0, z + 1, 'heavy_weighted_pressure_plate')
b.box(166, 0, 52, 166, 0, 54, 'smooth_stone_slab[type=top]'); b.box(167, 0, 52, 167, 0, 54, 'smooth_stone_slab[type=top]')
b.box(165, 0, 50, 168, 0, 50, 'black_concrete') if False else None
b.set(166, 1, 53, 'iron_trapdoor[half=top,facing=north,open=true]') if False else None
b.box(165, 0, 51, 168, 1, 51, 'gray_concrete'); b.set(166, 2, 51, 'black_stained_glass_pane'); b.chair(166, 0, 50, 'south', 'spruce_stairs')
for z in range(50, 64, 2):                  # queue rope posts
    b.set(168, 0, z, 'polished_blackstone_wall')
b.sign(168, 2, 64, ['', 'SECURITY', 'SCREENING', ''], 'north') if False else b.sign(169, 3, 58, ['', 'SECURITY', 'SCREENING', 'Have ID ready'], 'west')
b.sign(160, 2, 62, ['', 'Booksellers &', 'Visitor Office', ''], 'east') if False else None
lights(159, 48, 170, 65, 8, 4)
# First Lady's office x 148..158, z 49..59
office(148, 49, 158, 59, 0, ("First Lady's", 'Office'), (160, 51, 'east'), 'pink', [(153, 52, 'south'), (150, 56, 'east')])
# Family Theater x 148..158, z 66..83
b.box(148, -1, 66, 158, -1, 83, 'red_concrete') if False else b.box(148, -1, 66, 158, -1, 83, 'polished_blackstone')
b.box(149, 1, 83, 157, 6, 83, 'white_concrete'); b.box(148, 0, 83, 148, 7, 83, 'red_wool'); b.box(158, 0, 83, 158, 7, 83, 'red_wool')
b.box(149, 0, 82, 157, 0, 82, 'black_carpet')
for z in range(69, 80, 2):
    for x in range(149, 158):
        if x == 153:
            continue
        b.chair(x, 0, z, 'south', 'red_nether_brick_stairs')
b.set(153, 3, 67, 'observer[facing=south]') if False else b.set(153, 6, 66, 'lantern[hanging=true]')
b.carpet(153, 66, 153, 81, 0, 'red')
for z in (70, 76):
    b.set(148, 4, z, 'redstone_lamp[lit=true]') if False else b.set(149, 7, z, 'lantern[hanging=true]')
b.sign(151, 2, 64, ['', 'Family', 'Theater', ''], 'north')
# Visitors office / East Garden Room x 160..169, z 66..83
office(160, 66, 169, 83, 0, ('Visitors', 'Office'), (164, 64, 'north') if False else None, 'light_gray',
       [(162, 70, 'east'), (167, 70, 'west'), (162, 77, 'east'), (167, 77, 'west')])
b.sign(165, 2, 64, ['', 'Visitors', 'Office', ''], 'north')
# east-wing up-stair along the corridor (climbing east x 149..157 at z 61..62)
for i in range(9):
    for z in (61, 62):
        b.set(149 + i, i, z, 'quartz_stairs[facing=east]')
        for y in range(0, i):
            b.set(149 + i, y, z, 'quartz_bricks')
b.box(151, 9, 61, 157, 9, 62, 'air')
for x in range(149, 158):
    b.set(x, 10, 63, 'diorite_wall')
# second floor offices
wz(60, 148, 169, 10, 15); wz(65, 148, 169, 10, 15); wx(158, 49, 59, 10, 15); wx(158, 66, 83, 10, 15)
b.carpet(148, 61, 169, 64, 10, 'blue', border='light_blue')
for x in range(151, 158):
    for z in (61, 62):
        b.set(x, 10, z, 'air')
opening(153, 60, 154, 60, 10, 3); opening(163, 60, 164, 60, 10, 3); opening(153, 65, 154, 65, 10, 3); opening(163, 65, 164, 65, 10, 3)
office(148, 49, 157, 59, 10, ('Social', 'Secretary'), (155, 61, 'south'), 'gray', [(151, 52, 'south'), (154, 56, 'north')])
office(159, 49, 169, 59, 10, ('Military', 'Office'), (165, 61, 'south'), 'green', [(162, 52, 'south'), (166, 56, 'north')])
office(148, 66, 157, 83, 10, ('Staff', 'Offices'), (155, 64, 'north'), 'light_gray', [(150, 70, 'east'), (155, 70, 'west'), (150, 78, 'east'), (155, 78, 'west')])
office(159, 66, 169, 83, 10, ('Calendar &', 'Scheduling'), (166, 64, 'north'), 'gray', [(161, 70, 'east'), (167, 70, 'west'), (161, 78, 'east'), (167, 78, 'west')])
lights(147, 60, 170, 65, 15, 5)
