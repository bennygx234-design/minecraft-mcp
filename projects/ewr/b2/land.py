# B-2 apron: land reclamation, sea wall, taxiway corridor to 04R, apron paint.
# Built with world origin (0,64,0): builder (x,y,z) = world (x, 64+y, z). Ground surface y=-1.
X1, X2, Z1, Z2 = 130, 185, 45, 105

# --- reclaimed land ---
b.box(X1, -6, Z1, X2, -3, Z2, {"stone": 6, "andesite": 1})
b.box(X1, -2, Z1, X2, -2, Z2, "dirt")
b.box(X1, -1, Z1, X2, -1, Z2, "polished_andesite")      # apron slab
b.box(X1, 0, Z1, X2, 8, Z2, "air")                      # clear (kelp etc.)
# grass strips: behind the hangar and around the ops building
b.box(182, -1, 46, 184, -1, 104, "grass_block")
b.box(131, -1, 46, 131, -1, 104, "grass_block")
b.box(132, -1, 94, 155, -1, 104, "grass_block")
# concrete joint lines (every 8)
for x in range(134, 156, 8):
    for z in range(46, 94):
        if not (66 <= z <= 74):
            b.set(x, -1, z, "andesite")
for z in (54, 62, 78, 86):
    for x in range(132, 156):
        b.set(x, -1, z, "andesite")
# sea wall on the new edge (top at walking level, like stage 1)
b.box(X1, -6, Z1, X2, 0, Z1, "stone_bricks")
b.box(X1, -6, Z2, X2, 0, Z2, "stone_bricks")
b.box(X2, -6, Z1, X2, 0, Z2, "stone_bricks")
for x in range(X1, X2 + 1, 4):
    b.set(x, 0, Z1, "chiseled_stone_bricks"); b.set(x, 0, Z2, "chiseled_stone_bricks")
for z in range(Z1, Z2 + 1, 4):
    b.set(X2, 0, z, "chiseled_stone_bricks")

# --- taxiway corridor x 94..129, z 66..74 ---
for x in range(94, 130):
    road = 110 <= x <= 119
    for z in range(66, 75):
        if not road:
            b.set(x, -1, z, "polished_andesite")
    if not road:
        b.set(x, -1, 70, "yellow_concrete")              # centre line
        b.set(x, -1, 66, "light_gray_concrete"); b.set(x, -1, 74, "light_gray_concrete")  # shoulders
b.box(128, 0, 66, 129, 0, 74, "air")                    # cut the sea wall at grade
# taxiway centre line across the road (keep the road's own yellow centre)
for x in range(110, 120):
    b.set(x, -1, 70, "yellow_concrete")
# road stop bars (US right-hand traffic: southbound lane x110..113 stops at z66, northbound x116..119 at z74)
b.box(110, -1, 66, 113, -1, 66, "white_concrete")
b.box(116, -1, 74, 119, -1, 74, "white_concrete")
# taxiway hold-short lines: 2 solid + 2 dashed, dashed side toward the road
for (solid, dashed) in (((104, 105), (107, 108)), ((125, 124), (122, 121))):
    for z in range(66, 75):
        for x in solid:
            b.set(x, -1, z, "yellow_concrete")
        for x in dashed:
            if z % 2 == 0:
                b.set(x, -1, z, "yellow_concrete")
# hold position signs (red with white text) next to the hold lines
for x, face in ((106, "west"), (123, "east")):
    for z in (66, 74):
        b.set(x, 0, z, "polished_blackstone_wall")
        b.set(x, 1, z, "red_concrete")
        b.sign(x + (-1 if face == "west" else 1), 1, z, ["HOLD", "SHORT", "NJ TPK"], facing=face)
# STOP signs for turnpike traffic
b.set(109, 0, 67, "polished_blackstone_wall"); b.set(109, 1, 67, "polished_blackstone_wall")
b.set(109, 2, 67, "red_concrete"); b.sign(109, 2, 66, ["", "STOP", "AIRCRAFT", "CROSSING"], facing="north")
b.set(120, 0, 73, "polished_blackstone_wall"); b.set(120, 1, 73, "polished_blackstone_wall")
b.set(120, 2, 73, "red_concrete"); b.sign(120, 2, 74, ["", "STOP", "AIRCRAFT", "CROSSING"], facing="south")
# warning lights (wig-wag) on the road shoulders
for x, z in ((109, 72), (120, 68)):
    b.set(x, 0, z, "polished_blackstone_wall"); b.set(x, 1, z, "polished_blackstone_wall")
    b.set(x, 2, z, "redstone_lamp"); b.set(x, 3, z, "polished_blackstone_slab")
# blue taxiway edge lights
for x in list(range(95, 104, 4)) + list(range(126, 128)) :
    pass
for x in (96, 100, 127):
    b.set(x, 0, 66, "soul_lantern"); b.set(x, 0, 74, "soul_lantern")

# --- apron markings ---
# lead-in line from the corridor to the hangar door (x 156), plus edge lines
b.box(130, -1, 70, 156, -1, 70, "yellow_concrete")
b.box(130, -1, 66, 155, -1, 66, "light_gray_concrete"); b.box(130, -1, 74, 155, -1, 74, "light_gray_concrete")
# red "no parking" box in front of the hangar door
for x in range(148, 156):
    b.set(x, -1, 52, "red_concrete"); b.set(x, -1, 88, "red_concrete")
# USAF painted on the apron (5x7 font, stretched x2 in z), reads west->east, top to the north
F5 = {
    "U": ["X...X", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "S": [".XXXX", "X....", "X....", ".XXX.", "....X", "....X", "XXXX."],
    "A": [".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "F": ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "X...."],
}
x0, z0 = 132, 79
for i, ch in enumerate("USAF"):
    for r, row in enumerate(F5[ch]):
        for c, px in enumerate(row):
            if px == "X":
                for k in range(2):
                    b.set(x0 + i * 6 + c, -1, z0 + r * 2 + k, "white_concrete")
