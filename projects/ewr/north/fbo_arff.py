exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\north\lib.py").read())

TW, TE = -19, -12

# ================= FBO (general aviation terminal), s 300..321 =================
S1, S2 = 300, 321
rect(S1, S2, TW, TE, -1, "polished_diorite")
pbox(S1, S2, TW, TE, 0, 8, "white_concrete", hollow=True)
pbox(S1 + 1, S2 - 1, TW + 1, TE - 1, 0, 7, "air")
rect(S1 + 1, S2 - 1, TW + 1, TE - 1, 4, "smooth_quartz")          # 2nd floor slab
# glass curtain walls on south + east, vertical mullions
for s in range(S1 + 1, S2):
    if (s - S1) % 4:
        pbox(s, s, TE, TE, 1, 3, "light_blue_stained_glass"); pbox(s, s, TE, TE, 5, 7, "light_blue_stained_glass")
for t in range(TW + 1, TE):
    pbox(S1, S1, t, t, 1, 3, "light_blue_stained_glass"); pbox(S1, S1, t, t, 5, 7, "light_blue_stained_glass")
pbox(S2, S2, TW + 2, TE - 2, 5, 6, "light_blue_stained_glass")
# roof + parapet
rect(S1, S2, TW, TE, 8, "smooth_stone")
for s in range(S1, S2 + 1):
    for t in (TW, TE):
        put(s, t, 9, "white_concrete")
for t in range(TW, TE + 1):
    put(S1, t, 9, "white_concrete"); put(S2, t, 9, "white_concrete")
# rooftop HVAC
pbox(312, 314, -17, -15, 9, 10, "light_gray_concrete"); put(313, -16, 11, "iron_trapdoor[half=bottom]")
# sign fascia over the east face (faces the runway) : "FBO"
pbox(304, 316, TE, TE, 9, 14, "blue_concrete")
text_east(TE, 305, 13, "FBO", "white_concrete")
# entrance: south face double door + canopy
x, z = P(S1, -16)
b.box(x, 0, z, x + 1, 2, z, "air")
b.double_door(x, 0, z, "north", "iron_door")
rect(S1 - 1, S1 - 1, -18, -13, 4, "smooth_quartz_slab[type=bottom]")
x, z = P(S1 - 1, -14); b.sign(x, 3, z, ["EWR FBO", "General Aviation", "Pilot Lounge", "Customs"], facing="south")
# side door to the airside (east)
x, z = P(313, TE); b.box(x, 0, z, x, 1, z, "air"); b.door(x, 0, z, "west", "iron_door")
# ---- ground floor: lobby
for t in range(-18, -14):
    put(304, t, 0, "smooth_quartz"); put(304, t, 1, "smooth_quartz_slab[type=bottom]")
x, z = P(305, -17); b.chair(x, 0, z, "south")
x, z = P(305, -15); b.chair(x, 0, z, "south")
put(305, -18, 0, "lectern[facing=south]")
# lounge
x, z = P(308, -18); b.sofa(x, 0, z, "east", length=3, seat="quartz_stairs", arm=None)
x, z = P(308, -13); b.sofa(x, 0, z, "west", length=4, seat="quartz_stairs", arm=None)
for s in (309, 310):
    put(s, -16, 0, "spruce_slab[type=top]"); put(s, -15, 0, "spruce_slab[type=top]")
b.plant(P(302, -18)[0], 0, P(302, -18)[1], "potted_bamboo")
b.plant(P(302, -13)[0], 0, P(302, -13)[1], "potted_fern")
# coffee bar + pilot shop
x, z = P(318, -18); b.kitchen(x, 0, z, "south", length=6,
                             appliances=("smoker", "barrel", "water_cauldron[level=3]", "brewing_stand", "barrel", "crafting_table"))
b.bookshelves(P(314, -18)[0], 0, P(314, -18)[1], P(316, -18)[0], 2, P(316, -18)[1], mix=False)
put(314, -13, 0, "chest[facing=west]"); put(315, -13, 0, "barrel[facing=up]")
for s in (306, 312, 317):
    put(s, -16, 3, "sea_lantern")
# stairs: ladder in the north-west corner
x, z = P(320, -13); b.ladder(x, 0, z, 5, "south"); put(320, -13, 4, "air")
put(320, -13, 4, "ladder[facing=south]")
# ---- upper floor: flight planning + crew rest
for t in range(-17, -14):
    put(304, t, 5, "spruce_slab[type=top]"); put(305, t, 5, "spruce_slab[type=top]")
