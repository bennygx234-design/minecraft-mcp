exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
# South cargo area, build 1: apron ground + FedEx and UPS cargo warehouses.
S1, S2, T1, T2 = -14, 46, -100, -27

# ---- ground: whole zone becomes smooth-stone cargo apron, landside service road at the west edge
rect(S1, S2, T1, T2, -1, "smooth_stone")
rect(S1, S2, T1, T1, -1, "gray_concrete")

FONT = {
    "F": ["###", "#..", "##.", "#..", "#.."], "E": ["###", "#..", "##.", "#..", "###"],
    "D": ["##.", "#.#", "#.#", "#.#", "##."], "X": ["#.#", "#.#", ".#.", "#.#", "#.#"],
    "U": ["#.#", "#.#", "#.#", "#.#", "###"], "P": ["##.", "#.#", "##.", "#..", "#.."],
    "S": ["###", "#..", "###", "..#", "###"],
}


def pwalls(s1, s2, t1, t2, y1, y2, block):
    b.walls(int(t1), y1, int(-s2), int(t2), y2, int(-s1), block)


def roof_text(text, s_top, t0, y, colors):
    """block letters on a roof, read with plan +s (in-game north) up"""
    t = t0
    for i, ch in enumerate(text):
        col = colors[i] if isinstance(colors, (list, tuple)) else colors
        for r, row in enumerate(FONT[ch]):
            for c, px in enumerate(row):
                if px == "#":
                    put(s_top - r, t + c, y, col)
        t += 4


