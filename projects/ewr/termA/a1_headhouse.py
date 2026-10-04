exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
# Terminal A headhouse: t -95..-73, s 52..102. Level 1 (walk y0) arrivals/baggage, level 2 (walk y9) departures.
S1, S2, T1, T2 = 52, 102, -95, -73

def R(s, t):
    return 20 + round(2.2 * math.sin(2 * math.pi * (s - 52) / 26)) + round((-73 - t) / 10)

def lean(y):      # west curtain wall plan-t at height y (leans outward above y 15)
    return -95 if y <= 15 else -96

# ---------- landside curb road + sidewalk (ground repaint) ----------
rect(48, 105, -99, -98, -1, "gray_concrete")
for s in range(48, 106, 3):
    put(s, -98, -1, "white_concrete") if s % 6 == 0 else None
rect(48, 105, -97, -96, -1, "smooth_stone")
# ---------- ground floor slab ----------
rect(S1, S2, T1, T2, -1, {"polished_diorite": 3, "smooth_stone": 1})

# ---------- shell walls ----------
for s in range(S1, S2 + 1):
    for t in range(T1 - 1, T2 + 1):
        top = R(s, t)
        if t == T1 - 1:
            for y in range(16, top):
                put(s, t, y, "light_gray_stained_glass" if s % 4 else "white_concrete")
            continue
        if t == T1:   # west curtain wall
            for y in range(0, min(top, 16)):
                blk = "white_concrete" if (s % 4 == 0 or y == 8) else "light_blue_stained_glass"
                put(s, t, y, blk)
        elif t == T2:  # east wall (airside)
            for y in range(0, top):
                blk = "light_gray_concrete" if y < 8 else ("white_concrete" if s % 5 == 0 or y == 8 else "glass")
                put(s, t, y, blk)
        elif s in (S1, S2):  # end walls
            for y in range(0, top):
                band = y in (3, 4, 5, 11, 12, 13, 14, 15, 16)
                blk = "glass" if (band and t % 4) else "white_concrete"
                put(s, t, y, blk)
        else:   # interior air
            for y in range(0, top):
                if y not in (8,):
                    put(s, t, y, "air")
# ---------- wavy roof with skylights + canopy over the curb ----------
for s in range(S1 - 1, S2 + 2):
    for t in range(-99, T2 + 2):
        y = R(s, t)
        sky = (-92 <= t <= -76) and (s - 52) % 7 == 3 and S1 < s < S2
        lamp = (-92 <= t <= -76) and (s - 52) % 7 == 0 and t % 4 == 0 and S1 < s < S2
        put(s, t, y, "glass" if sky else ("sea_lantern" if lamp else "white_concrete"))
        if t <= -96 or s in (S1 - 1, S2 + 1) or t == T2 + 1:
            put(s, t, y - 1, "smooth_quartz_slab[type=top]")   # fascia edge
# canopy columns over the curb
for s in range(52, 104, 8):
    if 68 <= s <= 76:
        continue
    for y in range(0, R(s, -97)):
        put(s, -97, y, "white_concrete" if y % 6 else "smooth_quartz")

# ---------- level 2 floor (walk y9) with ceiling lights for level 1 ----------
for s in range(S1 + 1, S2):
    for t in range(T1 + 1, T2):
        lit = (t + 94) % 5 == 2 and (s - 53) % 5 == 2
        put(s, t, 8, "sea_lantern" if lit else ({"smooth_quartz": 3, "polished_diorite": 1} if (s + t) % 2 else "smooth_quartz"))
# floor holes for the two staircases
pbox(66, 72, -86, -85, 8, 8, "air")       # landside stair (bag claim <-> departures)
pbox(84, 90, -76, -75, 8, 8, "air")       # airside exit stair down to bag claim
# glass rails around holes on level 2
for s in range(65, 73): put(s, -87, 9, "glass_pane")
for t in (-86, -85): put(65, t, 9, "glass_pane")
for s in range(83, 91): put(s, -77, 9, "glass_pane"); put(s, -74, 9, "glass_pane")
for t in (-76, -75): put(83, t, 9, "glass_pane")
# staircases (polished diorite steps on solid support)
b.stairs_run(-86, 0, -64, "north", 9, "polished_diorite_stairs", width=2, support="smooth_stone")
b.stairs_run(-76, 0, -82, "north", 9, "polished_diorite_stairs", width=2, support="smooth_stone")
# stairs_run width goes to the right of 'north' (= east, +t): x -86,-85 and -76,-75

# ---------- AirTrain skybridge at level 2 (station deck y8 at t<=-100) ----------
rect(70, 74, -99, -96, 8, "smooth_quartz")
for t in range(-99, -95):
    for y in (9, 10, 11):
        put(70, t, y, "glass"); put(74, t, y, "glass")
        for s in (71, 72, 73):
            put(s, t, y, "air")
    rect(70, 74, t, t, 12, "smooth_quartz_slab[type=bottom]")
    put(72, t, 12, "glass")
    put(70, t, 7, "light_gray_concrete"); put(74, t, 7, "light_gray_concrete")
for s in (71, 72, 73):
    put(s, -100, 9, "air")                         # open the station railing into the bridge
    for y in (9, 10, 11): put(s, -95, y, "air")    # door in the curtain wall
b.sign(-97, 11, -73, ["Terminal A", "Departures", "Gates A1-A33"], facing="south")
b.sign(-96, 10, -71, ["<- AirTrain", "Terminal A"], facing="south", wall=True)

# ---------- big blue 'A' on the curtain wall above the skybridge ----------
A = [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"]
for r, row in enumerate(A):
    for c, ch in enumerate(row):
        if ch == "#":
            y = 19 - r
            put(70 + c, lean(y) - (1 if y <= 15 else 0), y, "blue_concrete")

# ---------- ground-level entrances (west) ----------
for s0 in (59, 85, 95):
    for s in (s0, s0 + 1):
        put(s, -95, 0, "air"); put(s, -95, 1, "air"); put(s, -95, 2, "air")
    rect(s0 - 1, s0 + 2, -96, -96, 3, "smooth_quartz_slab[type=bottom]")
b.sign(-96, 2, -61, ["Arrivals", "Baggage Claim"], facing="west")
b.sign(-96, 2, -87, ["Arrivals", "Taxi / Rideshare"], facing="west")
b.sign(-96, 2, -97, ["Ground", "Transportation"], facing="west")
