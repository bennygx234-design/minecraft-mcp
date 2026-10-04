exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
# ---------------------------------------------------------------------------------------------
# EWR Terminal C (United hub).  Zone: s 168..232, t -100..-27.
# Curved headhouse (convex facade toward the landside / west), 3 concourses radiating east.
# Levels: arrivals feet y=0 (baggage claim), departures + concourses floor y=5 (feet 6),
#         AirTrain mezzanine floor y=8 (feet 9) linked by a skybridge to the station at s~184.
# ---------------------------------------------------------------------------------------------
S1, S2, T1, T2 = 168, 232, -100, -27
CS, CT, R = 200.0, -53.0, 44.0          # headhouse curve centre + radius
EAST = -78                              # headhouse airside wall (t)
G = {}


def inz(s, t):
    return S1 <= s <= S2 and T1 <= t <= T2


def g(s, t, y, blk):
    if inz(s, t) and -1 <= y <= 60:
        G[(s, t, y)] = blk


def gcol(s, t, y1, y2, blk):
    for y in range(y1, y2 + 1):
        g(s, t, y, blk)


def dd(s, t):
    return math.hypot(s - CS, t - CT)


def inF(s, t):
    return 172 <= s <= 228 and -100 <= t <= EAST and dd(s, t) <= R


def edgeF(s, t):
    return inF(s, t) and not all(inF(s + a, t + c) for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)))


# ---- concourses: (name, A, B, gate numbers) --------------------------------------------------
CONC = [
    ("C1", (189.0, -78.0), (181.0, -65.0), ["C71", "C72", "C73", "C74", "C75"]),
    ("C2", (200.0, -78.0), (200.0, -59.0), ["C101", "C102", "C103", "C104", "C105"]),
    ("C3", (211.0, -78.0), (219.0, -65.0), ["C120", "C121", "C122", "C123", "C124"]),
]
HW_IN, HW_OUT = 4.5, 5.5


def seg(s, t, A, B):
    (as_, at_), (bs, bt) = A, B
    ds, dt = bs - as_, bt - at_
    L = math.hypot(ds, dt)
    us, ut = ds / L, dt / L                     # unit along axis
    ps, pt = -ut, us                            # unit perpendicular (left of axis)
    u = (s - as_) * us + (t - at_) * ut
    v = (s - as_) * ps + (t - at_) * pt
    uc = max(0.0, min(L, u))
    dist = math.hypot(s - (as_ + us * uc), t - (at_ + ut * uc))
    return dist, u, v, L, (us, ut), (ps, pt)


def conc_cell(s, t):
    """-> ('in'|'wall'|None, index of concourse, u, v)"""
    best = None
    for i, (nm, A, B, gates) in enumerate(CONC):
        dist, u, v, L, _, _ = seg(s, t, A, B)
        if dist <= HW_IN:
            return "in", i, u, v
        if dist <= HW_OUT and best is None:
            best = ("wall", i, u, v)
    return best if best else (None, -1, 0, 0)


# ================================ 1. GROUND ====================================================
for s in range(S1, S2 + 1):
    for t in range(-77, T2 + 1):
        g(s, t, -1, "smooth_stone")                          # extend the apron to the terminal
# lead-in lines for the three parking stands
for ps_ in (179, 200, 221):
    for t in range(-58 if ps_ != 200 else -51, -27):
        g(ps_, t, -1, "yellow_concrete")
# landside sidewalk ring + small plaza
for s in range(S1, S2 + 1):
    for t in range(T1, EAST + 1):
        if not inF(s, t):
            dv = dd(s, t)
            if dv <= 47.5 or (s < 172 or s > 228) and dv <= 48:
                g(s, t, -1, "light_gray_concrete")
            elif dv <= 49:
                g(s, t, -1, "smooth_stone")

