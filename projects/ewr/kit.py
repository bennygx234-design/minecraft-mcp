# Shared helpers for every Newark (EWR) build script. Start each script with:
#     exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
# Frame: plan coords (s, t): s = blocks north of the runway 04L threshold, t = blocks east of the 04L
# centreline. Builder coords: x = t, z = -s, y = 0 is the walking level (ground surface blocks are y = -1).
# The build origin is always (60, 64, 310) in the world.


def P(s, t):
    """plan (s, t) -> builder (x, z)"""
    return int(round(t)), int(round(-s))


def put(s, t, y, block, nbt=None):
    x, z = P(s, t)
    b.set(x, y, z, block, nbt)


def rect(s1, s2, t1, t2, y, block):
    """filled plan rectangle at height y"""
    b.box(int(round(t1)), y, int(round(-s2)), int(round(t2)), y, int(round(-s1)), block)


def pbox(s1, s2, t1, t2, y1, y2, block, hollow=False):
    """3-D box in plan coords"""
    b.box(int(round(t1)), y1, int(round(-s2)), int(round(t2)), y2, int(round(-s1)), block, hollow=hollow)


def at(s, t, y=0, rot=0):
    """child view at plan (s, t). rot = quarter turns clockwise; a view's local north (-z) is plan +s."""
    x, z = P(s, t)
    return b.at(x, y, z, rot)


LIVERIES = {
    "united": ("blue_concrete", "light_blue_concrete"), "delta": ("red_concrete", "blue_concrete"),
    "american": ("gray_concrete", "red_concrete"), "jetblue": ("blue_concrete", "cyan_concrete"),
    "alaska": ("cyan_concrete", "blue_concrete"), "spirit": ("yellow_concrete", "black_concrete"),
    "fedex": ("purple_concrete", "orange_concrete"), "ups": ("brown_concrete", "yellow_concrete"),
    "lufthansa": ("blue_concrete", "yellow_concrete"), "emirates": ("red_concrete", "white_concrete"),
}


def plane(v, livery="united", big=False):
    """Airliner centred on view v at ground level, nose pointing to the view's local north (-z).
    ~23 long, 21 wingspan (big=True: ~31 long, 29 span). Turn it with at(..., rot=...)."""
    tail, accent = LIVERIES.get(livery, LIVERIES["united"])
    L = 15 if big else 11          # half length
    span = 14 if big else 10       # half span
    body = "white_concrete"
    # fuselage: 3 wide, y 1..3, rounded with slabs on top
    v.box(-1, 1, -L, 1, 3, L, body)
    v.box(-1, 1, -L, 1, 1, L, "light_gray_concrete")                     # belly
    v.box(-1, 4, -L + 2, 1, 4, L - 3, "smooth_quartz_slab[type=bottom]")  # crown
    for z in range(-L + 3, L - 3, 2):
        v.set(-1, 3, z, "light_blue_stained_glass"); v.set(1, 3, z, "light_blue_stained_glass")
    v.box(-1, 2, -L + 3, -1, 2, L - 4, accent); v.box(1, 2, -L + 3, 1, 2, L - 4, accent)   # cheat line
    v.box(-1, 3, -L, 1, 3, -L, "black_stained_glass")                    # cockpit
    v.set(0, 2, -L - 1, body); v.set(0, 3, -L - 1, "white_concrete")     # nose
    # wings: swept back, y = 2
    for i in range(1, span + 1):
        sweep = i // 3
        for z in range(-1 + sweep, 2 + sweep - (1 if i > span - 3 else 0)):
            v.set(-1 - i, 2, z, body); v.set(1 + i, 2, z, body)
    v.set(-1 - span, 3, span // 3 + 1, tail); v.set(1 + span, 3, span // 3 + 1, tail)      # winglets
    # engines under the wings
    for ex in (-(span // 2 + 1), span // 2 + 1):
        v.box(ex, 1, -2, ex, 1, 0, "light_gray_concrete")
        v.set(ex, 1, -3, "gray_concrete")
    # tail: vertical fin + stabilisers
    for k in range(5):
        v.box(0, 4 + k, L - 4 + k // 2, 0, 4 + k, L, tail)
    v.box(-4, 4, L - 1, 4, 4, L, body)
    # landing gear
    v.set(0, 0, -L + 2, "black_concrete"); v.set(-2, 0, 1, "black_concrete"); v.set(2, 0, 1, "black_concrete")


def jet_bridge(s, t, length, direction, y=4):
    """Covered jet bridge from a terminal wall at plan (s, t) running `length` blocks in plan
    direction ('+t','-t','+s','-s'), floor at y."""
    ds, dt = {"+t": (0, 1), "-t": (0, -1), "+s": (1, 0), "-s": (-1, 0)}[direction]
    for k in range(length):
        ss, tt = s + ds * k, t + dt * k
        put(ss, tt, y, "light_gray_concrete")
        put(ss, tt, y + 1, "glass_pane" if k % 2 else "light_gray_concrete")
        put(ss, tt, y + 2, "smooth_stone_slab[type=bottom]")
        if k == length - 1:
            for yy in range(0, y):
                put(ss, tt, yy, "iron_bars")
