exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
# South cargo area, build 2: apron markings, fuel farm, cargo office, GSE, lighting, freighters.
T2 = -27

# ================= apron markings (ground y=-1) =================
FX_S, FX_T = 31, -45      # FedEx stand (big freighter, nose west toward the hub)
UP_S, UP_T = 6, -50       # UPS stand
for s0, nose in ((FX_S, FX_T - 16), (UP_S, UP_T - 12)):
    for t in range(nose, -32):
        put(s0, t, -1, "yellow_concrete")                    # lead-in line from the taxiway
    rect(s0 - 3, s0 + 3, nose - 1, nose - 1, -1, "yellow_concrete")   # stop bar
    rect(s0 - 1, s0 + 1, nose - 2, nose - 2, -1, "white_concrete")
# equipment restraint line (red) + service road (white dashes) between docks and stands
for s in range(-3, 47):
    put(s, -63, -1, "red_concrete")
    if s % 4 < 2:
        put(s, -69, -1, "white_concrete")
# taxi line to the taxiway at the zone's NE corner
for t in range(-33, T2 + 1):
    put(43, t, -1, "yellow_concrete")
for s in range(6, 44):
    put(s, -33, -1, "yellow_concrete")

# ================= fuel farm (Jet-A tank farm, south-west corner) =================
rect(-14, -4, -99, -58, -1, "gravel")
b.walls(-99, 0, 4, -58, 0, 14, "stone_bricks")          # containment bund (plan s -14..-4)
for t in range(-90, -60, 10):
    put(-4, t, 0, "air")                                 # access gaps
TANKS = (-93, -83, -73, -63)
for tc in TANKS:
    x, z = P(-10, tc)
    b.cylinder(x, 0, z, 4, 10, "white_concrete")
    b.cylinder(x, 6, z, 4, 1, "light_gray_concrete")     # band
    b.cylinder(x, 10, z, 4, 1, "light_gray_concrete")    # roof
    b.cylinder(x, 11, z, 2, 1, "smooth_quartz_slab[type=bottom]")
    b.cylinder(x, 11, z, 4, 1, "iron_bars", hollow=True)  # roof railing
    b.ladder(tc - 5, 0, 10, 11, "west")                   # ladder on the west face
    put(-10, tc - 4, 11, "air")                           # railing gap at the ladder head
    b.sign(tc + 2, 4, 5, ["JET A", "FLAMMABLE", "NO SMOKING"], facing="north")
# header pipe along the north side of the tanks, risers, to a pump house
for t in range(-98, -55):
    put(-5, t, 1, "iron_block")
for t in TANKS:
    put(-5, t, 2, "iron_block"); put(-5, t, 3, "iron_bars")
# pump house
pbox(-13, -8, -57, -53, 0, 3, "light_gray_concrete", hollow=True)
pbox(-12, -9, -56, -54, 0, 2, "air")
rect(-13, -8, -57, -53, 4, "smooth_stone_slab[type=bottom]")
b.door(-55, 0, 8, "south", "iron_door")
put(-12, -56, 0, "blast_furnace[facing=east]"); put(-11, -56, 0, "smoker[facing=east]")
put(-9, -54, 0, "cauldron")
b.lamp(-55, 2, 11, "lantern", hanging=True)
for t in range(-57, -52):
    put(-7, t, 1, "iron_block")
b.sign(-56, 2, 7, ["FUEL FARM", "PUMP HOUSE"], facing="north")
for s in range(-7, -3):
    put(s, -55, 0, "iron_block") if s != -7 else None

# ================= cargo operations office (2 storeys, glass) =================
OS1, OS2, OT1, OT2 = -14, -7, -52, -32
rect(OS1, OS2, OT1, OT2, -1, "polished_diorite")
pbox(OS1, OS2, OT1, OT2, 0, 8, "white_concrete", hollow=True)
pbox(OS1 + 1, OS2 - 1, OT1 + 1, OT2 - 1, 0, 7, "air")
for y in (1, 2, 5, 6):
    b.walls(OT1, y, -OS2, OT2, y, -OS1, "light_blue_stained_glass_pane")
