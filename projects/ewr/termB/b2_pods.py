exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\termB\lib.py").read())
# ---- Terminal B satellites B1/B2/B3 (octagonal pods, gate level floor y4), connectors, jet bridges ----
TC, R = -73, 6
PODS = [  # (centre s, name, gate range, kiosk names)
    (127, "B1", "Gates B40-B47", ["B1 Duty Free", "Hudson News"]),
    (143, "B2", "Gates B51-B57", ["B2 Duty Free", "Cafe Europa"]),
    (158, "B3", "Gates B60-B68", ["B3 Duty Free", "Global Bar"]),
]

# apron repaint under the satellites / connectors
rect(120, 166, -81, -73, -1, "smooth_stone")


def inside(dx, dz):
    return octa(dx, dz, R)


def is_wall(dx, dz):
    return inside(dx, dz) and not all(inside(dx + a, dz + c) for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)))


for sc, name, gates, shops in PODS:
    cells = [(dx, dz) for dx in range(-R, R + 1) for dz in range(-R, R + 1) if inside(dx, dz)]
    for dx, dz in cells:          # dx = plan t offset, dz = plan s offset
        s, t = sc + dz, TC + dx
        pbox(s, s, t, t, 0, 14, "air")
        wall = is_wall(dx, dz)
        corner = wall and abs(dx) + abs(dz) == R + R // 2 or (wall and (abs(dx) == R and abs(dz) == R // 2 or abs(dz) == R and abs(dx) == R // 2))
        if wall:
            pbox(s, s, t, t, 0, 3, "light_gray_concrete")
            put(s, t, 4, "white_concrete")
            put(s, t, 5, "white_concrete")
            for y in range(6, 10):
                put(s, t, y, "white_concrete" if corner else "glass")
            put(s, t, 10, "white_concrete")
        else:
            m = max(abs(dx), abs(dz))
            put(s, t, 4, "blue_concrete" if m == 3 else "smooth_quartz")
        # roof
        m = max(abs(dx), abs(dz))
        if octa(dx, dz, 3):
            put(s, t, 11, "glass" if not is_wall(dx, dz) or True else "white_concrete")
        else:
            put(s, t, 11, "sea_lantern" if (m == 5 and (dx + dz) % 3 == 0) else "white_concrete")
        if wall:
            put(s, t, 12, "white_concrete")
    # raised lantern over the centre (r=3 octagon walls y11..13, cap y14)
    for dx in range(-3, 4):
        for dz in range(-3, 4):
            if octa(dx, dz, 3):
                s, t = sc + dz, TC + dx
                edge = not all(octa(dx + a, dz + c, 3) for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if edge:
                    put(s, t, 11, "white_concrete"); put(s, t, 12, "light_blue_stained_glass"); put(s, t, 13, "light_blue_stained_glass")
                else:
                    put(s, t, 11, "air")
                put(s, t, 14, "white_concrete" if edge else ("sea_lantern" if dx == 0 and dz == 0 else "white_concrete"))
    # service doors in the base
    pbox(sc, sc, TC, TC, 0, 0, "light_gray_concrete")
    for ddz in (-R, R):
        pbox(sc + ddz, sc + ddz, TC, TC, 0, 2, "gray_concrete")
    # central kiosk: ring counter, display, pillar with signs
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            s, t = sc + dz, TC + dx
            m = max(abs(dx), abs(dz))
            if m == 2 and not (dx == 2 and dz == 0):
                put(s, t, 5, "smooth_quartz_slab[type=top]")
                if (dx + dz) % 2 == 0:
                    put(s, t, 6, ["potted_white_tulip", "brewing_stand", "potted_allium", "cake"][(dx * 3 + dz) % 4])
            elif m == 1:
                put(s, t, 5, "barrel[facing=up]" if (dx + dz) % 2 else "chiseled_bookshelf[facing=north]")
    pbox(sc, sc, TC, TC, 5, 10, "quartz_pillar")
    psign(sc, TC - 1, 8, [name, gates], "W")
    psign(sc, TC + 1, 8, [name, gates], "E")
    psign(sc + 1, TC, 8, [shops[0]], "N")
    psign(sc - 1, TC, 8, [shops[1]], "S")
    # gate seating (rows facing each other across aisles)
    for dx in range(-3, 2):
        t = TC + dx
        seat(sc + 5, t, 5, "S"); seat(sc + 3, t, 5, "N")
        seat(sc - 5, t, 5, "N"); seat(sc - 3, t, 5, "S")
    for dz in (-5, 5):
        put(sc + dz, TC + 2, 5, "potted_bamboo")
    # hanging lights
    for dx, dz in ((-4, 0), (4, 0), (0, 4), (0, -4)):
        put(sc + dz, TC + dx, 10, "lantern[hanging=true]")

    # ---- connector from the headhouse (east wall t-82, floor y8) down to the pod (floor y4) ----
    for dz in (-1, 0, 1):
        s = sc + dz
        put(s, -81, 7, "smooth_quartz_stairs[facing=west,half=bottom]")
        put(s, -80, 6, "smooth_quartz_stairs[facing=west,half=bottom]")
        put(s, -79, 5, "smooth_quartz_stairs[facing=west,half=bottom]")
        pbox(s, s, -81, -81, 4, 6, "white_concrete")
        pbox(s, s, -80, -80, 4, 5, "white_concrete")
        put(s, -79, 4, "white_concrete")
        pbox(s, s, -81, -81, 8, 10, "air"); pbox(s, s, -80, -80, 7, 10, "air"); pbox(s, s, -79, -79, 6, 10, "air")
    for t in (-81, -80, -79):
        for ss in (sc - 2, sc + 2):
            pbox(ss, ss, t, t, 4, 5, "white_concrete")
            pbox(ss, ss, t, t, 6, 10, "glass")
        pbox(sc - 2, sc + 2, t, t, 11, 11, "white_concrete")
    put(sc, -80, 11, "sea_lantern")
    for ss in (sc - 2, sc + 2):
        pbox(ss, ss, -80, -80, 0, 3, "light_gray_concrete")


def bridge(sc, t0, t1, door_s, gate):
    """3-wide walkable jet bridge along +t at plan s=sc from t0 to t1 (floor y4)."""
    for t in range(t0, t1 + 1):
        for s in (sc - 1, sc, sc + 1):
            put(s, t, 4, "light_gray_concrete")
            put(s, t, 7, "light_gray_concrete")
        for s in (sc - 1, sc + 1):
            put(s, t, 5, "light_gray_concrete")
            put(s, t, 6, "glass" if (t - t0) % 3 else "light_gray_concrete")
        put(sc, t, 5, "air"); put(sc, t, 6, "air")
    pbox(sc - 1, sc + 1, t1 + 1, t1 + 1, 4, 7, "gray_concrete")       # cab end
    pbox(door_s, door_s, t1, t1, 5, 6, "air")                         # aircraft door
    put(door_s, t1, 4, "black_concrete")
    for s in (sc - 1, sc + 1):                                        # drive column + wheels
        pbox(s, s, t1 - 1, t1 - 1, 1, 3, "gray_concrete")
        put(s, t1 - 1, 0, "black_concrete")
    put(sc, t0 + 1, 7, "sea_lantern")
    put(sc, t1 - 1, 7, "sea_lantern")


# B1 -> Delta (gate B42)
bridge(130, -66, -62, 129, "B42")
pbox(131, 131, -67, -67, 4, 7, "light_gray_concrete")
pbox(130, 130, -67, -67, 5, 6, "air")
# B2 -> Emirates (gate B51)
bridge(138, -68, -55, 137, "B51")
pbox(137, 137, -69, -69, 4, 7, "light_gray_concrete")
pbox(138, 138, -69, -69, 5, 6, "air")
# B3 -> Lufthansa (gate B62)
bridge(158, -66, -61, 157, "B62")
pbox(158, 158, -67, -67, 5, 6, "air")

# gate desks + gate signs
def desk(cells, sign_cell, lines, facing):
    for s, t in cells:
        put(s, t, 5, "polished_andesite")
        put(s, t, 6, "smooth_quartz_slab[type=bottom]")
    psign(sign_cell[0], sign_cell[1], 5, lines, facing)

desk([(128, -69), (129, -69)], (128, -70), ["Gate B42", "DL 117", "Paris CDG", "Boarding"], "W")
psign(130, -68, 8, ["GATE B42", "Delta"], "W")
desk([(140, -71), (141, -71)], (140, -72), ["Gate B51", "EK 202", "Dubai DXB", "On time"], "W")
psign(138, -70, 8, ["GATE B51", "Emirates"], "W")
desk([(160, -69), (161, -69)], (160, -70), ["Gate B62", "LH 403", "Frankfurt", "Boarding"], "W")
psign(158, -68, 8, ["GATE B62", "Lufthansa"], "W")
psign(161, -68, 7, ["Gate B60", "AS 33 Seattle", "Bus to remote", "stand"], "W")