# ================================ 2. HEADHOUSE =================================================
ROOF = 16
for s in range(172, 229):
    for t in range(-100, EAST + 1):
        if not inF(s, t):
            continue
        dv = dd(s, t)
        g(s, t, -1, "light_gray_concrete" if (s % 6 == 0 or t % 6 == 0) else "smooth_quartz")
        # departures floor (= arrivals ceiling)
        g(s, t, 5, "sea_lantern" if (s % 5 == 2 and t % 5 == 2) else
          ("light_gray_concrete" if (s % 6 == 3 or t % 6 == 3) else "polished_diorite"))
        # roof with skylight band
        if 31.5 <= dv <= 33.5:
            g(s, t, ROOF, "light_blue_stained_glass")
        else:
            g(s, t, ROOF, "sea_lantern" if (s % 5 == 0 and t % 5 == 0) else "white_concrete")
        if edgeF(s, t):
            west = t < EAST
            # mullions every 4 blocks along the curve
            ang = math.degrees(math.atan2(s - CS, -(t - CT)))
            mull = (int(round(ang / 4.5)) % 2 == 0) and west and t != EAST
            for y in range(0, ROOF + 1):
                if y in (5, ROOF):
                    blk = "white_concrete"
                elif t == EAST and y <= 4:
                    blk = "light_gray_concrete" if y in (0, 4) else "light_gray_stained_glass"
                elif s in (172, 228) and t > -84:
                    blk = "white_concrete" if y % 5 == 0 else "light_gray_stained_glass"
                else:
                    blk = "white_concrete" if (mull and y % 3 == 0) else "light_gray_stained_glass"
                g(s, t, y, blk)
            g(s, t, ROOF + 1, "smooth_quartz_slab[type=bottom]")   # parapet

# big blue "C" on the facade at s 197..203 (the facade there is ~t -97)
C_ART = ["01110", "10001", "10000", "10000", "10000", "10001", "01110"]
for row, line in enumerate(C_ART):
    for col, ch in enumerate(line):
        if ch == "1":
            s = 202 - col
            y = 14 - row
            for t in range(-100, EAST):
                if edgeF(s, t):
                    g(s, t, y, "blue_concrete")
                    break

# arrivals doors on the west facade (3 high openings) + departures doors to the curb deck
for s0 in (178, 186, 194, 206, 214, 222):
    for s in (s0, s0 + 1):
        for t in range(-100, -86):
            if edgeF(s, t) and t < -86:
                gcol(s, t, 0, 2, "air")
for s in (197, 198, 202, 203):
    for t in range(-100, -88):
        if edgeF(s, t):
            gcol(s, t, 6, 8, "air")

# ---- AirTrain skybridge (s 182..186) at mezzanine level y=8 -----------------------------------
for s in range(182, 187):
    for t in range(-99, -80):
        if inF(s, t) and not edgeF(s, t):
            break
        if edgeF(s, t):
            if 183 <= s <= 185:
                gcol(s, t, 9, 11, "air")
                g(s, t, 8, "smooth_quartz")
            continue
        if inF(s, t):
            continue
        g(s, t, 8, "smooth_quartz")
        g(s, t, 12, "white_concrete")
        if s in (182, 186):
            gcol(s, t, 9, 11, "light_blue_stained_glass")
        else:
            gcol(s, t, 9, 11, "air")
            if t % 2 == 0:
                g(s, t, 11, "air")
    # bridge support
for t in (-99, -97):
    for s in (182, 186):
        if not inF(s, t):
            gcol(s, t, 0, 7, "white_concrete")

# ---- departures curb deck along the facade (s 188..222), with stair down at the north end -------
for s in range(188, 223):
    for t in range(-100, EAST):
        if inF(s, t):
            continue
        dv = dd(s, t)
        if 44 < dv <= 47.6:
            g(s, t, 5, "white_concrete")
            g(s, t, 10, "smooth_quartz_slab[type=bottom]")
            if dv > 46.6 or t == -100:
                g(s, t, 6, "glass_pane")
                if s % 6 == 0:
                    gcol(s, t, 0, 4, "white_concrete")
                    gcol(s, t, 6, 9, "white_concrete")
for k, s in enumerate(range(227, 222, -1)):          # stairs: s=227 y0 ... s=223 y4, deck at 222
    for t in (-93, -92):
        g(s, t, k, "quartz_stairs[facing=south]")
        gcol(s, t, k + 1, k + 3, "air")