for t in range(OT1, OT2 + 1, 5):
    for s in (OS1, OS2):
        pbox(s, s, t, t, 0, 8, "white_concrete")
for s in range(OS1, OS2 + 1, 4):
    for t in (OT1, OT2):
        pbox(s, s, t, t, 0, 8, "white_concrete")
rect(OS1 + 1, OS2 - 1, OT1 + 1, OT2 - 1, 4, "smooth_quartz")          # 2nd floor
rect(OS1 + 1, OS1 + 1, OT2 - 5, OT2 - 2, 4, "air")                       # stair well
b.stairs_run(OT2 - 6, 0, -(OS1 + 1), "east", 5, "quartz_stairs")
b.double_door(-43, 0, -OS2, "south", "iron_door")
put(OS2 + 1, -44, 0, "polished_blackstone_button[face=floor]")
b.sign(-43, 3, -(OS2 + 1), ["CARGO", "OPERATIONS"], facing="north")
b.sign(-42, 3, -(OS2 + 1), ["EWR SOUTH", "CARGO"], facing="north")
# ground floor: counter, waiting chairs, desks
for t in range(-48, -40):
    put(OS2 - 3, t, 0, "white_concrete"); put(OS2 - 3, t, 1, "smooth_quartz_slab[type=bottom]")
for t in range(-50, -46):
    b.chair(t, 0, -(OS2 - 1), "south")
b.plant(-51, 0, -(OS2 - 1), "potted_bamboo"); b.plant(-33, 0, -(OS2 - 1), "potted_fern")
for t in (-49, -46, -43, -40):
    put(OS1 + 2, t, 0, "spruce_planks"); b.chair(t, 0, -(OS1 + 3), "south")
    put(OS1 + 2, t, 1, "black_carpet")
b.lamp(-36, 3, -(OS1 + 4), "lantern", hanging=True)
b.lamp(-46, 3, -(OS1 + 4), "lantern", hanging=True)
# upper floor: ramp-control room with desks facing the apron (north)
for t in range(-50, -38):
    put(OS2 - 1, t, 5, "dark_oak_slab[type=top]")
for t in range(-50, -38, 2):
    b.chair(t, 5, -(OS2 - 2), "north")
b.long_table(-50, -(OS1 + 4), -42, -(OS1 + 4), 5, "spruce_slab")
for t in range(-50, -42, 2):
    b.chair(t, 5, -(OS1 + 3), "north")
for t in range(-50, -32, 5):
    put(OS1 + 4, t, 8, "sea_lantern")
# roof: antenna + rim
b.walls(OT1, 9, -OS2, OT2, 9, -OS1, "white_concrete")
pbox(-10, -10, -36, -36, 9, 14, "iron_bars"); put(-10, -36, 15, "redstone_block")


# ================= high-mast apron lighting =================
def mast(s, t, h=14):
    pbox(s, s, t, t, 0, h, "andesite_wall")
    pbox(s, s, t - 1, t + 1, h + 1, h + 1, "smooth_stone_slab[type=bottom]")
    for dt in (-1, 0, 1):
        put(s, t + dt, h, "sea_lantern" if dt else "andesite")


for s, t in ((-2, -66), (18, -66), (45, -66), (17, -29), (-3, -29), (45, -29), (18, -52)):
    mast(s, t)

# ================= ground support equipment =================
FX_ULD = {"purple_shulker_box": 2, "orange_shulker_box": 2, "white_shulker_box": 2, "barrel[facing=up]": 1}
UP_ULD = {"brown_shulker_box": 3, "yellow_shulker_box": 1, "barrel[facing=up]": 1, "chest[facing=east]": 1}


