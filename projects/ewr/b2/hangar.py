# B-2 hangar (x 160..184, z 48..92, door on the west facing the taxiway) + security, ops, lights.
# World origin (0,64,0). Keep out of the flyable B-2 footprint x 146..159, z 64..97.
HX1, HX2, HZ1, HZ2, HH = 160, 184, 48, 92, 12     # roof at y=HH

FONT = {
    "A": ["XXX", "X.X", "XXX", "X.X", "X.X"], "B": ["XX.", "X.X", "XX.", "X.X", "XX."],
    "F": ["XXX", "X..", "XX.", "X..", "X.."], "H": ["X.X", "X.X", "XXX", "X.X", "X.X"],
    "I": ["XXX", ".X.", ".X.", ".X.", "XXX"], "P": ["XX.", "X.X", "XX.", "X..", "X.."],
    "R": ["XX.", "X.X", "XX.", "X.X", "X.X"], "S": [".XX", "X..", ".X.", "..X", "XX."],
    "T": ["XXX", ".X.", ".X.", ".X.", ".X."], "U": ["X.X", "X.X", "X.X", "X.X", "XXX"],
    "0": ["XXX", "X.X", "X.X", "X.X", "XXX"], "2": ["XX.", "..X", ".X.", "X..", "XXX"],
    "5": ["XXX", "X..", "XX.", "..X", "XX."], "9": ["XXX", "X.X", "XXX", "..X", "XXX"],
    "-": ["...", "...", "XXX", "...", "..."], " ": ["...", "...", "...", "...", "..."],
}


def letters(text, put, ytop, sw=1, gap=1):
    """put(k, y): k = position along the reading direction (0..)."""
    k0 = 0
    for ch in text:
        g = FONT[ch]
        for r, row in enumerate(g):
            for c, px in enumerate(row):
                if px == "X":
                    for s in range(sw):
                        put(k0 + c * sw + s, ytop - r)
        k0 += 3 * sw + gap


# ---------------- hangar shell ----------------
b.box(HX1, -1, HZ1, HX2, -1, HZ2, "polished_deepslate")                       # slab
b.box(HX1 + 1, -1, HZ1 + 1, HX2 - 1, -1, HZ2 - 1, "light_gray_concrete")      # epoxy floor
for x in (HX1, HX2):
    b.box(x, 0, HZ1, x, HH - 1, HZ2, "deepslate_tiles")
for z in (HZ1, HZ2):
    b.box(HX1, 0, z, HX2, HH - 1, z, "deepslate_tiles")
for (x1, z1, x2, z2) in ((HX1, HZ1, HX2, HZ1), (HX1, HZ2, HX2, HZ2), (HX1, HZ1, HX1, HZ2), (HX2, HZ1, HX2, HZ2)):
    b.box(x1, 0, z1, x2, 0, z2, "polished_blackstone_bricks")                # dark plinth course
# pilasters
for z in range(HZ1, HZ2 + 1, 6):
    b.box(HX2, 0, z, HX2, HH - 1, z, "polished_basalt")
for x in range(HX1, HX2 + 1, 6):
    b.box(x, 0, HZ1, x, HH - 1, HZ1, "polished_basalt"); b.box(x, 0, HZ2, x, HH - 1, HZ2, "polished_basalt")
for z in (HZ1, 51, 89, HZ2):
    b.box(HX1, 0, z, HX1, HH - 1, z, "polished_basalt")
# clerestory windows on the side walls
for x in range(HX1 + 2, HX2 - 1, 6):
    for z in (HZ1, HZ2):
        b.box(x, 8, z, x + 2, 9, z, "gray_stained_glass")
