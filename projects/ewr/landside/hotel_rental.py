exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\landside\common.py").read())

# ---------------------------------------------------------------- Newark Airport Marriott
HS1, HS2 = 102, 124
pbox(HS1, HS2, -142, -123, 0, 56, "air")
rect(HS1, HS2, -142, -123, -1, "smooth_stone")
# driveway / porte-cochere apron
rect(HS1 + 4, HS2 - 4, -128, -123, -1, "gray_concrete")
for s in range(HS1 + 4, HS2 - 3, 2):
    put(s, -123, -1, "white_concrete")

# podium (lobby, restaurant), walk 0, roof slab y=5
PS1, PS2, PT1, PT2 = 103, 123, -141, -129
pbox(PS1, PS2, PT1, PT2, 0, 4, "white_concrete", hollow=True)
rect(PS1, PS2, PT1, PT2, -1, "polished_diorite")
rect(PS1, PS2, PT1, PT2, 5, "white_concrete")
# glass curtain wall on the podium
for s in range(PS1 + 1, PS2):
    if (s - PS1) % 4:
        pbox(s, s, PT2, PT2, 0, 3, "light_blue_stained_glass")
        pbox(s, s, PT1, PT1, 1, 3, "light_blue_stained_glass")
for t in range(PT1 + 1, PT2):
    if (t - PT1) % 4:
        pbox(PS1, PS1, t, t, 1, 3, "light_blue_stained_glass")
        pbox(PS2, PS2, t, t, 1, 3, "light_blue_stained_glass")
# main entrance (east) and canopy
mid = 113
pbox(mid - 1, mid + 1, PT2, PT2, 0, 2, "air")
x, z = P(mid - 1, PT2); b.door(x, 0, z, "west", "birch_door", "left")
x, z = P(mid + 1, PT2); b.door(x, 0, z, "west", "birch_door", "right")
put(mid, PT2, 0, "air"); put(mid, PT2, 1, "air")
pbox(HS1 + 6, HS2 - 6, -128, -124, 4, 4, "white_concrete")
pbox(HS1 + 6, HS2 - 6, -128, -124, 5, 5, "red_concrete")
for s in (HS1 + 6, HS2 - 6):
    pbox(s, s, -124, -124, 0, 3, "smooth_quartz")
for s in range(HS1 + 8, HS2 - 6, 3):
    put(s, -126, 3, "lantern[hanging=true]")
x, z = P(mid, -124)
b.sign(x, 2, z, ["Newark Airport", "MARRIOTT", "Hotel Entrance"], facing="east")
# lobby interior
for s in range(PS1 + 2, PS2 - 1, 4):
    for t in (PT1 + 3, PT2 - 3):
        put(s, t, 4, "glowstone")
pbox(108, 118, -136, -136, 0, 0, "dark_oak_planks")          # reception desk
pbox(108, 118, -136, -136, 1, 1, "smooth_quartz_slab[type=bottom]")
for s in (110, 113, 116):
    x, z = P(s, -137); b.chair(x, 0, z, "east", "dark_oak_stairs")
put(113, -136, 1, "bell[attachment=floor,facing=east]")
x, z = P(105, -132); b.sofa(x, 0, z, "north", 3, "quartz_stairs")
x, z = P(121, -134); b.sofa(x, 0, z, "south", 3, "quartz_stairs")
rect(108, 118, -133, -131, 0, "red_carpet")
for s in (105, 121):
    put(s, -130, 0, "potted_bamboo"); put(s, -140, 0, "potted_fern")
# restaurant tables at the south end
for (s, t) in ((105, -139), (105, -137), (107, -139)):
    x, z = P(s, t); b.table(x, 0, z)
x, z = P(119, -140); b.sign(x, 2, z, ["Lobby Bar"], facing="east")

# tower: 15 guest floors above the podium, walk y = 6 + 3f
TS1, TS2, TT1, TT2 = 104, 122, -141, -131
FLOORS = 15
for f in range(FLOORS):
    w = 6 + 3 * f
    rect(TS1, TS2, TT1, TT2, w - 1, "white_concrete")
    # facade: white piers every 3 blocks, glass between, spandrel band at floor line
    for s in range(TS1, TS2 + 1):
        for t in (TT1, TT2):
            pier = (s - TS1) % 3 == 0
            for yy in (w, w + 1):
                put(s, t, yy, "white_concrete" if pier else "light_gray_stained_glass")
    for t in range(TT1, TT2 + 1):
        for s in (TS1, TS2):
            pier = (t - TT1) % 3 == 0
            for yy in (w, w + 1):
                put(s, t, yy, "white_concrete" if pier else "light_gray_stained_glass")
    # corridor walls, room partitions, beds, lights
    for s in range(TS1 + 1, TS2):
        put(s, -137, w, "white_terracotta"); put(s, -137, w + 1, "white_terracotta")
        put(s, -135, w, "white_terracotta"); put(s, -135, w + 1, "white_terracotta")
    for s in range(TS1 + 4, TS2, 4):
        for t in (-140, -139, -138, -134, -133, -132):
            put(s, t, w, "white_terracotta"); put(s, t, w + 1, "white_terracotta")
    for j, s in enumerate(range(TS1 + 1, TS2 - 2, 4)):
        put(s + 2, -137, w, "air"); put(s + 2, -137, w + 1, "air")     # doorways
        put(s + 2, -135, w, "air"); put(s + 2, -135, w + 1, "air")
        x, z = P(s + 1, -139); b.bed(x, w, z, "west", rng.choice(["white", "light_gray", "red"]))
        x, z = P(s + 1, -133); b.bed(x, w, z, "east", rng.choice(["white", "light_gray", "red"]))
        # lit windows: random rooms have their lights on
        if f < FLOORS - 1:
            if rng.random() < 0.65:
                put(s + 2, -139, w + 2, "glowstone")
            if rng.random() < 0.65:
                put(s + 2, -133, w + 2, "glowstone")
            put(s, -136, w + 2, "sea_lantern")