def warehouse(s1, s2, t1, t2, H, wall, band, stripe, name, letters, lcolors, crate_mix):
    # floor + shell
    rect(s1, s2, t1, t2, -1, "polished_andesite")
    pbox(s1, s2, t1, t2, 0, H - 1, wall, hollow=True)
    pbox(s1 + 1, s2 - 1, t1 + 1, t2 - 1, 0, H - 1, "air")
    rect(s1, s2, t1, t2, H, "light_gray_concrete")
    # livery bands around the top
    for y in (H - 2, H - 1):
        pwalls(s1, s2, t1, t2, y, y, band)
    pwalls(s1, s2, t1, t2, H - 3, H - 3, stripe)
    pwalls(s1, s2, t1, t2, H + 1, H + 1, band)          # parapet
    # clerestory windows on the short (north/south) walls
    for t in range(t1 + 2, t2 - 1, 3):
        for s in (s1, s2):
            pbox(s, s, t, t + 1, H - 6, H - 5, "light_gray_stained_glass_pane")
    # ---- airside loading docks on the east wall (t = t2)
    k = 0
    for s in range(s1 + 2, s2 - 2, 3):
        open_ = (k % 3 == 1)
        pbox(s, s + 1, t2, t2, 0, 3, "air" if open_ else "iron_block")
        put(s - 1, t2 + 1, 0, "black_concrete"); put(s + 2, t2 + 1, 0, "black_concrete")   # dock bumpers
        put(s, t2, 4, "sea_lantern")                                                          # dock light
        rect(s, s + 1, t2 + 1, t2 + 1, -1, "yellow_concrete")                                 # dock edge
        k += 1
    # dock canopy
    rect(s1 + 1, s2 - 1, t2 + 1, t2 + 2, 5, "smooth_stone_slab[type=top]")
    for s in range(s1 + 3, s2 - 2, 6):
        put(s, t2 + 2, 4, "lantern[hanging=true]")
    # ---- landside (west) truck docks + staff doors
    for s in range(s1 + 3, s2 - 3, 4):
        pbox(s, s + 1, t1, t1, 0, 2, "iron_block")
        put(s, t1, 3, "sea_lantern")
    mid = (s1 + s2) // 2
    b.door(t1, 0, -mid, "east", "iron_door")
    # side personnel doors (north wall)
    b.door(t2 - 3, 0, -s2, "south", "iron_door")
    # ---- interior: racks, sort belt, ULD build-up area, office, lights
    # pallet racks in rows running along s (west half)
    for t in range(t1 + 2, t1 + (t2 - t1) // 2, 3):
        for s in range(s1 + 3, s2 - 6):
            for y in (1, 3, 5):
                put(s, t, y, "spruce_slab[type=top]")
            for y in (0, 2, 4):
                put(s, t, y, crate_mix)
        for s in (s1 + 3, s2 - 7):
            pbox(s, s, t, t, 0, 5, "iron_bars")
    # sorting conveyor along s through the middle
    tc = t1 + (t2 - t1) // 2 + 2
    for s in range(s1 + 2, s2 - 1):
        put(s, tc, 0, "smooth_stone_slab[type=top]")
        put(s, tc + 1, 0, "smooth_stone_slab[type=top]")
        if s % 3 == 0:
            put(s, tc + (s % 2), 1, crate_mix)
    # side spurs to the docks
    for s in range(s1 + 4, s2 - 3, 6):
        for t in range(tc + 2, t2 - 3):
            put(s, t, 0, "smooth_stone_slab[type=top]")
    # ULD build-up area inside the docks: rows of containers
    for s in range(s1 + 2, s2 - 1, 2):
        if s % 6 != (s1 + 4) % 6:
            put(s, t2 - 2, 0, crate_mix)
    # supervisors' office in the south-west corner
    pbox(s1 + 1, s1 + 5, t1 + 1, t1 + 6, 0, 3, "white_concrete", hollow=True)
    pwalls(s1 + 1, s1 + 5, t1 + 1, t1 + 6, 1, 2, "glass_pane")
    pbox(s1 + 2, s1 + 4, t1 + 2, t1 + 5, 0, 2, "air")
    rect(s1 + 2, s1 + 4, t1 + 2, t1 + 5, 3, "white_concrete")
    b.door(t1 + 4, 0, -(s1 + 5), "south", "oak_door")
    put(s1 + 2, t1 + 2, 0, "oak_planks"); put(s1 + 2, t1 + 3, 0, "oak_planks")
    b.chair(t1 + 2, 0, -(s1 + 3), "south")
    b.lamp(t1 + 5, 0, -(s1 + 2), "lantern")
    b.sign(t1 + 4, 2, -(s1 + 6), ["SHIFT", "SUPERVISOR", name], facing="north")
    # high-bay lights
    for s in range(s1 + 3, s2 - 1, 5):
        for t in range(t1 + 3, t2 - 1, 5):
            put(s, t, H, "sea_lantern")
            put(s, t, H - 1, "lantern[hanging=true]")
    # ---- roof: skylights, HVAC units, giant name
    for t in range(t1 + 3, t2 - 2, 6):
        rect(s1 + 2, s1 + 3, t, t + 1, H, "glass")
        rect(s2 - 3, s2 - 2, t, t + 1, H, "glass")
    for s, t in ((s2 - 6, t1 + 3), (s1 + 6, t2 - 5), (s2 - 6, t2 - 5)):
        pbox(s, s + 2, t, t + 2, H + 1, H + 2, "light_gray_concrete")
        rect(s, s + 2, t, t + 2, H + 3, "iron_bars")
    w = 4 * len(letters) - 1
    roof_text(letters, (s1 + s2) // 2 + 2, (t1 + t2) // 2 - w // 2, H + 1, lcolors)
    # big name signs on the airside and north walls
    b.sign(t2 + 1, H - 4, -(mid), [name, "CARGO"], facing="east")
    b.sign(t2 + 1, H - 4, -(mid + 1), [name, "CARGO"], facing="east")


# FedEx Express EWR hub (one of FedEx's largest) - purple/orange, biggest building
warehouse(20, 45, -99, -76, 12, "white_concrete", "purple_concrete", "orange_concrete",
          "FedEx", "FEDEX", ["purple_concrete"] * 3 + ["orange_concrete"] * 2,
          {"barrel[facing=up]": 3, "chest[facing=east]": 2, "purple_shulker_box": 1,
           "orange_shulker_box": 1, "white_shulker_box": 1})
# UPS - brown/gold
warehouse(-2, 15, -99, -79, 10, "brown_terracotta", "brown_concrete", "yellow_concrete",
          "UPS", "UPS", "yellow_concrete",
          {"barrel[facing=up]": 3, "chest[facing=east]": 2, "brown_shulker_box": 2, "yellow_shulker_box": 1})