# roof with a skylight strip and parapet
b.box(HX1, HH, HZ1, HX2, HH, HZ2, "polished_deepslate")
b.box(HX1 + 3, HH, 69, HX2 - 3, HH, 71, "gray_stained_glass")
b.box(HX1, HH + 1, HZ1, HX2, HH + 1, HZ2, "polished_blackstone_slab[type=bottom]", hollow=True)
b.box(HX1 + 1, HH + 1, HZ1 + 1, HX2 - 1, HH + 1, HZ2 - 1, "air")
for x, z in ((168, 54), (176, 54), (168, 86), (176, 86)):                    # roof vents / AC units
    b.box(x, HH + 1, z, x + 2, HH + 2, z + 2, "light_gray_concrete")
    b.box(x, HH + 3, z, x + 2, HH + 3, z + 2, "iron_trapdoor[half=bottom,facing=north]")
b.set(182, HH + 1, 50, "lightning_rod"); b.set(182, HH + 2, 50, "lightning_rod")
# wide low door opening facing the taxiway (z 52..88 = 37 wide for the 33-block span), 7 high
b.box(HX1, 0, 52, HX1, 6, 88, "air")
b.box(HX1, 7, 51, HX1, 7, 89, "polished_blackstone")                         # door header / track
for y in range(0, 7):                                                         # hazard-striped jambs
    blk = "yellow_concrete" if y % 2 == 0 else "black_concrete"
    b.set(HX1, y, 51, blk); b.set(HX1, y, 89, blk)