for t in (-93, -92):
    g(222, t, 5, "white_concrete")
    g(222, t, 6, "air")
    g(222, t, 10, "air")

# ---- AirTrain mezzanine inside the facade (s 176..194, d 40..43) + stair down -----------------
for s in range(176, 195):
    for t in range(-100, EAST):
        if inF(s, t) and not edgeF(s, t):
            dv = dd(s, t)
            if dv >= 40:
                g(s, t, 8, "smooth_quartz" if dv >= 41 else "white_concrete")
                if dv < 41:
                    g(s, t, 9, "glass_pane")
for s, y in ((195, 7), (196, 6)):
    for t in range(-100, EAST):
        if inF(s, t) and not edgeF(s, t) and dd(s, t) >= 40.5:
            g(s, t, y, "quartz_stairs[facing=south]")
            g(s, t, 8, "air")
            g(s, t, 9, "air")
# gap in the mezzanine railing at the stair head + skybridge landing
for t in range(-100, EAST):
    if inF(194, t) and not edgeF(194, t) and dd(194, t) >= 40:
        g(194, t, 9, "air")

# ---- arrivals <-> departures stairs (landside, d 33..35) ---------------------------------------
STAIRS = [(range(192, 197), +1), (range(208, 203, -1), -1)]
for rs, dirn in STAIRS:
    for k, s in enumerate(rs):
        for t in (-87, -86):
            g(s, t, k, f"quartz_stairs[facing={'north' if dirn > 0 else 'south'}]")
            for y in range(k + 1, 5):
                g(s, t, y, "air")
            if k >= 1:
                g(s, t, 5, "air")
    # glass railing around the opening on the departures level
    ss = list(rs)
    for s in ss[1:]:
        g(s, -88, 6, "glass_pane"); g(s, -85, 6, "glass_pane")
    g(ss[0], -87, 6, "glass_pane"); g(ss[0], -86, 6, "glass_pane")
    g(ss[0] - dirn, -88, 6, "glass_pane"); g(ss[0] - dirn, -85, 6, "glass_pane")

# ---- departures hall: check-in counter arc (d~39), bag belt (d~37), security (d~30) -----------
LANES = (190, 194, 198, 202, 206, 210)
for s in range(172, 229):
    for t in range(-100, EAST + 1):
        if not inF(s, t) or edgeF(s, t):
            continue
        dv = dd(s, t)
        gap = (s % 7 in (0, 1))
        if 38.5 <= dv < 39.5 and not gap:
            g(s, t, 6, "smooth_quartz")                         # check-in desk
            if s % 7 == 3:
                g(s, t, 7, "light_gray_stained_glass")          # screen
        elif 36.5 <= dv < 37.5 and not gap:
            g(s, t, 6, "smooth_stone_slab[type=bottom]")        # bag belt
            gcol(s, t, 7, 7, "air")
        elif 35.5 <= dv < 36.5 and not gap:
            gcol(s, t, 6, 9, "blue_concrete" if s % 7 != 4 else "light_blue_concrete")  # United wall
        # security wall + lanes
        if 29.5 <= dv < 30.5:
            if s in LANES:
                g(s, t, 9, "light_gray_concrete")
            elif s - 1 in LANES or s + 1 in LANES:
                gcol(s, t, 6, 9, "light_gray_concrete")          # walk-through scanner frame
            else:
                gcol(s, t, 6, 8, "glass_pane")
        if 30.5 <= dv < 32.5 and (s - 2) in LANES:
            g(s, t, 6, "smooth_stone_slab[type=top]" if dv >= 31.5 else "gray_concrete")  # x-ray
            if 30.5 <= dv < 31.5:
                g(s, t, 7, "gray_concrete")

