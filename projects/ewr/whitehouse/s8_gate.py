exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\whitehouse\lib.py").read())
# East security gate (site-local x 177, z 137..143 = world x -93, z -99..-93) + driveway to the South Lawn drive
Z1, Z2 = 137, 143
# clear the two trees in the way, then the driveway (7 wide) from the fence to the ellipse spur at x 119..122
b.box(149, 0, 134, 159, 14, 146, 'air'); b.box(167, 0, 141, 176, 14, 151, 'air')
for x in range(123, 178):
    for z in range(Z1, Z2 + 1):
        b.set(x, -1, z, 'polished_andesite')
        for y in range(0, 10):
            b.set(x, y, z, 'air')
for x in range(123, 177, 4):
    b.set(x, -1, 140, 'white_concrete') if x > 126 else None
for x in (178, 179):
    for z in range(Z1, Z2 + 1):
        for y in range(0, 10):
            b.set(x, y, z, 'air')
tree(156, 130); tree(162, 150, h=5, r=3)
# fence: gate posts, overhead red/white height bar, sliding iron gate (open, parked inside the fence line)
for z in (Z1 - 1, Z2 + 1):
    b.box(177, 0, z, 177, 5, z, 'polished_blackstone_bricks'); b.set(177, 6, z, 'lantern')
for z in range(Z1 - 1, Z2 + 2):
    b.set(177, 6, z, 'red_concrete' if z % 2 else 'white_concrete') if Z1 <= z <= Z2 else None
for z in range(Z1, Z2 + 1):
    b.set(177, 5, z, 'red_concrete' if z % 2 else 'white_concrete')
for z in range(Z2 + 2, Z2 + 9):                     # parked sliding gate panel (iron bars) just inside
    b.set(176, 0, z, 'polished_blackstone'); b.box(176, 1, z, 176, 3, z, 'iron_bars')
# raised boom barrier (red/white) on its post outside the gate
b.box(179, 0, Z2 + 1, 179, 0, Z2 + 1, 'gray_concrete')
for y in range(1, 7):
    b.set(179, y, Z2 + 1, 'red_concrete' if y % 2 else 'white_concrete')
# bollards outside and inside, not blocking the 7-wide opening
for x in range(170, 180, 2):
    for z in (Z1 - 2, Z2 + 2):
        if x == 176 and z == Z2 + 2:
            continue
        b.set(x, 0, z, 'polished_blackstone_wall'); b.set(x, 1, z, 'yellow_carpet') if False else b.set(x, 1, z, 'stone_button[face=floor]') if False else None
# inside STOP line
for z in range(Z1, Z2 + 1):
    b.set(174, -1, z, 'white_concrete')
# guard booth (inside, south of the drive)
def booth(x, y, z, door):
    b.box(x, y - 1, z, x + 3, y - 1, z + 3, 'smooth_stone')
    b.room(x, y, z, x + 3, y + 3, z + 3, 'white_concrete', ceiling='smooth_quartz')
    b.window(x, y + 1, z + 1, x, y + 2, z + 2, 'glass_pane'); b.window(x + 3, y + 1, z + 1, x + 3, y + 2, z + 2, 'glass_pane')
    b.window(x + 1, y + 1, z, x + 2, y + 2, z, 'glass_pane'); b.window(x + 1, y + 1, z + 3, x + 2, y + 2, z + 3, 'glass_pane')
    b.box(x - 1, y + 4, z - 1, x + 4, y + 4, z + 4, 'smooth_quartz_slab')
    dx, dz = {'south': (1, 3), 'north': (1, 0), 'east': (3, 1), 'west': (0, 1)}[door]
    b.door(x + dx, y, z + dz, OPPOSITE[door], 'iron_door')
    b.set(x + 2, y, z + 2, 'lectern[facing=north]')
    b.set(x + 2, y + 2, z + 1, 'lantern[hanging=true]')
booth(171, 0, Z2 + 3, 'west')
# signs
b.box(179, 0, Z1 - 4, 179, 2, Z1 - 4, 'smooth_quartz'); b.box(179, 0, Z1 - 5, 179, 2, Z1 - 5, 'smooth_quartz')
b.sign(180, 2, Z1 - 4, ['WHITE HOUSE', '~ AUTHORISED ~', 'VEHICLES ONLY', 'USSS checkpoint'], 'east')
b.sign(180, 1, Z1 - 5, ['', 'STOP', 'at the line', ''], 'east')
b.sign(180, 2, Z1 - 5, ['', 'U.S. SECRET', 'SERVICE', ''], 'east')
b.sign(176, 2, Z1 - 1, ['', 'STOP', 'Show ID', ''], 'west')
b.summon('text_display', 178, 8, 140, '{Tags:["ewhs","ewhs_text"],billboard:"center",text:{text:"WHITE HOUSE \u00b7 AUTHORISED VEHICLES ONLY",color:"red",bold:true},background:-1442840576,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.2f,1.2f,1.2f]}}')