for z in range(52, 89):                                                       # threshold stripe
    b.set(HX1, -1, z, "yellow_concrete" if (z // 2) % 2 == 0 else "black_concrete")
# stacked sliding door leaves parked at both ends inside
for z in (49, 50, 90, 91):
    b.box(HX1 + 1, 0, z, HX1 + 1, 7, z, "polished_basalt")
    b.set(HX1 + 1, 8, z, "polished_blackstone_slab[type=bottom]")
# "USAF" across the facade above the door (white, set into the wall; reads north->south from outside)
letters("USAF", lambda k, y: b.set(HX1, y, 55 + k, "white_concrete"), 11, sw=2, gap=2)
# signs on the facade, beside the door (outside the parked flyable B-2)
b.sign(HX1 - 1, 3, 49, ["509th", "BOMB WING"], facing="west")
b.sign(HX1 - 1, 3, 50, ["509th BOMB WING", "·", "B-2 SPIRIT"], facing="west")
b.sign(HX1 - 1, 2, 50, ["USAF", "RESTRICTED", "AREA"], facing="west")

# ---------------- interior ----------------
# floor markings
b.box(163, -1, 53, 177, -1, 53, "red_concrete"); b.box(163, -1, 87, 177, -1, 87, "red_concrete")
b.box(163, -1, 53, 163, -1, 87, "red_concrete"); b.box(177, -1, 53, 177, -1, 87, "red_concrete")
b.box(HX1, -1, 70, 166, -1, 70, "yellow_concrete")                           # lead-in to the nose wheel
b.box(166, -1, 68, 166, -1, 72, "yellow_concrete")                           # nose-wheel stop bar
for z in range(49, 92):                                                       # weapons-bay boundary
    b.set(178, -1, z, "yellow_concrete" if z % 2 else "black_concrete")
for x in range(161, 178, 2):                                                  # walkway lines along the walls
    b.set(x, -1, 50, "white_concrete"); b.set(x, -1, 90, "white_concrete")
# roof trusses with hanging lights
for x in (163, 169, 175, 181):
    b.box(x, HH - 1, HZ1 + 1, x, HH - 1, HZ2 - 1, "polished_blackstone")
    for z in range(51, 91, 4):
        b.set(x, HH - 2, z, "iron_chain"); b.set(x, HH - 3, z, "sea_lantern")
for x in range(161, 184, 3):                                                  # wall lights
    b.set(x, 5, HZ1, "sea_lantern"); b.set(x, 5, HZ2, "sea_lantern")
for z in range(52, 90, 6):
    b.set(HX2, 5, z, "sea_lantern")
# wall lettering: "509TH" (north wall), "USAF" (south wall), "B-2 SPIRIT" (back wall)
letters("509TH", lambda k, y: b.set(163 + k, y, HZ1 + 1, "white_concrete"), 10)
letters("USAF", lambda k, y: b.set(180 - k, y, HZ2 - 1, "white_concrete"), 10)
letters("B-2 SPIRIT", lambda k, y: b.set(HX2 - 1, y, 51 + k, "white_concrete"), 11)
b.sign(HX2 - 1, 4, 69, ["509th", "BOMB WING"], facing="west")
b.sign(HX2 - 1, 4, 70, ["509th BOMB WING", "·", "B-2 SPIRIT"], facing="west")
b.sign(HX2 - 1, 4, 71, ["USAF", "WHITEMAN AFB"], facing="west")
b.sign(HX2 - 1, 4, 60, ["TOOL CRIB", "SIGN OUT ALL", "TOOLS"], facing="west")
b.sign(HX2 - 1, 4, 80, ["MUNITIONS", "AUTHORIZED", "PERSONNEL ONLY"], facing="west")

# maintenance stand at the nose (deck surface at y=4, level with the windscreen)
b.box(161, 3, 66, 162, 3, 75, "smooth_stone_slab[type=top]")
for x, z in ((161, 66), (162, 66), (161, 75), (162, 75), (161, 70), (162, 70)):
    b.box(x, 0, z, x, 2, z, "yellow_concrete")
b.box(161, 4, 66, 161, 4, 75, "iron_bars"); b.box(162, 4, 66, 162, 4, 66, "iron_bars")
b.stairs_run(161, 0, 79, "north", 4, "polished_andesite_stairs", width=2, support="yellow_concrete")
b.set(162, 4, 72, "lantern")
# ground power cart + fire extinguisher stations near the wing
b.box(170, 0, 51, 172, 0, 51, "yellow_concrete"); b.set(171, 1, 51, "iron_trapdoor[half=bottom,facing=north]")
for z in (60, 80):
    b.set(161, 0, z, "red_concrete"); b.set(161, 1, z, "red_concrete_powder")

# ---------------- weapons / maintenance bay along the back wall (x 179..183) ----------------
racks = ["anvil[facing=north]", "grindstone[face=floor,facing=west]", "smithing_table", "stonecutter[facing=west]",
         "crafting_table", "cauldron", "fletching_table", "blast_furnace[facing=west]"]
for i, z in enumerate(list(range(50, 63)) + list(range(78, 91))):
    b.set(183, 0, z, racks[i % len(racks)])
    b.set(183, 1, z, "iron_trapdoor[half=top,facing=west,open=true]")      # pegboard
    b.set(183, 2, z, "chiseled_bookshelf[facing=west]" if i % 3 else "chest[facing=west]")
    b.set(183, 3, z, "polished_blackstone_slab[type=bottom]")
# crate stacks
CR = {"barrel[facing=up]": 2, "green_terracotta": 2, "stripped_spruce_wood": 1, "spruce_planks": 1}
for (x1, z1, x2, z2, h) in ((179, 50, 181, 53, 3), (179, 87, 181, 90, 3), (180, 56, 181, 58, 2), (180, 82, 181, 84, 2)):
    b.box(x1, 0, z1, x2, h - 1, z2, CR)
# munitions on carts behind the tail (x 179..182, z 63..77)
for z in (64, 66, 68, 72, 74, 76):
    b.box(179, 0, z, 182, 0, z, "iron_trapdoor[half=top,facing=north]")      # cart bed
    b.set(178, 1, z, "lightning_rod[facing=west]")                           # fuse nose
    b.box(179, 1, z, 182, 1, z, "polished_basalt[axis=x]")
    b.set(180, 1, z, "yellow_terracotta")                                   # HE band
    b.set(183, 1, z, "iron_bars") if False else None
for z in (65, 67, 73, 75):
    b.set(182, 0, z, "black_concrete")                                      # cart wheels
b.box(179, 0, 70, 182, 0, 70, "yellow_concrete")                            # bomb lift (MJ-1 "jammer")
b.set(178, 0, 70, "polished_blackstone_wall"); b.set(178, 1, 70, "lever[face=floor,facing=west]")

# ---------------- security fence, gate, guard post ----------------
for z in list(range(46, 66)) + list(range(75, 105)):
    b.box(131, 0, z, 131, 2, z, "iron_bars")
    if z % 5 == 0:
        b.box(131, 0, z, 131, 3, z, "polished_blackstone_wall")
for x in range(130, 186):
    b.box(x, 1, 45, x, 2, 45, "iron_bars"); b.box(x, 1, 105, x, 2, 105, "iron_bars")
for z in range(45, 106):
    b.box(185, 1, z, 185, 2, z, "iron_bars")
for x in range(130, 186, 5):
    b.set(x, 3, 45, "polished_blackstone_wall"); b.set(x, 3, 105, "polished_blackstone_wall")
# gate posts with red/white boom (raised)
for z in (65, 75):
    b.box(131, 0, z, 131, 3, z, "polished_blackstone_bricks"); b.set(131, 4, z, "polished_blackstone_wall")
b.set(132, 0, 65, "red_concrete")
for y in range(1, 9):
    b.set(132, y, 65, "red_wool" if y % 2 else "white_wool")
b.sign(130, 2, 64, ["RESTRICTED", "AREA", "USE OF DEADLY", "FORCE AUTHORIZED"], facing="west")
b.sign(130, 2, 76, ["509th BOMB WING", "·", "B-2 SPIRIT", "ID REQUIRED"], facing="west")
# guard post x 132..136, z 58..63
b.box(132, -1, 58, 136, -1, 63, "polished_andesite")
b.box(132, 0, 58, 136, 3, 63, "white_concrete", hollow=True)
b.box(133, 1, 58, 135, 2, 58, "glass_pane"); b.box(133, 1, 63, 135, 2, 63, "glass_pane")
b.box(132, 1, 59, 132, 2, 62, "glass_pane"); b.box(136, 1, 59, 136, 2, 62, "glass_pane")
b.box(132, 3, 58, 136, 3, 63, "light_gray_concrete")
b.box(131, 4, 57, 137, 4, 64, "smooth_stone_slab[type=bottom]")
b.door(136, 0, 61, "west", "iron_door")
b.set(137, 0, 60, "stone_button[face=floor,facing=west]") if False else None
b.chair(134, 0, 61, "west", "spruce_stairs")
b.long_table(133, 59, 133, 62, 0, "spruce_slab")
b.set(133, 1, 60, "lever[face=floor,facing=west]")
b.set(134, 2, 60, "lantern[hanging=true]")
b.sign(132, 2, 64, ["SECURITY", "FORCES", "ID CHECK"], facing="south") if False else None
b.sign(134, 3, 64, ["SECURITY FORCES", "ENTRY CONTROL"], facing="south")
b.set(134, 4, 60, "redstone_lamp") ; b.set(134, 5, 60, "lightning_rod")

# ---------------- floodlights ----------------
for (x, z, dx, dz) in ((133, 49, 1, 1), (157, 49, -1, 1), (157, 101, -1, -1), (133, 92, 1, -1), (182, 46, -1, 0), (182, 94, -1, 0)):
    b.box(x, 0, z, x, 8, z, "polished_blackstone_wall")
    b.set(x, 9, z, "sea_lantern"); b.set(x + dx, 9, z, "sea_lantern"); b.set(x, 9, z + dz, "sea_lantern")
    b.set(x, 10, z, "polished_blackstone_slab[type=bottom]"); b.set(x + dx, 10, z, "polished_blackstone_slab[type=bottom]")
    b.set(x, 10, z + dz, "polished_blackstone_slab[type=bottom]")

# ---------------- blast fence (north edge of the apron, deflector slopes up to the north) ----------------
for x in range(136, 157):
    for i, z in enumerate((49, 48, 47, 46)):
        if i:
            b.box(x, 0, z, x, i - 1, z, "light_gray_concrete")
        b.set(x, i, z, "polished_andesite_stairs[facing=north,half=bottom]")
    if x % 4 == 0:
        b.set(x, 4, 46, "red_concrete")
b.sign(146, 0, 50, ["CAUTION", "JET BLAST"], facing="south", wall=False)

# ---------------- ops building x 132..144, z 95..104 ----------------
OX1, OX2, OZ1, OZ2 = 132, 144, 95, 104
b.box(OX1, -1, OZ1, OX2, -1, OZ2, "polished_andesite")
b.box(OX1, 0, OZ1, OX2, 4, OZ2, "light_gray_concrete", hollow=True)
b.box(OX1, 0, OZ1, OX2, 0, OZ2, "gray_concrete", hollow=True)
b.box(OX1 + 1, 0, OZ1 + 1, OX2 - 1, 0, OZ2 - 1, "air")
b.box(OX1 + 1, -1, OZ1 + 1, OX2 - 1, -1, OZ2 - 1, "gray_concrete")          # floor
for x in range(OX1 + 1, OX2, 3):
    b.box(x, 1, OZ1, x + 1, 2, OZ1, "gray_stained_glass_pane")
    b.box(x, 1, OZ2, x + 1, 2, OZ2, "gray_stained_glass_pane")
for z in range(OZ1 + 2, OZ2 - 1, 3):
    b.box(OX1, 1, z, OX1, 2, z + 1, "gray_stained_glass_pane"); b.box(OX2, 1, z, OX2, 2, z + 1, "gray_stained_glass_pane")
b.box(OX1, 4, OZ1, OX2, 4, OZ2, "smooth_stone")
b.box(OX1, 5, OZ1, OX2, 5, OZ2, "smooth_stone_slab[type=bottom]", hollow=True)
b.box(OX1 + 1, 5, OZ1 + 1, OX2 - 1, 5, OZ2 - 1, "air")
b.box(137, 0, OZ1, 138, 1, OZ1, "air")
b.double_door(138, 0, OZ1, "south", "iron_door")
b.box(137, 3, OZ1 - 1, 140, 3, OZ1 - 1, "polished_blackstone_slab[type=top]")   # entrance canopy
b.sign(141, 2, OZ1 - 1, ["509th OPS GROUP", "B-2 SPIRIT", "OPERATIONS"], facing="north")
# ops desks + monitors along the south wall
b.long_table(OX1 + 1, OZ2 - 1, OX2 - 1, OZ2 - 1, 0, "spruce_slab")
for x in range(OX1 + 1, OX2):
    b.set(x, 1, OZ2 - 1, "black_stained_glass_pane" if x % 2 else "air")
    if x % 2:
        b.chair(x, 0, OZ2 - 2, "south", "spruce_stairs")
# briefing table
b.long_table(135, 98, 141, 99, 0, "dark_oak_slab")
for x in range(135, 142, 2):
    b.chair(x, 0, 97, "south", "dark_oak_stairs"); b.chair(x, 0, 100, "north", "dark_oak_stairs")
b.set(134, 0, 97, "lectern[facing=east]")
b.set(143, 0, 96, "cartography_table"); b.set(143, 0, 97, "jukebox"); b.set(143, 1, 97, "note_block")
b.set(133, 0, 96, "chest[facing=east]"); b.set(133, 0, 97, "barrel[facing=up]")
for x in (135, 138, 141):
    b.set(x, 3, 98, "lantern[hanging=true]"); b.set(x, 3, 102, "lantern[hanging=true]")
# roof: antenna mast + satellite dish
b.box(142, 5, 102, 142, 9, 102, "iron_bars"); b.set(142, 10, 102, "lightning_rod")
b.box(134, 5, 101, 135, 5, 102, "white_concrete"); b.set(134, 6, 101, "white_concrete_powder") if False else None
b.set(134, 6, 102, "smooth_quartz_slab[type=bottom]"); b.set(135, 6, 102, "smooth_quartz_stairs[facing=west]")
# flagpole with a US flag
b.box(147, 0, 101, 147, 9, 101, "iron_bars"); b.set(147, 10, 101, "end_rod")
for i in range(6):
    for j in range(4):
        y = 9 - j
        blk = ("blue_wool" if (i < 3 and j < 2) else ("red_wool" if j % 2 == 0 else "white_wool"))
        b.set(148 + i, y, 101, blk)
