exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
# Terminal A concourse pier (t -72..-28, s 72..80), concourse at walk y=9, ramp level below.
PS1, PS2, PT1, PT2 = 72, 80, -72, -28


def sgn(s, t, y, lines, facing, wall=True):
    x, z = P(s, t)
    b.sign(x, y, z, lines, facing=facing, wall=wall)


# extend the apron paving to the zone edge
rect(48, 49, -72, -27, -1, "smooth_stone")

# ---- shell ----
for t in range(PT1, PT2 + 1):
    for s in range(PS1, PS2 + 1):
        edge_s = s in (PS1, PS2)
        end = t == PT2
        if edge_s or end:
            for y in range(0, 8):
                win = (2 <= y <= 4) and (t % 4 == 1 or (end and s % 2))
                put(s, t, y, "glass" if win else "light_gray_concrete")
            put(s, t, 8, "white_concrete")
            for y in range(9, 14):
                mull = (t % 5 == 0 and not end) or (end and s in (PS1, PS2))
                put(s, t, y, "white_concrete" if mull else "light_blue_stained_glass_pane")
        else:
            for y in range(0, 8):
                put(s, t, y, "air")
            lit = (t % 6 == 0) and s in (74, 78)
            put(s, t, 8, "sea_lantern" if lit else ("polished_andesite" if s == 76 else "smooth_quartz"))
            for y in range(9, 14):
                put(s, t, y, "air")
        # roof
        sky = s == 76 and t % 3 != 0
        lamp = s in (74, 78) and t % 5 == 2
        put(s, t, 14, "glass" if sky else ("sea_lantern" if lamp else "white_concrete"))
        if 74 <= s <= 78:
            put(s, t, 15, "glass" if s == 76 else "smooth_quartz_slab[type=bottom]")
# open the headhouse east wall into the pier
for s in range(73, 80):
    for y in range(9, 14):
        put(s, -73, y, "air")
# ramp-level service doors
for s in (PS1, PS2):
    for t in (-56, -46):
        for y in (0, 1, 2):
            put(s, t, y, "air")

# ---- gates ----
GATES = [  # (side, tcol, gate, airline, dest, livery, tc)
    (-1, -64, "A20", "JetBlue", "Fort Lauderdale", "jetblue", -61),
    (-1, -41, "A24", "American", "Charlotte", "american", -38),
    (+1, -64, "A21", "Delta", "Atlanta", "delta", -61),
    (+1, -41, "A25", "Alaska", "Seattle", "alaska", -38),
]
EXTRA = [(-1, -52, "A22", "JetBlue", "Boston"), (+1, -52, "A23", "American", "Miami"),
         (-1, -31, "A26", "Delta", "Detroit"), (+1, -31, "A27", "Spirit", "Orlando")]


def bridge(s0, d, tcol, n=9):
    """walkable sloping jet bridge from the pier door (walk y9) down toward the aircraft door."""
    for k in range(n):
        s = s0 + d * k
        surf = 9 - k * 0.5
        full = surf == int(surf)
        fy = int(surf) - 1 if full else int(surf)
        roof = math.ceil(surf) + 2
        put(s, tcol, fy, "light_gray_concrete" if full else "smooth_stone_slab[type=bottom]")
        if not full:
            put(s, tcol, fy - 1, "light_gray_concrete")
        for y in range(fy + 1, roof):
            put(s, tcol, y, "air")
        for w in (tcol - 1, tcol + 1):
            put(s, w, fy, "light_gray_concrete")
            if not full:
                put(s, w, fy - 1, "light_gray_concrete")
            for y in range(fy + 1, roof):
                put(s, w, y, "glass_pane" if k % 3 else "light_gray_concrete")
        for w in (tcol - 1, tcol, tcol + 1):
            put(s, w, roof, "light_gray_concrete")
    # cab: open toward the fuselage, end cap
    s_last = s0 + d * (n - 1)
    put(s_last, tcol + 1, 5, "air"); put(s_last, tcol + 1, 6, "air")
    put(s_last, tcol + 1, 4, "black_concrete")
    s_cap = s0 + d * n
    for w in (tcol - 1, tcol, tcol + 1):
        for y in range(3, 8):
            put(s_cap, w, y, "light_gray_concrete")
    put(s_cap, tcol, 5, "glass")
    # rotunda / drive column with wheels
    s_col = s0 + d * (n - 2)
    for y in range(0, 4):
        put(s_col, tcol, y, "light_gray_concrete")
    put(s_col, tcol - 1, 0, "black_concrete"); put(s_col, tcol + 1, 0, "black_concrete")
    put(s0 + d * 2, tcol, 0, "iron_bars"); put(s0 + d * 2, tcol, 1, "iron_bars")
    for y in range(2, 8):
        put(s0 + d * 2, tcol, y, "iron_bars")