for t in range(-17, -14):
    x, z = P(303, t); b.chair(x, 5, z, "north")
    x, z = P(306, t); b.chair(x, 5, z, "south")
put(304, -18, 5, "cartography_table"); put(305, -18, 5, "lectern[facing=east]")
x, z = P(311, -18); b.sofa(x, 5, z, "east", length=3, seat="spruce_stairs", arm=None)
put(312, -16, 5, "spruce_slab[type=top]")
for s in (316, 318):
    x, z = P(s, -18); b.bed(x, 5, z, "north", "light_blue")
for s in (316, 318):
    x, z = P(s, -15); b.bed(x, 5, z, "north", "white")
b.bookshelves(P(314, -13)[0], 5, P(314, -13)[1], P(312, -13)[0], 6, P(312, -13)[1])
for s in (303, 309, 315, 319):
    put(s, -16, 7, "sea_lantern")
b.plant(P(308, -13)[0], 5, P(308, -13)[1], "potted_azalea_bush")

# ================= ARFF fire station, s 324..350 =================
A1, A2 = 324, 350
rect(A1, A2, TW, TE, -1, "polished_andesite")
pbox(A1, A2, TW, TE, 0, 10, "red_concrete", hollow=True)
pbox(A1 + 1, A2 - 1, TW + 1, TE - 1, 0, 9, "air")
rect(A1 + 1, A2 - 1, TW + 1, TE - 1, 5, "smooth_stone")           # 2nd floor
rect(A1, A2, TW, TE, 10, "smooth_stone")
for s in range(A1, A2 + 1):
    put(s, TE, 4, "white_concrete"); put(s, TE, 5, "white_concrete")   # white band
for t in range(TW, TE + 1):
    put(A1, t, 4, "white_concrete"); put(A1, t, 5, "white_concrete")
    put(A1, t, 11, "red_concrete"); put(A2, t, 11, "red_concrete")
for s in range(A1, A2 + 1):
    put(s, TW, 11, "red_concrete"); put(s, TE, 11, "red_concrete")
