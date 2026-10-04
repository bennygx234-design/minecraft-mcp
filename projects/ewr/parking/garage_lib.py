# Garage re-stripe generator (exec after kit.py, landside/common.py, parking/plib.py).
# Each garage is widened east from t=-129 to t=-127 so the interior (t -141..-128) is 14 wide:
#   parking row t -141..-135 (3x7 bays, nose west, wheel stop at t=-140) + 7-wide aisle t -134..-128.
# Levels: deck k walk y = 4k, floor block 4k-1, ceiling = next floor 4k+3 -> 3 blocks headroom.
# Ramps: a "scissor" block at s S..S+7 (rise 4 over 8, slab/full alternating = 1 per 2):
#   odd ramps (deck k-1 -> k, k odd) in the west lane t -141..-138, rising north (foot S, top S+7);
#   even ramps in the east lane t -131..-128, rising south (foot S+7, top S).
#   Between them a 4-wide level corridor t -136..-133, guard walls t -137 / -132 (full height),
#   turning zones (full width) at S-Z..S-1 and S+8..S+7+Z.
TW, TE = -142, -127
WL, EL = (-141, -138), (-131, -128)
GW, GE = -137, -132
DECK = "gray_concrete"
WALL = "light_gray_concrete"
RAMP_FILL = "light_gray_concrete"
SLAB = "smooth_stone_slab[type=bottom]"


def lanes(k):
    return WL if k % 2 else EL


