# Newark Liberty International (EWR), laid out from the FAA airport diagram at 1 block = 10 m.
# The whole airport is turned 25 degrees so runways 4/22 run exactly north-south in-game.
# Local frame: x = t (blocks east of the 04L centreline), z = -s (s = blocks north of the 04L threshold),
# y = 0 at ground level (ground blocks at y = -1). Origin used: (60, 64, 310), on reclaimed land in the bay.
# Set PHASE before running: "ground" (land, runways, taxiways, roads), "terminals", "hangars".

PHASE = globals().get("PHASE", "ground")

S0, S1, T0, T1 = -14, 352, -142, 68                  # site extents (s along runways, t across)
RWY_W = 4                                            # half width (9 blocks; real 46 m, widened for planes)
D11 = (0.935, 0.355)                                 # runway 11->29 direction in (t, s), 69.2 deg off 4/22
P11 = (0.0, 294.0)                                   # where 11/29 crosses 04L (t, s)
ASPHALT, MARK, TAXI, TAXI_LINE, APRON, GRASS = ("gray_concrete", "white_concrete", "polished_andesite",
                                                 "yellow_concrete", "smooth_stone", "grass_block")


def P(s, t):            # plan coords -> builder coords (x, z)
    return t, -s


def put(s, t, y, block):
    x, z = P(s, t)
    b.set(x, y, z, block)


def rect(s1, s2, t1, t2, y, block):
    b.box(t1, y, -s2, t2, y, -s1, block)


def rwy11(s, t):        # (along, across) for runway 11/29
    dt, ds = t - P11[0], s - P11[1]
    return dt * D11[0] + ds * D11[1], -dt * D11[1] + ds * D11[0]


FONT = {"0": ["###", "#.#", "#.#", "#.#", "###"], "1": [".#.", "##.", ".#.", ".#.", "###"],
        "2": ["###", "..#", "###", "#..", "###"], "4": ["#.#", "#.#", "###", "..#", "..#"],
        "9": ["###", "#.#", "###", "..#", "###"], "L": ["#..", "#..", "#..", "#..", "###"],
        "R": ["##.", "#.#", "##.", "#.#", "#.#"]}