# ---- arrivals: three baggage carousels --------------------------------------------------------
for c, (sa, sb) in enumerate(((180, 188), (196, 204), (212, 220))):
    for s in range(sa, sb + 1):
        for t in range(-84, -79):
            if s in (sa, sb) or t in (-84, -80):
                g(s, t, -1, "black_concrete")
                g(s, t, 0, "polished_blackstone_slab[type=bottom]")
            else:
                g(s, t, 0, "light_gray_concrete")
                g(s, t, 1, "smooth_stone_slab[type=bottom]")

# east (airside) wall: openings into the three concourses at departures level
for s in range(172, 229):
    kind, i, u, v = conc_cell(s, EAST)
    st, i2, u2, v2 = conc_cell(s, EAST + 1)
    if st == "in":
        gcol(s, EAST, 6, 10, "air")
        g(s, EAST, 5, "polished_diorite")

# ================================ 3. CONCOURSES ===============================================
CROOF = 11
for s in range(S1, S2 + 1):
    for t in range(EAST + 1, T2 + 1):
        kind, i, u, v = conc_cell(s, t)
        if kind is None:
            continue
        gcol(s, t, 0, 4, "light_gray_concrete")              # ramp / ops level (solid)
        if kind == "wall":
            g(s, t, 5, "white_concrete")
            post = int(u) % 5 == 0
            for y in range(6, CROOF):
                g(s, t, y, "white_concrete" if (post or y == 10) else "glass")
            g(s, t, CROOF, "white_concrete")
            g(s, t, CROOF + 1, "smooth_quartz_slab[type=bottom]")
        else:
            aisle = abs(v) <= 1.5
            g(s, t, 5, "light_gray_concrete" if aisle else "polished_diorite")
            g(s, t, CROOF, "sea_lantern" if (s % 4 == 0 and t % 4 == 0) else "white_concrete")
            for y in range(6, CROOF):
                g(s, t, y, "air")

# ---- emit grid --------------------------------------------------------------------------------
for (s, t, y), blk in G.items():
    put(s, t, y, blk)


# ================================ 4. FURNITURE (direct) ========================================
def X(s, t):
    return P(s, t)


def chair_pt(s, t, y, facing, blk="blue_terracotta"):
    if inz(s, t):
        x, z = X(s, t)
        b.chair(x, y, z, facing, "dark_oak_stairs")


def sign_pt(s, t, y, lines, facing):
    if inz(s, t):
        x, z = X(s, t)
        b.sign(x, y, z, lines, facing=facing, wall=False, wood="birch")


def post(s, t, ytop):
    if inz(s, t):
        x, z = X(s, t)
        for y in range(6, ytop + 1):
            b.set(x, y, z, "quartz_block")


def dir_of(vs, vt):
    """plan vector -> builder direction name"""
    if abs(vs) >= abs(vt):
        return "north" if vs > 0 else "south"
    return "east" if vt > 0 else "west"