def garage(name, s1, s2, L, accent, bridges, S, core, bays, lines, label, kinds=None, rental=None,
           north_row=None, zone=4, lights=None, pillars=None):
    top = 4 * L
    kinds = kinds or {}
    # ---------------------------------------------------------------- clear interior + old east face
    pbox(s1 + 1, s2 - 1, -141, -128, 0, top + 8, "air")
    pbox(core, core + 2, -126, -124, 0, top + 5, "air")
    # ---------------------------------------------------------------- ground + deck floors
    rect(s1 + 1, s2 - 1, -141, -127, -1, DECK)
    rect(s1, s2, -128, -127, -1, DECK)
    for k in range(1, L + 1):
        rect(s1, s2, -141, -127, 4 * k - 1, DECK)
    # ---------------------------------------------------------------- east wall (new line t=-127) + end-wall extensions
    for k in range(0, L + 1):
        y = 4 * k
        blk = accent if k == L else WALL
        for s in range(s1, s2 + 1):
            put(s, TE, y, blk)
        for t in (-128, -127):
            put(s1, t, y, blk); put(s2, t, y, blk)
    for s in range(s1, s2 + 1):
        put(s, TE, top + 1, "smooth_quartz_slab[type=bottom]")
    for t in (-129, -128, -127):
        put(s1, t, top + 1, "smooth_quartz_slab[type=bottom]"); put(s2, t, top + 1, "smooth_quartz_slab[type=bottom]")
    ps = list(range(s1, s2 + 1, 6))
    if ps[-1] != s2:
        ps.append(s2)
    entry = range(S + 1, S + 7)
    for s in ps:
        for k in range(L):
            if s in bridges and k in (0, 1, 2):
                continue                      # bridge post / bridge opening
            if k == 0 and s in entry:
                continue
            if s == core + 1:
                continue
            for yy in range(4 * k, 4 * k + 3):
                put(s, TE, yy, "stone_bricks")
    # ---------------------------------------------------------------- ramps
    for k in range(1, L + 1):
        w = 4 * (k - 1)
        ln = lanes(k)
        for i in range(8):
            s = S + i if k % 2 else S + 7 - i
            y = w + i // 2
            blk = SLAB if i % 2 == 0 else "smooth_stone"
            for t in range(ln[0], ln[1] + 1):
                for yy in range(w, y):
                    put(s, t, yy, RAMP_FILL)
                put(s, t, y, blk)
                if i < 7:
                    for yy in range(y + 1, 4 * k):
                        put(s, t, yy, "air")      # headroom + the hole in deck k
        # rail across the open end of the hole on deck k
        rs = S - 1 if k % 2 else S + 8
        for t in range(ln[0], ln[1] + 1):
            put(rs, t, 4 * k, WALL)
    # guard walls + solid outer walls along the ramp block, every storey
    for k in range(L):
        for s in range(S, S + 8):
            for yy in range(4 * k, 4 * k + 3):
                put(s, GW, yy, WALL); put(s, GE, yy, WALL); put(s, TW, yy, WALL)
                if not (k == 0 and s in entry):
                    put(s, TE, yy, WALL)
    for s in range(S, S + 8):                  # roof rails
        put(s, GW, top, accent); put(s, GE, top, accent)
    # ground entry from the loop road (east lane of the ramp block is free on deck 0)
    for s in entry:
        for yy in range(0, 3):
            put(s, TE, yy, "air")
    rect(S, S + 7, -126, -123, -1, DECK)
    for t in range(-126, -122):
        put(S, t, -1, LINE); put(S + 7, t, -1, LINE)
    x, z = P(S, -124)
    b.sign(x, 0, z, [f"Garage {label}", "ENTRANCE", "<- parking", "headroom 3 m"], facing="east", wall=False)
    # ramp signs on the guard-wall ends
    for k in range(L):
        y = 4 * k + 1
        if k % 2 == 0:      # next ramp up is in the west lane, foot at S, approached from the south
            x, z = P(S - 1, GW); b.sign(x, y, z, ["^ RAMP UP", f"to level {k + 2}", "", "<- west lane"], facing="south")
        else:               # next ramp up is the east lane, foot at S+7, approached from the north
            x, z = P(S + 8, GE); b.sign(x, y, z, ["RAMP UP v", f"to level {k + 2}", "", "east lane ->"], facing="north")
    # ---------------------------------------------------------------- bays, lines, pillars
    for k in range(L + 1):
        fy = 4 * k
        if north_row is None:
            for ls in lines:
                pline(ls, ls, -141, -135, fy)
            for j, (sa, sb) in enumerate(bays):
                kd = kinds.get((k, j), ("std", None))
                if rental and k in rental and kd[0] == "std":
                    kd = ("rental", rental[k][1])
                cs, ct = bay(sa, sb, -141, -135, fy, "-t", kind=kd[0], col=kd[1], tag=f"{label} L{k + 1}",
                             charger=((sa + sb) // 2, TW), charger_y=fy + 1)
                if kd[0] == "rental":
                    x, z = P((sa + sb) // 2, -141)
                    b.sign(x, fy, z, [rental[k][0].upper(), "RENTAL", "ready / return", f"bay {j + 1}"],
                           facing="east", wall=True)
            for ls in (pillars if pillars is not None else lines[1::2]):
                for yy in range(fy, fy + 3):
                    if k < L:
                        put(ls, -138, yy, "gray_concrete")
        else:
            sa, sb, tl = north_row
            for lt in [t for t in range(-138, -127, 4)]:
                pline(sa, sb, lt, lt, fy)
            for j, (ta, tb) in enumerate(tl):
                kd = kinds.get((k, j), ("std", None))
                bay(sa, sb, ta, tb, fy, "+s", kind=kd[0], col=kd[1], tag=f"{label} L{k + 1}",
                    charger=(s2, (ta + tb) // 2), charger_y=fy + 1)
            if k < L:
                for yy in range(fy, fy + 3):
                    put((sa + sb) // 2, -138, yy, "gray_concrete")
                    put((sa + sb) // 2, -130, yy, "gray_concrete")
    # flush ceiling lights in the aisle
    for k in range(1, L + 1):
        for s in (lights or range(s1 + 3, s2 - 1, 6)):
            if not (S - 1 <= s <= S + 8):
                put(s, -131, 4 * k - 1, "sea_lantern")
        put(S - 2, -134, 4 * k - 1, "sea_lantern"); put(S + 9, -134, 4 * k - 1, "sea_lantern")
    # ---------------------------------------------------------------- pedestrian bridges (deck 2, walk y 8)
    for bs in bridges:
        for s in range(bs - 1, bs + 2):
            if S <= s <= S + 7:
                continue
            for yy in (8, 9, 10):
                put(s, TE, yy, "air")
        for s in (bs - 2, bs + 2):
            for yy in (8, 9, 10):
                put(s, TE, yy, "light_blue_stained_glass")
    # ---------------------------------------------------------------- stair core, outside the east wall
    pbox(core, core + 2, -126, -124, 0, top + 3, "light_blue_stained_glass", hollow=True)
    pbox(core, core + 2, -126, -124, top + 4, top + 4, "white_concrete")
    put(core + 1, -125, top + 3, "sea_lantern")
    for yy in range(0, top + 1):
        put(core + 1, -125, yy, "ladder[facing=west]")
    for k in range(L + 1):
        for yy in (4 * k, 4 * k + 1):
            put(core + 1, -126, yy, "air"); put(core + 1, TE, yy, "air")
    x, z = P(core + 1, -123)
    b.sign(x, 0, z, ["Stairs", f"Garage {label}", "all levels"], facing="east", wall=False)
    # ---------------------------------------------------------------- roof: lamps on the parapets + sign
    for s in range(s1 + 4, s2 - 2, 8):
        if not (S - 1 <= s <= S + 8):
            lamp_post(s, TW, top + 1); lamp_post(s, TE, top + 1)
    n = len(label)
    ws = 4 * n + 1
    mid = (s1 + s2) // 2
    s0 = mid - ws // 2
    pbox(s0, s0 + ws - 1, TE, TE, top + 1, top + 7, accent)
    etext(s0 + 1, TE + 1, top + 2, label, "white_concrete")
