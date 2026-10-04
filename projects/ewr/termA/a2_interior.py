exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
# Terminal A headhouse interiors + roof step closing.
S1, S2, T1, T2 = 52, 102, -95, -73


def R(s, t):
    return 20 + round(2.2 * math.sin(2 * math.pi * (s - 52) / 26)) + round((-73 - t) / 10)


# ---- close the vertical slits where the wavy roof steps ----
for s in range(S1 - 1, S2 + 2):
    for t in range(-99, T2 + 2):
        r = R(s, t)
        m = min(R(s + ds, t + dt) for ds, dt in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if t == -96 and 69 <= s <= 75:
            continue
        sky = (-92 <= t <= -76) and (s - 52) % 7 == 3 and S1 < s < S2
        for y in range(m, r):
            put(s, t, y, "glass" if sky else "white_concrete")


def sgn(s, t, y, lines, facing, wall=True):
    x, z = P(s, t)
    b.sign(x, y, z, lines, facing=facing, wall=wall)


# =================== LEVEL 2 (walk y=9): departures ===================
AIR = [("blue_concrete", "JetBlue"), ("red_concrete", "American"), ("red_concrete", "Delta"),
       ("cyan_concrete", "Alaska"), ("yellow_concrete", "Spirit"), ("blue_concrete", "JetBlue")]
for i, c in enumerate((55, 61, 77, 84, 91, 97)):
    col, name = AIR[i]
    for t in range(-92, -86):
        put(c, t, 9, "smooth_quartz"); put(c + 3, t, 9, "smooth_quartz")       # counters
        put(c + 1, t, 9, "gray_carpet")                                         # bag belt
    for t in (-92, -87):
        put(c, t, 10, "lantern"); put(c + 3, t, 10, "lantern")
    for s in (c + 1, c + 2):
        for t in (-90, -89):
            for y in range(9, 14):
                put(s, t, y, col if y < 13 else "white_concrete")
            put(s, t, 14, "sea_lantern")
    for t in (-90, -89):
        sgn(c, t, 12, [name, "Check-in", "Desk %d" % (i + 1)], "south")
        sgn(c + 3, t, 12, [name, "Check-in", "Desk %d" % (i + 1)], "north")
    for s in (c + 1, c + 2):   # self-service kiosks
        put(s, -93, 9, "light_gray_concrete"); put(s, -93, 10, "black_stained_glass_pane")
put(68, -93, 9, "smooth_quartz"); put(68, -93, 10, "smooth_quartz")
sgn(69, -93, 10, ["Welcome to", "Newark Liberty", "Terminal A"], "north")

# ---- security checkpoint: partition at t=-84, 10 lanes s 62..91 ----
for s in range(S1 + 1, S2):
    for y in range(9, 13):
        put(s, -84, y, "white_stained_glass_pane")
    put(s, -84, 13, "white_concrete")
for k, L in enumerate(range(62, 90, 3)):
    a, bb, c = L, L + 1, L + 2
    for t in range(-85, -78):
        put(a, t, 9, "polished_andesite_slab[type=top]")          # bag belt
        put(c, t, 9, "white_stained_glass_pane")                  # lane divider
    for y in (9, 10):
        put(bb, -84, y, "air")                                    # walk-through opening
    for t in (-83, -82):                                          # x-ray machine
        put(a, t, 9, "light_gray_concrete"); put(a, t, 10, "gray_concrete")
    put(a, -81, 10, "white_concrete"); put(a, -81, 11, "white_concrete")   # body scanner arch
    for y in (9, 10, 11):
        put(c, -81, y, "white_concrete")
    put(bb, -81, 11, "lime_concrete" if k % 2 else "white_concrete")
    put(c, -86, 9, "polished_andesite")                                   # TSA podium
    put(c, -86, 10, "lantern")
for s, lines in ((66, ["TSA", "Security", "Checkpoint"]), (75, ["Gates A1-A33", "TSA PreCheck", "this way ->"]),
                 (85, ["TSA", "Security", "Checkpoint"])):
    sgn(s, -85, 13, lines, "west")

# ---- food halls (airside) south s53..60 and north s92..101, t -83..-74 ----
FOOD = [("Jersey Pizza", "red_wool"), ("Taqueria", "orange_wool"), ("Burger Bar", "yellow_wool"),
        ("Ramen House", "purple_wool"), ("NJ Bagels", "lime_wool"), ("Coffee", "brown_wool")]
stall_t = ((-83, -81), (-79, -77), (-76, -74))
for side in (0, 1):
    back, counter, signrow, face = (53, 55, 56, "north") if side == 0 else (101, 99, 98, "south")
    for j, (t1, t2) in enumerate(stall_t):
        name, wool = FOOD[side * 3 + j]
        for t in range(t1, t2 + 1):
            put(back, t, 9, ["smoker[facing=%s]" % face, "barrel[facing=up]", "furnace[facing=%s]" % face][(t - t1) % 3])
            put(back, t, 10, "white_concrete")
            put(counter, t, 9, "smooth_quartz")
            for s in range(min(back, counter), max(back, counter) + 1):
                put(s, t, 12, wool)
        put(counter, t1, 10, "lantern")
        sgn(signrow, (t1 + t2) // 2 if t2 - t1 == 2 else t1, 12, [name, "Local Food Hall"], face)
    rows = (58, 60) if side == 0 else (94, 96)
    for s in rows:
        for tt in (-82, -78, -75):
            x, z = P(s, tt)
            b.table(x, 9, z, "birch_fence", "white_carpet")
            b.chair(x - 1, 9, z, "east", "birch_stairs"); b.chair(x + 1, 9, z, "west", "birch_stairs")
    for tt in (-83, -74):
        x, z = P(rows[0] + 1, tt)
        b.lamp(x, 9, z, "lantern", post="iron_bars")

# ---- airside concourse strip (t -78..-74): newsstand + way to the pier ----
for s in range(62, 70):
    put(s, -74, 9, "bookshelf"); put(s, -74, 10, "bookshelf")
for s in (64, 65, 66):
    put(s, -76, 9, "smooth_quartz")
put(65, -76, 10, "lantern")
put(70, -74, 9, "white_concrete"); put(70, -74, 10, "white_concrete")
sgn(70, -75, 10, ["Newsstand", "Books & Snacks"], "west")
for s in (63, 68):
    x, z = P(s, -77); b.plant(x, 9, z, "potted_bamboo")
put(76, -73, 14, "white_concrete")
sgn(76, -74, 14, ["Gates A1-A33", "->"], "west")
put(91, -78, 9, "smooth_quartz"); put(91, -78, 10, "smooth_quartz")
sgn(90, -78, 10, ["Exit to", "Baggage Claim", "(stairs down)"], "south")

# ---- public art: suspended glass cloud over the departures hall ----
cols = ["blue_stained_glass", "cyan_stained_glass", "light_blue_stained_glass", "magenta_stained_glass",
        "yellow_stained_glass", "orange_stained_glass"]
for s in range(66, 79):
    for t in range(-93, -86):
        for y in range(15, 19):
            d = ((s - 72) / 6.5) ** 2 + ((t + 89.5) / 3.6) ** 2 + ((y - 16.5) / 2) ** 2
            if d < 1 and rng.random() < 0.3:
                put(s, t, y, rng.choice(cols))
murals = ["blue_glazed_terracotta", "orange_glazed_terracotta", "cyan_glazed_terracotta", "yellow_glazed_terracotta"]
for t in range(-94, -73):
    for y in (18, 19):
        put(102, t, y, murals[(t + y) % 4])

# =================== LEVEL 1 (walk y=0): arrivals / baggage claim ===================
for n, c in enumerate((57, 74, 84, 93)):
    for s in range(c, c + 4):
        for t in range(-92, -79):
            edge = s in (c, c + 3) or t in (-92, -80)
            put(s, t, 0, "polished_andesite" if edge else "light_gray_concrete")
            put(s, t, 1, "black_carpet" if edge else "light_gray_concrete")
            if edge and rng.random() < 0.18:
                put(s, t, 1, rng.choice(["barrel[facing=up]", "red_wool", "blue_wool", "black_wool", "green_wool"]))
    for s in (c + 1, c + 2):
        put(s, -91, 2, "white_concrete"); put(s, -91, 3, "white_concrete")
    names = ["JetBlue", "American/Delta", "Alaska/Spirit", "JetBlue"][n]
    sgn(c, -91, 3, ["Baggage Claim", "Carousel A%d" % (n + 1), names], "south")
    sgn(c + 3, -91, 3, ["Baggage Claim", "Carousel A%d" % (n + 1), names], "north")
# rental-car / ground transport counters along the south wall
for t in range(-92, -79):
    put(54, t, 0, "smooth_quartz" if t % 4 else "air")
    put(52, t, 3, ["red_wool", "yellow_wool", "green_wool", "blue_wool"][(t // 4) % 4])
sgn(55, -86, 0, ["Rental Cars", "Ground Transport"], "north", wall=False)
# information desk on the main axis
for s in range(70, 73):
    for t in range(-80, -77):
        if not (s == 71 and t == -79):
            put(s, t, 0, "smooth_quartz")
put(70, -79, 1, "lantern"); put(72, -79, 1, "lantern")
sgn(73, -79, 0, ["Information", "Terminal A"], "north", wall=False)
# benches in the meeting area
for s in (65, 67):
    for t in range(-78, -74):
        x, z = P(s, t)
        b.chair(x, 0, z, "north" if s == 80 else "south", "smooth_quartz_stairs")
sgn(81, -77, 0, ["Gate exit", "from concourse", "stairs ^"], "south", wall=False)
sgn(63, -84, 0, ["Departures", "Check-in &", "Security ^"], "south", wall=False)
for t in range(-94, -73):
    for y in (5, 6):
        put(102, t, y, murals[(t * 2 + y) % 4])
for s, t in ((62, -94), (82, -94), (90, -94), (100, -76), (100, -93)):
    x, z = P(s, t)
    b.plant(x, 0, z, "potted_flowering_azalea_bush")
