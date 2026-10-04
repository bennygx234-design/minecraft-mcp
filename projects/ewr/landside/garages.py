exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\landside\common.py").read())

T1, T2 = -142, -129          # garage footprint (west edge .. east wall)
RAMP = (-141, -139)          # ramp lane
ROWS = ((-137, -136), (-131, -130))   # parked-car rows (cars run along t)


def garage(s1, s2, label, levels, accent, bridges=()):
    top = 4 * levels
    pbox(s1, s2, T1, T2, 0, top + 3, "air")
    rect(s1, s2, T1, T2, -1, "gray_concrete")
    # painted bays on ground
    for k in range(1, levels + 1):
        rect(s1, s2, T1, T2, 4 * k - 1, "light_gray_concrete")
    # ceiling / floor lights flush in each deck
    for k in range(1, levels + 1):
        for s in range(s1 + 3, s2 - 1, 6):
            put(s, -134, 4 * k - 1, "sea_lantern")
    # ramps (alternating ends)
    for k in range(1, levels + 1):
        w = 4 * (k - 1)
        for i in range(8):
            s = s1 + 2 + i if k % 2 else s2 - 2 - i
            y = w + i // 2
            blk = "smooth_stone_slab[type=bottom]" if i % 2 == 0 else "smooth_stone"
            for t in range(RAMP[0], RAMP[1] + 1):
                for yy in range(w, y):
                    put(s, t, yy, "light_gray_concrete")
                put(s, t, y, blk)
                if i < 7:
                    for yy in range(y + 1, 4 * k):
                        put(s, t, yy, "air")
    # parapets on every level (open-sided decks), accent band on the roof
    for k in range(0, levels + 1):
        y = 4 * k
        blk = accent if k == levels else "light_gray_concrete"
        for s in range(s1, s2 + 1):
            put(s, T1, y, blk); put(s, T2, y, blk)
        for t in range(T1, T2 + 1):
            put(s1, t, y, blk); put(s2, t, y, blk)
        if k == levels:
            for s in range(s1, s2 + 1):
                put(s, T1, y + 1, "smooth_quartz_slab[type=bottom]"); put(s, T2, y + 1, "smooth_quartz_slab[type=bottom]")
            for t in range(T1, T2 + 1):
                put(s1, t, y + 1, "smooth_quartz_slab[type=bottom]"); put(s2, t, y + 1, "smooth_quartz_slab[type=bottom]")
    # ground entries / exits on the east side
    mid = (s1 + s2) // 2
    for s in list(range(s1 + 3, s1 + 7)) + list(range(s2 - 6, s2 - 2)):
        put(s, T2, 0, "air")
    for s in (s1 + 2, s1 + 7, s2 - 7, s2 - 2):
        put(s, T2 + 1, 0, "yellow_concrete")
        put(s, T2 + 1, 1, "yellow_concrete")
    # pillars
    ps = list(range(s1, s2 + 1, 6))
    if ps[-1] != s2:
        ps.append(s2)
    for s in ps:
        for t in (T1, T2, -138):
            for k in range(levels):
                for yy in range(4 * k, 4 * k + 3):
                    put(s, t, yy, "stone_bricks" if t != -138 else "gray_concrete")
    # parked cars
    for k in range(0, levels + 1):
        y = 4 * k
        dens = 0.55 if k == levels else 0.78
        for (ta, tb) in ROWS:
            for s in range(s1 + 2, s2 - 1, 2):
                if rng.random() < dens:
                    car(s, ta, y)
        # white bay stripes on the floor between rows is too fine; mark the aisle with arrows
        for s in range(s1 + 4, s2 - 3, 8):
            put(s, -133, y - 1, "white_concrete")
    # roof lamp posts
    for s in range(s1 + 2, s2 - 1, 8):
        lamp_post(s, -134, top)
    for s in (s1 + 1, s2 - 1):
        lamp_post(s, T1 + 1, top); lamp_post(s, T2 - 1, top)
    # stair/elevator core at the north-east corner (glass shaft, ladder inside)
    cs = s2 - 3
    for k in range(levels + 1):
        for s in (cs, cs + 1, cs + 2):
            for t in (-131, -130):
                put(s, t, 4 * k, "air")   # no cars in the core
    pbox(cs, cs + 2, -132, -130, 0, top + 3, "light_blue_stained_glass", hollow=True)
    pbox(cs, cs + 2, -132, -130, top + 4, top + 4, "white_concrete")
    for k in range(levels + 1):
        put(cs + 1, -131, 4 * k - 1, "air") if k > 0 else None
        # doorway out of the core on each level (west side)
        put(cs + 1, -132, 4 * k, "air"); put(cs + 1, -132, 4 * k + 1, "air")
    for yy in range(0, top + 1):
        put(cs + 1, -131, yy, "ladder[facing=south]")      # hangs on the north glass wall (s = cs+2)
    # big level signs on the east face (accent panel + white letters)
    n = len(label)
    ws = 4 * n + 1
    s0 = mid - ws // 2
    pbox(s0, s0 + ws - 1, T2, T2, top + 1, top + 7, accent)
    etext(s0 + 1, T2 + 1, top + 2, label, "white_concrete")
    # pedestrian bridges toward the terminal road, at level 2 (walk y = 8)
    for bs in bridges:
        yb = 8
        pbox(bs - 2, bs + 2, T2 + 1, -123, yb - 1, yb - 1, "smooth_quartz")
        pbox(bs - 2, bs + 2, T2 + 1, -123, yb + 3, yb + 3, "white_concrete")
        for s in (bs - 2, bs + 2):
            pbox(s, s, T2 + 1, -123, yb, yb + 2, "light_blue_stained_glass")
        pbox(bs - 1, bs + 1, -123, -123, yb, yb + 2, "light_blue_stained_glass")   # temporary end glass
        pbox(bs - 1, bs + 1, T2 + 1, -123, yb - 1, yb - 1, "white_concrete")
        put(bs, -125, yb - 1, "sea_lantern")
        for t in (-127, -124):
            pbox(bs, bs, t, t, 0, yb - 2, "smooth_quartz")
        pbox(bs - 1, bs + 1, T2, T2, yb, yb + 1, "air")       # opening in the parapet
        for s in range(bs - 1, bs + 2):
            for t in (-131, -130):
                put(s, t, yb, "air")
        x, z = P(bs, -124)
        b.sign(x, yb + 1, z, ["Terminals", "<- AirTrain", "Garage " + label.replace(" ", "")], facing="west")


# Terminal A garage: the big new 6-level structure opposite Terminal A / AirTrain station A
garage(54, 98, "P-A", 6, "blue_concrete", bridges=(72, 88))
# P4: central garage opposite Terminal B
garage(128, 150, "P4", 4, "green_concrete", bridges=(140,))
# P3 / P1 opposite Terminals B and C
garage(154, 184, "P3", 5, "orange_concrete", bridges=(166,))
garage(188, 236, "P1", 4, "red_concrete", bridges=(196, 220))
