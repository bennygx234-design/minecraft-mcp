exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\whitehouse\lib.py").read())
W, D = 180, 156
# ---------------- trees first (everything else overrides)
TREES = [(10, 22), (22, 30), (34, 20), (46, 32), (14, 38), (56, 22), (124, 22), (136, 32), (148, 20), (160, 30),
         (170, 38), (166, 18), (40, 38), (140, 38),
         (8, 100), (20, 112), (12, 128), (26, 140), (40, 146), (8, 146), (36, 104),
         (172, 100), (160, 112), (168, 128), (154, 140), (140, 146), (172, 146), (146, 104),
         (40, 125), (140, 125), (88, 148), (66, 110), (114, 110)]
for (x, z) in TREES:
    tree(x, z, kind=rng.choice(['oak', 'oak', 'dark_oak', 'birch']))
for (x, z) in [(52, 97), (128, 97)]:
    tree(x, z, h=4, r=2)

# ---------------- Pennsylvania Avenue (z 0..6) + pedestrian plaza (z 7..12)
for x in range(W):
    for z in range(0, 13):
        for yy in range(8, 20):
            b.set(x, yy, z, 'air')
    for z in range(0, 7):
        b.set(x, 7, z, 'gray_concrete')
    if x % 6 < 3:
        b.set(x, 7, 3, 'white_concrete')
    for z in range(7, 13):
        b.set(x, 7, z, 'polished_andesite' if (x // 4 + z) % 2 else 'smooth_stone')
    b.set(x, 7, 7, 'smooth_stone_slab[type=double]')
for x in range(8, 176, 16):          # plaza planters + trees, benches, lamps
    if abs(x - 68) < 6 or abs(x - 112) < 6 or abs(x - 60) < 4:
        continue
    b.box(x - 1, 8, 9, x + 1, 8, 11, 'smooth_quartz'); b.set(x, 8, 10, 'grass_block')
    tree(x, 10, y=9, h=4, r=2)
    b.set(x + 4, 8, 11, 'spruce_stairs[facing=north]'); b.set(x + 5, 8, 11, 'spruce_stairs[facing=north]')
    lamp_post(x + 8, 8, y=8)

# ---------------- North Lawn: U-shaped drive from NW/NE gates to the North Portico
cx, cz, ax, az = 90, 13, 22, 21
for x in range(60, 121):
    for z in range(13, 38):
        e = math.hypot((x - cx) / ax, (z - cz) / az)
        if abs(e - 1) * 21.5 <= 2.0:
            b.set(x, 7, z, 'polished_andesite')
            for yy in range(8, 16):
                b.set(x, yy, z, 'air')
        elif abs(e - 1) * 21.5 <= 2.6:
            b.set(x, 7, z, 'smooth_stone')
b.box(78, 7, 33, 102, 7, 36, 'polished_andesite')
for k in range(0, 181, 18):           # drive lamps
    t = math.radians(k)
    lx, lz = round(cx + (ax + 4) * math.cos(t)), round(cz + (az + 4) * math.sin(t))
    if 15 < lz < 36:
        lamp_post(lx, lz)
    lx, lz = round(cx + (ax - 4) * math.cos(t)), round(cz + (az - 4) * math.sin(t))
    if 15 < lz < 31:
        lamp_post(lx, lz)
# North fountain (round basin with a jet)
disc(90, 22, 5, 7, 'smooth_stone')
disc(90, 22, 5.2, 8, 'smooth_quartz', 3.9); disc(90, 22, 5.2, 9, 'smooth_quartz', 3.9)
disc(90, 22, 5.2, 10, 'smooth_quartz_slab', 3.9)
disc(90, 22, 3.9, 8, 'water'); disc(90, 22, 3.9, 9, 'air')
b.box(90, 8, 22, 90, 10, 22, 'quartz_pillar'); b.set(90, 11, 22, 'water')
for (x, z) in [(84, 16), (96, 16), (82, 28), (98, 28)]:
    b.set(x, 8, z, 'rose_bush'); b.set(x, 9, z, 'rose_bush[half=upper]')
flagpole(76, 26, h=11); flagpole(104, 26, h=11, facing='west')

# ---------------- terrace edge (z 44 retaining wall + balustrade), stairs, areaway along the residence
for x in list(range(3, 48)) + list(range(133, 177)):
    for y in range(0, 8):
        b.set(x, y, 44, 'quartz_bricks')
    if x in (37, 38, 39, 140, 141, 142):
        continue
    b.set(x, 8, 44, 'diorite_wall' if x % 5 else 'smooth_quartz'); b.set(x, 9, 44, 'smooth_quartz_slab')
for sx in (37, 140):
    for i in range(8):
        for x in range(sx, sx + 3):
            b.set(x, 7 - i, 45 + i, 'quartz_stairs[facing=north]')
            for y in range(0, 7 - i):
                b.set(x, y, 45 + i, 'quartz_bricks')
        for x in (sx - 1, sx + 3):
            for y in range(0, 9 - i):
                b.set(x, y, 45 + i, 'smooth_quartz')
            b.set(x, 9 - i, 45 + i, 'smooth_quartz_slab')
    for x in range(sx, sx + 3):          # top landing in the wall line
        b.set(x, 7, 44, 'smooth_quartz')
# areaway (dry moat) x 48..132, z 42..44 down to the ground floor
for x in range(48, 133):
    for z in range(42, 45):
        b.set(x, -1, z, 'smooth_stone')
        for y in range(0, 8):
            b.set(x, y, z, 'air')
    for y in range(0, 8):
        b.set(x, y, 41, 'quartz_bricks')
    b.set(x, 8, 41, 'diorite_wall' if x % 5 else 'smooth_quartz'); b.set(x, 9, 41, 'smooth_quartz_slab')
for x in (47, 133):
    for z in range(41, 45):
        for y in range(0, 8):
            b.set(x, y, z, 'quartz_bricks')
        b.set(x, 8, z, 'smooth_quartz'); b.set(x, 9, z, 'smooth_quartz_slab')

# ---------------- South Lawn: ellipse drive, big fountain, Marine One helipad
ex, ez, erx, erz = 90, 122, 46, 20
for x in range(40, 141):
    for z in range(98, 146):
        e = math.hypot((x - ex) / erx, (z - ez) / erz)
        if abs(e - 1) * 30 <= 1.6:
            b.set(x, -1, z, 'polished_andesite')
            for yy in range(0, 10):
                b.set(x, yy, z, 'air')
for sx in (58, 119):                       # spurs to the south gates
    for z in range(136, 153):
        for x in range(sx, sx + 4):
            b.set(x, -1, z, 'polished_andesite')
            for yy in range(0, 10):
                b.set(x, yy, z, 'air')
b.box(80, -1, 98, 100, -1, 102, 'polished_andesite')   # apron at the Diplomatic Reception Room door
for k in range(0, 360, 20):
    t = math.radians(k)
    lx, lz = round(ex + (erx + 3) * math.cos(t)), round(ez + (erz + 3) * math.sin(t))
    if 100 < lz < 150 and not (55 < lx < 64 and lz > 135) and not (116 < lx < 125 and lz > 135):
        lamp_post(lx, lz)
# fountain
fx, fz = 90, 134
disc(fx, fz, 7, -1, 'smooth_stone')
disc(fx, fz, 7.3, 0, 'smooth_quartz', 5.9); disc(fx, fz, 7.3, 1, 'smooth_quartz_slab', 5.9)
disc(fx, fz, 5.9, 0, 'water'); disc(fx, fz, 5.9, 1, 'air')
disc(fx, fz, 1.5, 0, 'smooth_quartz'); disc(fx, fz, 1.5, 1, 'smooth_quartz')
b.box(fx, 2, fz, fx, 3, fz, 'quartz_pillar'); b.set(fx, 4, fz, 'water')
for k in range(0, 360, 45):
    t = math.radians(k)
    b.set(round(fx + 4 * math.cos(t)), -1, round(fz + 4 * math.sin(t)), 'sea_lantern')
# helipad (Marine One): pale pad, white ring, big H
hx, hz = 90, 116
for x in range(hx - 10, hx + 11):
    for z in range(hz - 10, hz + 11):
        for yy in range(0, 12):
            b.set(x, yy, z, 'air')
        b.set(x, -1, z, 'grass_block')
disc(hx, hz, 8.4, -1, 'light_gray_concrete'); disc(hx, hz, 8.4, -1, 'white_concrete', 7.4)
for z in range(hz - 4, hz + 5):
    for x in (hx - 3, hx - 2, hx + 2, hx + 3):
        b.set(x, -1, z, 'white_concrete')
for x in range(hx - 1, hx + 2):
    b.set(x, -1, hz, 'white_concrete')
for k in range(0, 360, 90):                # landing lights
    t = math.radians(k + 45)
    b.set(round(hx + 9.5 * math.cos(t)), -1, round(hz + 9.5 * math.sin(t)), 'pearlescent_froglight')
flagpole(70, 128, h=12); flagpole(110, 128, h=12, facing='west')

# ---------------- Rose Garden (x 30..47, z 68..92) and Jacqueline Kennedy Garden (x 134..146)
def garden(x1, x2, z1, z2, roses=True):
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            for yy in range(0, 8):
                b.set(x, yy, z, 'air')
            edge = min(x - x1, x2 - x, z - z1, z2 - z)
            if edge == 0:
                b.set(x, -1, z, 'grass_block')
                b.set(x, 0, z, 'oak_leaves[persistent=true]' if (x + z) % 2 else 'azalea_leaves[persistent=true]')
            elif edge == 1:
                b.set(x, -1, z, 'smooth_sandstone')
            elif edge in (2, 3):
                b.set(x, -1, z, 'grass_block')
                if edge == 2:
                    fl = rng.choice(['rose_bush', 'rose_bush', 'peony', 'lilac']) if roses else rng.choice(['peony', 'lilac', 'rose_bush'])
                    b.set(x, 0, z, fl); b.set(x, 1, z, fl + '[half=upper]')
                else:
                    b.set(x, 0, z, rng.choice(['red_tulip', 'white_tulip', 'pink_tulip', 'lily_of_the_valley', 'oxeye_daisy']))
            elif edge == 4:
                b.set(x, -1, z, 'smooth_sandstone')
            else:
                b.set(x, -1, z, 'grass_block')
    for (x, z) in [(x1 + 2, z1 + 2), (x2 - 2, z1 + 2), (x1 + 2, z2 - 2), (x2 - 2, z2 - 2)]:
        b.ellipsoid(x, 3, z, 2, 1, 2, 'flowering_azalea_leaves[persistent=true]')
        b.set(x, 0, z, 'oak_log'); b.set(x, 1, z, 'oak_log'); b.set(x, 2, z, 'oak_log')
garden(30, 47, 68, 92)
garden(134, 146, 68, 90, roses=False)
for z in (79, 80, 81):
    for x in (30, 31, 46, 47):
        b.set(x, -1, z, 'smooth_sandstone'); b.set(x, 0, z, 'air'); b.set(x, 1, z, 'air')
for x in (38, 39):
    for z in (90, 91, 92):
        b.set(x, -1, z, 'smooth_sandstone'); b.set(x, 0, z, 'air'); b.set(x, 1, z, 'air')

# ---------------- perimeter fence x 2..177, z 13..152, gates + guard booths
GATES_N = [(66, 70), (110, 114)]
GATES_S = [(58, 61), (119, 122)]
GATES_W = [(57, 61)]
GATES_E = [(57, 61)]
def fence_cell(x, z, n):
    y = grade(z)
    b.set(x, y, z, 'polished_blackstone')
    if n % 8 == 0:
        for yy in range(y + 1, y + 4):
            b.set(x, yy, z, 'polished_blackstone_bricks')
        b.set(x, y + 4, z, 'polished_blackstone_slab')
    else:
        for yy in range(y + 1, y + 4):
            b.set(x, yy, z, 'iron_bars')
        b.set(x, y + 4, z, 'lightning_rod' if n % 2 else 'air')
def in_gate(v, gates):
    return any(a <= v <= c for a, c in gates)
for x in range(2, 178):
    if not in_gate(x, GATES_N):
        fence_cell(x, 13, x)
    if not in_gate(x, GATES_S):
        fence_cell(x, 152, x)
for z in range(13, 153):
    if not in_gate(z, GATES_W):
        fence_cell(2, z, z)
    if not in_gate(z, GATES_E):
        fence_cell(177, z, z)
for (x, z) in [(2, 44), (177, 44)]:
    for y in range(0, 13):
        b.set(x, y, z, 'polished_blackstone_bricks')
for z in range(56, 63):       # west / east gate roads (West & East Executive Ave entrances)
    for x in range(0, 8):
        b.set(x, -1, z, 'polished_andesite')
    for x in range(172, 180):
        b.set(x, -1, z, 'polished_andesite')
for z in range(153, 156):
    for x in range(0, 180):
        b.set(x, -1, z, 'gray_concrete' if z < 155 else 'smooth_stone')
for (a, c) in GATES_N:
    for x in (a - 1, c + 1):
        b.box(x, 8, 13, x, 11, 13, 'polished_blackstone_bricks'); b.set(x, 12, 13, 'lantern')
for (a, c) in GATES_S:
    for x in (a - 1, c + 1):
        b.box(x, 0, 152, x, 3, 152, 'polished_blackstone_bricks'); b.set(x, 4, 152, 'lantern')
for (a, c) in GATES_W:
    for z in (a - 1, c + 1):
        b.box(2, 0, z, 2, 3, z, 'polished_blackstone_bricks'); b.set(2, 4, z, 'lantern')
        b.box(177, 0, z, 177, 3, z, 'polished_blackstone_bricks'); b.set(177, 4, z, 'lantern')

def booth(x, y, z, door):
    b.box(x, y - 1, z, x + 3, y - 1, z + 3, 'smooth_stone')
    b.room(x, y, z, x + 3, y + 3, z + 3, 'white_concrete', ceiling='smooth_quartz')
    b.window(x, y + 1, z + 1, x, y + 2, z + 2, 'glass_pane'); b.window(x + 3, y + 1, z + 1, x + 3, y + 2, z + 2, 'glass_pane')
    b.window(x + 1, y + 1, z, x + 2, y + 2, z, 'glass_pane'); b.window(x + 1, y + 1, z + 3, x + 2, y + 2, z + 3, 'glass_pane')
    b.box(x - 1, y + 4, z - 1, x + 4, y + 4, z + 4, 'smooth_quartz_slab')
    dx, dz = {'south': (1, 3), 'north': (1, 0), 'east': (3, 1), 'west': (0, 1)}[door]
    b.door(x + dx, y, z + dz, OPPOSITE[door], 'iron_door')
    b.set(x + 2, y, z + 1, 'lectern[facing=south]')
    b.set(x + 2, y + 2, z + 2, 'lantern[hanging=true]')
BOOTHS = [(72, 8, 15, 'south'), (105, 8, 15, 'south'), (63, 0, 147, 'north'), (114, 0, 147, 'north'),
          (4, 0, 64, 'east'), (172, 0, 64, 'west')]
for bt in BOOTHS:
    booth(*bt)
# gate sign (monument) on the plaza west of the NW gate + floating text
b.box(57, 8, 10, 63, 9, 10, 'smooth_quartz'); b.box(57, 10, 10, 63, 10, 10, 'smooth_quartz_slab')
for x in (57, 63):
    b.box(x, 8, 10, x, 10, 10, 'quartz_pillar'); b.set(x, 11, 10, 'smooth_quartz_slab')
b.sign(60, 9, 11, ['THE WHITE HOUSE', '~', '1600 Pennsylvania', 'Ave NW'], 'south')
b.sign(60, 9, 9, ['THE WHITE HOUSE', '~', '1600 Pennsylvania', 'Ave NW'], 'north')
b.sign(59, 9, 11, ['', 'United States', 'Secret Service', 'RESTRICTED'], 'south')
b.sign(61, 9, 11, ['', 'Official', 'Residence of the', 'President'], 'south')
b.sign(59, 9, 9, ['', 'United States', 'Secret Service', 'RESTRICTED'], 'north')
b.sign(61, 9, 9, ['', 'Official', 'Residence of the', 'President'], 'north')
b.summon('text_display', 60, 12, 10, '{Tags:["ewhs","ewhs_text"],billboard:"center",text:{text:"THE WHITE HOUSE \u00b7 1600 Pennsylvania Ave NW",color:"white",bold:true},background:-1442840576,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.4f,1.4f,1.4f]}}')