# roof + crown
roof = 6 + 3 * FLOORS - 1
rect(TS1, TS2, TT1, TT2, roof, "white_concrete")
pbox(TS1, TS2, TT1, TT2, roof + 1, roof + 2, "white_concrete", hollow=True)
pbox(TS1 + 1, TS2 - 1, TT1 + 1, TT2 - 1, roof + 1, roof + 2, "air")
pbox(TS1, TS2, TT1, TT2, roof + 2, roof + 2, "red_concrete", hollow=True)
pbox(TS1 + 1, TS2 - 1, TT1 + 1, TT2 - 1, roof + 2, roof + 2, "air")
pbox(110, 116, -138, -134, roof + 1, roof + 4, "light_gray_concrete")   # mechanical penthouse
for (s, t) in ((TS1, TT1), (TS1, TT2), (TS2, TT1), (TS2, TT2)):
    put(s, t, roof + 3, "lantern[hanging=false]")
# ladder/stair core on the corridor north end: ladder through every slab
for yy in range(0, roof + 1):
    put(121, -136, yy, "ladder[facing=south]")
# vertical red MARRIOTT blade sign on the east face (letters read top-down)
word = "MARRIOTT"
pbox(111, 117, -130, -130, 6, 6 + 6 * len(word), "white_concrete")
for i, ch in enumerate(word):
    y0 = 6 + 6 * (len(word) - 1 - i) + 1
    glyph(ch, 112, -129, y0, "red_concrete")

# ---------------------------------------------------------------- Rental car center
RS1, RS2, RT1, RT2 = 31, 50, -142, -128
pbox(RS1, RS2, -142, -123, 0, 16, "air")
rect(RS1, RS2, -142, -123, -1, "gray_concrete")
pbox(RS1, RS2, RT1, RT2, 0, 10, "light_gray_concrete", hollow=True)
rect(RS1 + 1, RS2 - 1, RT1 + 1, RT2 - 1, 5, "light_gray_concrete")     # 2nd level (ready cars)
rect(RS1 + 1, RS2 - 1, RT1 + 1, RT2 - 1, -1, "polished_andesite")
# glass east facade with a canopy and the customer hall at the east side
for s in range(RS1 + 1, RS2):
    pbox(s, s, RT2, RT2, 1, 3, "light_blue_stained_glass")
    pbox(s, s, RT2, RT2, 6, 8, "light_blue_stained_glass")
    if (s - RS1) % 3:
        pbox(s, s, RT1, RT1, 6, 8, "air")            # open-sided upper deck to the west
for t in range(RT1 + 1, RT2):
    pbox(RS1, RS1, t, t, 1, 3, "light_blue_stained_glass")
pbox(39, 42, RT2, RT2, 0, 2, "air")                   # entrance
pbox(37, 44, -127, -124, 4, 4, "white_concrete")      # canopy
for s in (37, 44):
    pbox(s, s, -124, -124, 0, 3, "smooth_quartz")
pbox(RS1, RS2, RT1, RT2, 10, 10, "light_gray_concrete")
pbox(RS1, RS2, RT1, RT2, 11, 11, "yellow_concrete", hollow=True)       # band
# customer hall: counters for the rental brands (east part, t -133..-129)
pbox(RS1 + 2, RS2 - 2, -133, -133, 0, 0, "smooth_stone")
pbox(RS1 + 2, RS2 - 2, -133, -133, 1, 1, "smooth_stone_slab[type=bottom]")
brands = [("Hertz", "yellow"), ("Avis", "red"), ("Enterprise", "green"), ("National", "lime"),
          ("Budget", "orange"), ("Alamo", "blue")]
for i, (nm, col) in enumerate(brands):
    s = RS1 + 3 + 3 * i
    put(s, -134, 0, "air")
    x, z = P(s, -134); b.chair(x, 0, z, "east", "dark_oak_stairs")
    pbox(s - 1, s + 1, -134, -134, 3, 3, f"{col}_concrete")
    x, z = P(s, -133); b.sign(x, 3, z, [nm, "Rental"], facing="east")
for s in range(RS1 + 2, RS2 - 1, 4):
    put(s, -130, 4, "sea_lantern"); put(s, -137, 4, "sea_lantern"); put(s, -137, 9, "sea_lantern")
    put(s, -130, 9, "sea_lantern")
# return lanes with cars on the ground (west part) and ready-car deck above
for s in range(RS1 + 2, RS2 - 1, 2):
    for t in (-141, -138):
        if rng.random() < 0.8:
            car(s, t, 0)
    for t in (-141, -137, -133):
        if rng.random() < 0.8:
            car(s, t, 6)
# ladder up to the ready-car deck
for yy in range(0, 6):
    put(RS2 - 1, -131, yy, "ladder[facing=south]")
# pylon sign out front
pbox(46, 48, -125, -125, 0, 8, "white_concrete")
pbox(46, 48, -124, -124, 5, 8, "yellow_concrete")
x, z = P(47, -123)
b.sign(x, 7, z, ["RENTAL CAR", "RETURN", "& PICK-UP"], facing="east")
# ready-car lot on the east apron and lamp posts
for s in range(33, 37):
    car(s, -126, 0)
for s in (33, 49):
    lamp_post(s, -124, 0, 4)