# concourse interiors: shops / food court near the headhouse, gate lounges beyond, gate desks
for i, (nm, A, B, gates) in enumerate(CONC):
    _, _, _, L, (us, ut), (ps, pt) = seg(A[0], A[1], A, B)
    outward_l = dir_of(ps, pt)          # toward the +v wall
    outward_r = dir_of(-ps, -pt)
    for s in range(S1, S2 + 1):
        for t in range(EAST + 1, T2 + 1):
            kind, j, u, v = conc_cell(s, t)
            if kind != "in" or j != i:
                continue
            x, z = X(s, t)
            av = abs(v)
            side = outward_l if v > 0 else outward_r
            inward = outward_r if v > 0 else outward_l
            if 1.5 <= u < 8.5:                                       # shops / food court
                if av > 3.5:
                    if nm == "C2":
                        b.set(x, 6, z, "smoker[facing=%s]" % inward if int(u) % 3 == 0 else "smooth_stone_slab[type=top]")
                        b.set(x, 7, z, "air")
                    elif nm == "C1":
                        b.set(x, 6, z, "bookshelf"); b.set(x, 7, z, "bookshelf" if int(u) % 2 else "light_blue_concrete")
                    else:
                        b.set(x, 6, z, "barrel[facing=up]"); b.set(x, 7, z, "flower_pot" if int(u) % 2 else "air")
                elif nm == "C2" and 2.2 <= av <= 3.2 and int(u) % 3 == 1:
                    b.table(x, 6, z, "birch_fence", "white_carpet")
            elif 9.5 <= u <= L + 1 and 1.6 < av <= 3.6 and int(u) % 4 != 1:  # gate lounge seating
                if av <= 2.6:
                    b.chair(x, 6, z, inward, "dark_oak_stairs")
                else:
                    b.chair(x, 6, z, side, "dark_oak_stairs")
            elif u > L + 1.5 and av <= 1.5 and u < L + 2.6:          # gate desk at the tip
                b.set(x, 6, z, "quartz_block")
            if av <= 0.5 and int(u) % 6 == 3 and u < L:
                b.set(x, 10, z, "lantern[hanging=true]")
    # signs along the concourse
    def at_uv(u, v):
        return (int(round(A[0] + us * u + ps * v)), int(round(A[1] + ut * u + pt * v)))
    fwd = dir_of(-us, -ut)  # readable from the headhouse side
    s_, t_ = at_uv(1.0, 3.9)
    post(s_, t_, 7)
    sign_pt(s_, t_, 8, ["Concourse " + nm, "Gates", gates[0] + "-" + gates[-1], "United"], fwd)
    s_, t_ = at_uv(3.0, -3.0)
    post(s_, t_, 7)
    sign_pt(s_, t_, 8, ["Food Court" if nm == "C2" else ("Hudson News" if nm == "C1" else "Duty Free"),
                         "", "open 5am-11pm"], fwd)
    for k, (uu, vv) in enumerate(((10.5, 3.9), (10.5, -3.9), (L - 1, 3.9), (L - 1, -3.9))):
        s_, t_ = at_uv(uu, vv)
        b.set(*(lambda p: (p[0], 6, p[1]))(X(s_, t_)), "quartz_block")
        sign_pt(s_, t_, 7, ["Gate", gates[k + 1], "to " + ["SFO", "ORD", "DEN", "IAH"][k], "UA"], fwd)
    s_, t_ = at_uv(L + 2.0, 0)
    post(s_, t_, 6)
    sign_pt(s_, t_, 7, ["Gate", gates[0], "Boarding", "UA"], fwd)

# headhouse signage (standing signs readable from the curb / west)
sign_pt(184, -92, 9, ["AirTrain", "Terminal C", "<- trains", ""], "east")
sign_pt(200, -92, 7, ["UNITED", "Check-in", "Bag drop", ""], "west")
sign_pt(186, -89, 7, ["UNITED", "Premier Access", "", ""], "west")
sign_pt(214, -89, 7, ["UNITED", "Check-in", "Kiosks", ""], "west")
sign_pt(200, -88, 6, ["TSA", "Security", "Checkpoint", "Gates C70-C139"], "west")
for c, sc in enumerate((184, 200, 216)):
    sign_pt(sc, -82, 2, ["Baggage Claim", str(c + 1), "", ""], "west")
sign_pt(200, -95, 0, ["Arrivals", "Ground", "Transportation", "Taxi / Rideshare"], "east")
sign_pt(200, -79, 6, ["<- C1  C2  C3 ->", "All gates", "", ""], "west")

# arrivals lighting (floor lamps near carousels) and hall plants
for s in (176, 192, 208, 224):
    x, z = X(s, -90)
    if inF(s, -90):
        b.plant(x, 6, z, "potted_bamboo")

# ================================ 5. APRON: jet bridges + United planes ========================
for (ps_, ct, conc_i) in ((179, -45, 0), (200, -38, 1), (221, -45, 2)):
    plane(at(ps_, ct, 0, rot=3), "united")
    bs = ps_ + 2
    t0 = EAST + 1
    while conc_cell(bs, t0)[0] is not None or t0 < -70:
        t0 += 1
    nose = ct - 12
    length = (nose + 6) - t0 + 1
    jet_bridge(bs, t0, length, "+t", y=4)
    # ground equipment
    put(ps_ - 3, nose - 1, 0, "yellow_concrete")
    put(ps_ - 3, nose, 0, "yellow_concrete")