# apparatus bays facing east (toward runway 04L)
BAYS = [(326, 330), (333, 337), (340, 344)]
for i, (a, c) in enumerate(BAYS):
    pbox(a, c, TE, TE, 0, 3, "air")
    pbox(a - 1, a - 1, TE, TE, 0, 3, "white_concrete"); pbox(c + 1, c + 1, TE, TE, 0, 3, "white_concrete")
    if i == 2:   # closed roller door
        for y in range(0, 4):
            pbox(a, c, TE, TE, y, y, "white_concrete" if y != 2 else "light_gray_stained_glass")
    else:        # rolled-up door
        pbox(a, c, TE, TE, 3, 3, "iron_trapdoor[facing=east,half=top,open=false]")
    # fire truck, nose east
    v = at((a + c) // 2, -16, 0, rot=1)
    for xx in (-1, 1):
        for zz in (-2, 1):
            v.set(xx, 0, zz, "black_concrete")
    v.box(-1, 1, -3, 1, 2, 2, "red_concrete")
    v.box(-1, 1, -3, 1, 1, 2, "red_concrete")
    v.set(-1, 1, -1, "white_concrete"); v.set(1, 1, -1, "white_concrete")
    v.set(-1, 1, 0, "white_concrete"); v.set(1, 1, 0, "white_concrete")
    v.box(-1, 2, -3, 1, 2, -3, "black_stained_glass")
    v.set(-1, 3, -2, "red_stained_glass"); v.set(0, 3, -2, "white_stained_glass"); v.set(1, 3, -2, "blue_stained_glass")
    v.set(0, 3, -1, "lightning_rod[facing=north]")
    v.box(-1, 3, 0, 1, 3, 2, "iron_trapdoor[half=bottom]")
    if i < 2:   # turnout-gear lockers between bays
        for t in range(-18, -14):
            put(c + 1, t, 0, "barrel[facing=up]"); put(c + 2, t, 0, "barrel[facing=up]")
        x, z = P(c + 1, -14); b.chest(x, 0, z, "south", [("bucket", 4), ("water_bucket", 2)])
    put((a + c) // 2, -16, 4, "sea_lantern")
# bay floor lines
for (a, c) in BAYS:
    for s in (a - 1, c + 1):
        rect(s, s, TW + 1, TE, -1, "yellow_concrete")
# gear room north end s 346..349 ground
for t in range(-18, -13):
    put(349, t, 0, "barrel[facing=south]"); put(349, t, 1, "chest[facing=south]")
put(347, -18, 0, "crafting_table")
# ladder to 2nd floor against the west wall at s 347
x, z = P(347, -18)
b.ladder(x, 0, z, 6, "east"); put(347, -18, 5, "ladder[facing=east]")
# personnel door, south face
x, z = P(A1, -16); b.box(x, 0, z, x, 1, z, "air"); b.door(x, 0, z, "north", "iron_door")
x, z = P(A1 - 1, -14); b.sign(x, 2, z, ["PANYNJ", "ARFF Station", "Fire Rescue", "EWR"], facing="south")
# windows band, 2nd floor
for s in range(A1 + 1, A2):
    if s % 3:
        put(s, TE, 7, "glass"); put(s, TW, 7, "glass")
for t in range(TW + 1, TE):
    put(A1, t, 7, "glass"); put(A2, t, 7, "glass")
# "ARFF" letters on the east face above the bays
pbox(326, 344, TE, TE, 6, 10, "red_concrete")
text_east(TE, 328, 10, "ARFF", "white_concrete")
# 2nd floor: crew quarters
for s in range(326, 336, 2):
    x, z = P(s, -18); b.bed(x, 6, z, "south", "red")
x, z = P(338, -18); b.kitchen(x, 6, z, "east", length=4)
for s in (340, 341):
    put(s, -15, 6, "spruce_slab[type=top]")
x, z = P(340, -14); b.chair(x, 6, z, "west")
x, z = P(341, -16); b.chair(x, 6, z, "east")
x, z = P(345, -18); b.sofa(x, 6, z, "east", length=3, seat="red_nether_brick_stairs", arm=None)
put(345, -13, 6, "jukebox")
for s in (328, 334, 340, 346):
    put(s, -16, 9, "sea_lantern")
# watch tower at the north end
pbox(345, 350, -19, -14, 11, 12, "red_concrete")
pbox(345, 350, -19, -14, 13, 15, "light_blue_stained_glass", hollow=True)
pbox(346, 349, -18, -15, 11, 15, "air")
rect(346, 349, -18, -15, 10, "smooth_stone")
rect(345, 350, -19, -14, 16, "red_concrete")
put(347, -16, 17, "sea_lantern")
put(347, -16, 18, "red_stained_glass")
x, z = P(348, -17); b.chair(x, 11, z, "east"); put(348, -15, 11, "lectern[facing=west]")
x, z = P(347, -18); b.ladder(x, 6, z, 5, "east")
put(347, -18, 10, "ladder[facing=east]")

# ================= apron: markings, tugs, GPUs, bizjet, fuel truck =================
for tc, sf in ((-84, 312), (-56, 318), (-32, 318)):
    rect(301, sf - 4, tc, tc, -1, "yellow_concrete")          # lead-in lines
    tug(at(sf - 7, tc - 2, 0, rot=0))                           # tug waiting to tow out
    gpu(at(sf - 6, tc - 6, 0))
rect(304, 304, -84, -22, -1, "yellow_concrete")                # apron taxilane
rect(300, 304, -40, -40, -1, "yellow_concrete")                # tie-in to the south connector
for t in range(-99, -12, 2):
    put(300, t, -1, "white_concrete")                            # apron edge
# bizjet on the FBO ramp (nose south), with chocks
bizjet(at(308, -25, 0, rot=2), "blue_concrete")
# fuel truck along the south edge
fv = at(301, -62, 0, rot=1)
fv.box(0, 0, -3, 0, 0, 3, "black_concrete")
fv.box(-1, 1, -3, 1, 2, -2, "white_concrete"); fv.box(-1, 2, -3, 1, 2, -3, "black_stained_glass")
fv.box(-1, 1, -1, 1, 2, 3, "light_gray_concrete"); fv.box(-1, 1, -1, 1, 1, 3, "red_concrete")
# baggage carts + belt loader near H1
for k in range(3):
    put(302, -95 + 3 * k, 0, "gray_concrete"); put(302, -94 + 3 * k, 0, "gray_concrete")
    put(302, -95 + 3 * k, 1, "barrel[facing=up]"); put(302, -94 + 3 * k, 1, "barrel[facing=up]")
tug(at(302, -98, 0, rot=1), "white_concrete")
# light masts
for t in (-90, -60, -30):
    pbox(300, 300, t, t, 0, 7, "iron_bars"); put(300, t, 8, "sea_lantern")