def runway_text(s_start, t_c, lines, north):
    """Paint runway designators upright for a pilot landing toward `north` (True) or south.
    lines are top (far from threshold) to bottom (nearest)."""
    sgn = 1 if north else -1
    row = 0
    for line in reversed(lines):                     # nearest line first
        width = len(line) * 4 - 1
        for ci, ch in enumerate(line):
            g = FONT[ch]
            for r in range(5):
                for c in range(3):
                    if g[r][c] == "#":
                        s = s_start + sgn * (row + (4 - r))
                        t = t_c + sgn * (ci * 4 + c - width // 2)
                        put(s, t, -1, MARK)
        row += 7


def parallel_runway(t_c, s_a, s_b, low, high):
    rect(s_a, s_b, t_c - RWY_W, t_c + RWY_W, -1, ASPHALT)
    for s in range(s_a + 14, s_b - 13):
        if s % 10 < 5:
            put(s, t_c, -1, MARK)                     # centreline dashes
    for s_end, sgn in ((s_a, 1), (s_b, -1)):
        for k in range(2, 8):
            for dt in (-3, -1, 1, 3):
                put(s_end + sgn * k, t_c + dt, -1, MARK)          # threshold "piano keys"
        for k in range(30, 36):
            for dt in (-3, -2, 2, 3):
                put(s_end + sgn * k, t_c + dt, -1, MARK)          # aiming point
        for k in range(1, 12):
            if k % 2:
                put(s_end - sgn * k, t_c, -1, "sea_lantern")       # approach lights
        for dt in range(-3, 4):
            put(s_end - sgn * 6, t_c + dt, -1, "sea_lantern")
    runway_text(s_a + 10, t_c, low, True)
    runway_text(s_b - 10, t_c, high, False)
    for s in range(s_a, s_b + 1, 6):
        put(s, t_c - RWY_W - 1, -1, "sea_lantern"); put(s, t_c + RWY_W + 1, -1, "sea_lantern")


if PHASE == "ground":
    # reclaimed land: solid fill from y-6, grass top, everything above cleared
    b.box(T0, -6, -S1, T1, -2, -S0, {"stone": 3, "dirt": 1})
    rect(S0, S1, T0, T1, -1, GRASS)
    b.box(T0, 0, -S1, T1, 16, -S0, "air")
    # sea wall along the bay side
    b.box(T1, -6, -S1, T1 + 1, 0, -S0, "stone_bricks")

    # taxiways (5 wide) with yellow centrelines
    def taxi_s(t_c, s_a, s_b):
        rect(s_a, s_b, t_c - 2, t_c + 2, -1, TAXI)
        rect(s_a, s_b, t_c, t_c, -1, TAXI_LINE)

    def taxi_t(s_c, t_a, t_b):
        rect(s_c - 2, s_c + 2, t_a, t_b, -1, TAXI)
        rect(s_c, s_c, t_a, t_b, -1, TAXI_LINE)

    taxi_s(-14, 2, 300)            # parallel taxiway west of 04L
    taxi_s(-23, 40, 290)           # outer parallel (terminal side)
    taxi_s(14, 20, 322)            # between the parallels
    for s in range(10, 300, 36):
        taxi_t(s, -23, -6)
        if 25 < s < 325:
            taxi_t(s + 18, 6, 23)
    # terminal aprons
    rect(50, 215, -72, -26, -1, APRON)
    # north (hangar / cargo) apron, above runway 11/29
    rect(300, 348, -100, -12, -1, APRON)
    taxi_s(-40, 262, 300)

    parallel_runway(0, 0, 335, ["4", "L"], ["2", "2", "R"])
    parallel_runway(29, 25, 330, ["4", "R"], ["2", "2", "L"])

    # crosswind runway 11/29 (diagonal) painted last so it crosses the parallels
    for t in range(T0, T1 + 1):
        for s in range(S0, S1 + 1):
            a, p = rwy11(s, t)
            if -150 <= a <= 57:
                if abs(p) <= RWY_W:
                    on_center = abs(p) < 0.55 and int(a) % 10 < 5 and -136 < a < 43
                    keys = (a < -142 or a > 49) and round(p) in (-3, -1, 1, 3)
                    if not (abs(t) <= RWY_W or abs(t - 29) <= RWY_W) or on_center:
                        put(s, t, -1, MARK if (on_center or keys) else ASPHALT)
                elif RWY_W + 0.5 <= abs(p) <= RWY_W + 1.5 and int(a) % 6 == 0:
                    put(s, t, -1, "sea_lantern")

    # NJ Turnpike along the bay side
    rect(S0, S1, 50, 59, -1, "gray_concrete")
    rect(S0, S1, 54, 55, -1, "yellow_concrete")
    for s in range(S0, S1, 8):
        rect(s, s + 3, 52, 52, -1, MARK); rect(s, s + 3, 57, 57, -1, MARK)
    for s in range(S0, S1, 20):
        b.lamp(*P(s, 60)[:1], 0, P(s, 60)[1], post="iron_bars") if False else None
        x, z = P(s, 60); b.set(x, 0, z, "iron_bars"); b.set(x, 1, z, "iron_bars"); b.set(x, 2, z, "lantern")
    # terminal loop road + AirTrain
    rect(30, 235, -122, -116, -1, "gray_concrete")
    rect(30, 235, -119, -119, -1, "yellow_concrete")
    for s in range(40, 226):
        for dt in (-104, -103):
            put(s, dt, 8, "smooth_quartz")
        if s % 10 == 0:
            for y in range(0, 8):
                put(s, -104, y, "light_gray_concrete")
    for s_st in (72, 151, 184):                        # AirTrain stations at A, B, C
        rect(s_st - 5, s_st + 5, -107, -100, 8, "smooth_quartz")
        rect(s_st - 5, s_st + 5, -107, -107, 9, "glass_pane")
        rect(s_st - 5, s_st + 5, -100, -100, 9, "glass_pane")
        rect(s_st - 5, s_st + 5, -107, -100, 12, "smooth_quartz_slab[type=bottom]")
        b.stairs_run(*P(s_st - 6, -103)[:1], 0, P(s_st - 6, -103)[1], "north", 8, "quartz_stairs", width=2,
                     support="smooth_quartz")
    # airport sign at the entrance
    b.sign(*P(20, -119)[:1], 0, P(20, -119)[1], ["NEWARK LIBERTY", "INTERNATIONAL", "AIRPORT", "EWR"],
           facing="south", wall=False)
    print("ground phase planned")