def uld_row(s1, s2, t, mix, step=2):
    for s in range(s1, s2 + 1, step):
        put(s, t, 0, "smooth_stone_slab[type=top]")      # dolly deck
        put(s, t, 1, mix)


def tug(s, t, color, heading="+s"):
    """baggage tug 2 wide x 3 long along s; front at the +heading end"""
    d = 1 if heading == "+s" else -1
    for i in range(3):
        for dt in (0, 1):
            put(s + d * i, t + dt, 0, color)
    for dt in (0, 1):
        put(s, t + dt, 0, "black_concrete"); put(s + 2 * d, t + dt, 0, "black_concrete")
    put(s, t, 1, "dark_oak_stairs[facing=%s]" % ("south" if d == 1 else "north"))
    put(s + 2 * d, t + 1, 1, "black_stained_glass_pane")


def cart_train(s, t, n, mix, color="white_concrete", heading="+s"):
    """tug at (s,t) pulling n carts behind it"""
    d = 1 if heading == "+s" else -1
    tug(s, t, color, heading)
    ss = s - d
    for k in range(n):
        put(ss, t, 0, "iron_chain[axis=z]")
        ss -= d
        for i in range(2):
            for dt in (0, 1):
                put(ss - d * i, t + dt, 0, "smooth_stone_slab[type=top]")
                put(ss - d * i, t + dt, 1, mix)
        ss -= 2 * d


# FedEx ULD staging between the hub's docks and the freighter
for t in (-74, -72):
    uld_row(21, 44, t, FX_ULD)
cart_train(29, -66, 3, FX_ULD, "purple_concrete")
cart_train(34, -66, 3, FX_ULD, "white_concrete", heading="-s")
# UPS ULD staging
for t in (-77, -75):
    uld_row(-1, 14, t, UP_ULD)
cart_train(10, -67, 2, UP_ULD, "brown_concrete")
cart_train(14, -71, 2, UP_ULD, "yellow_concrete", heading="-s")


def k_loader(s1, t1, deck_y, color="yellow_concrete"):
    """main-deck loader 3x4 with scissor lift up to deck_y"""
    rect(s1, s1 + 2, t1, t1 + 3, 0, color)
    for y in range(1, deck_y):
        put(s1 + 1, t1 + 1, y, "scaffolding"); put(s1 + 1, t1 + 2, y, "scaffolding")
    rect(s1, s1 + 2, t1, t1 + 3, deck_y, "smooth_stone_slab[type=bottom]")
    put(s1 + 2, t1, deck_y + 1, "iron_bars"); put(s1, t1, deck_y + 1, "iron_bars")


# loaders at the freighters' forward main-deck doors
k_loader(FX_S + 2, FX_T - 12, 2)
put(FX_S + 3, FX_T - 11, 3, "purple_shulker_box")
k_loader(UP_S + 2, UP_T - 9, 2)
put(UP_S + 3, UP_T - 8, 3, "brown_shulker_box")
# fuel truck beside the UPS freighter's wing
for s in range(-3, 3):
    for t in (-56, -55):
        put(s, t, 0, "black_concrete" if s in (-3, 2) else "white_concrete")
        put(s, t, 1, "white_concrete" if s > -2 else "light_blue_stained_glass")
b.sign(-57, 1, 0, ["JET A"], facing="west")
# ground power unit + safety cones at the noses
rect(FX_S - 4, FX_S - 3, FX_T - 18, FX_T - 17, 0, "yellow_concrete")
for s0, t0 in ((FX_S, FX_T - 14), (UP_S, UP_T - 10)):
    put(s0 + 3, t0, 0, "orange_carpet"); put(s0 - 3, t0, 0, "orange_carpet")

# ================= parked freighters =================
plane(at(FX_S, FX_T, 0, rot=3), "fedex", big=True)
plane(at(UP_S, UP_T, 0, rot=3), "ups")