for side, tcol, gate, airline, dest, livery, tc in GATES:
    wall = PS1 if side < 0 else PS2
    inner = wall - side          # interior row next to the wall
    for y in (9, 10):
        put(wall, tcol, y, "air")
    put(wall, tcol, 11, "white_concrete")
    sgn(inner, tcol, 11, ["Gate " + gate, airline, "to " + dest], "north" if side < 0 else "south")
    bridge(wall + side, side, tcol)
    # aircraft, nose-in to the pier
    if side < 0:
        plane(at(59, tc, 0, rot=0), livery)
        rect(49, 70, tc, tc, -1, "yellow_concrete")
        rect(70, 70, tc - 2, tc + 2, -1, "yellow_concrete")
    else:
        plane(at(93, tc, 0, rot=2), livery)
        rect(82, 104, tc, tc, -1, "yellow_concrete")
        rect(82, 82, tc - 2, tc + 2, -1, "yellow_concrete")
    # ground-service: tug + baggage carts beside the plane
    cs = 64 if side < 0 else 88
    put(cs, tc + 4, 0, "white_concrete"); put(cs, tc + 4, 1, "black_stained_glass_pane")
    for i in range(1, 4):
        put(cs, tc + 4 + i, 0, "iron_block" if i % 2 else "light_gray_concrete")
        put(cs, tc + 4 + i, 1, rng.choice(["barrel[facing=up]", "red_wool", "blue_wool", "black_wool"]))

# ---- gate lounges: seating rows, podiums ----
door_ts = (-64, -52, -41, -31)
for side in (-1, 1):
    wall = PS1 if side < 0 else PS2
    seat_s = 74 if side < 0 else 78
    pod_s = seat_s
    look = "south" if side < 0 else "north"
    for t in range(-70, -33):
        near = any(tc - 1 <= t <= tc + 3 for tc in door_ts)
        if near:
            continue
        x, z = P(seat_s, t)
        if (t + 70) % 5 == 4:
            b.set(x, 9, z, "smooth_quartz_slab[type=top]")      # charging table
            b.set(x, 10, z, "potted_fern")
        else:
            b.chair(x, 9, z, look, "polished_deepslate_stairs")
    for tc in door_ts:
        put(pod_s, tc + 2, 9, "smooth_quartz"); put(pod_s, tc + 3, 9, "smooth_quartz")
        put(pod_s, tc + 3, 10, "lantern")
# gate signs for the four walk-out / remote lounges (on the window mullion line)
for side, tcol, gate, airline, dest in EXTRA:
    wall = PS1 if side < 0 else PS2
    put(wall, tcol, 11, "white_concrete")
    sgn(wall - side, tcol, 11, ["Gate " + gate, airline, "to " + dest], "north" if side < 0 else "south")

# ---- pier end: Spirit lounge A28 with seats facing the window ----
for s in range(73, 80):
    if s == 76:
        continue
    x, z = P(s, -30)
    b.chair(x, 9, z, "east", "polished_deepslate_stairs")
put(76, -29, 9, "smooth_quartz"); put(76, -29, 10, "lantern")
put(73, -33, 9, "white_concrete"); put(73, -33, 10, "white_concrete"); put(73, -33, 11, "white_concrete")
sgn(73, -34, 11, ["Gate A28", "Spirit", "to Orlando"], "west")
put(79, -33, 9, "white_concrete"); put(79, -33, 10, "white_concrete"); put(79, -33, 11, "white_concrete")
sgn(79, -34, 11, ["Gates A20-A28", "<- Main Hall", "Food / Exit"], "west")

# ---- mid-pier wine & coffee bar island ----
for t in range(-49, -46):
    put(76, t, 9, "smooth_quartz")
put(76, -48, 10, "lantern")
sgn(75, -48, 10, ["Garden State", "Coffee & Wine"], "south")
sgn(77, -48, 10, ["Garden State", "Coffee & Wine"], "north")
# planters at the pier root
for s in (73, 79):
    x, z = P(s, -71)
    b.plant(x, 9, z, "potted_bamboo")
