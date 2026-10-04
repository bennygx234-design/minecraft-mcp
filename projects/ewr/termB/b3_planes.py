exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\termB\lib.py").read())
# ---- Terminal B apron: parked international aircraft + stand markings + ground equipment ----


def rplane(v, livery, L=7, span=5):
    """regional-jet sized copy of kit.plane (E175 / CRJ class)."""
    tail, accent = LIVERIES[livery]
    body = "white_concrete"
    v.box(-1, 1, -L, 1, 3, L, body)
    v.box(-1, 1, -L, 1, 1, L, "light_gray_concrete")
    v.box(-1, 4, -L + 2, 1, 4, L - 3, "smooth_quartz_slab[type=bottom]")
    for z in range(-L + 3, L - 3, 2):
        v.set(-1, 3, z, "light_blue_stained_glass"); v.set(1, 3, z, "light_blue_stained_glass")
    v.box(-1, 2, -L + 3, -1, 2, L - 4, accent); v.box(1, 2, -L + 3, 1, 2, L - 4, accent)
    v.box(-1, 3, -L, 1, 3, -L, "black_stained_glass")
    v.set(0, 2, -L - 1, body); v.set(0, 3, -L - 1, body)
    for i in range(1, span + 1):
        sw = i // 3
        for z in range(-1 + sw, 2 + sw - (1 if i > span - 2 else 0)):
            v.set(-1 - i, 2, z, body); v.set(1 + i, 2, z, body)
    v.set(-1 - span, 3, span // 3 + 1, tail); v.set(1 + span, 3, span // 3 + 1, tail)
    # rear-mounted engines (regional jet look)
    for ex in (-2, 2):
        v.box(ex, 3, L - 5, ex, 3, L - 3, "light_gray_concrete")
    for k in range(4):
        v.box(0, 4 + k, L - 3 + k // 2, 0, 4 + k, L, tail)
    v.box(-3, 7, L - 1, 3, 7, L, body)          # T-tail
    v.set(0, 0, -L + 2, "black_concrete"); v.set(-1, 0, 1, "black_concrete"); v.set(1, 0, 1, "black_concrete")


# stand lead-in lines (yellow) + stop bars, painted on the apron (y=-1)
for s, tn, tt in ((127, -66, -50), (135, -66, -28), (155, -66, -30), (159, -46, -28)):
    rect(s, s, tn, tt, -1, "yellow_concrete")
for s, tn in ((127, -64), (135, -57), (155, -64), (159, -41)):
    rect(s - 2, s + 2, tn, tn, -1, "yellow_concrete")
# stand numbers
for s, t, txt in ((124, -66, "B42"), (131, -66, "B51"), (151, -66, "B62"), (163, -46, "B60")):
    pass

# aircraft (all nose-in toward the satellites, i.e. nose to plan -t: rot=3)
plane(at(135, -42, 0, rot=3), "emirates", big=True)   # Emirates widebody at B51 (pod B2)
plane(at(155, -54, 0, rot=3), "lufthansa")            # Lufthansa at B62 (pod B3)
rplane(at(127, -57, 0, rot=3), "delta")               # Delta Connection regional at B42 (pod B1)
rplane(at(159, -34, 0, rot=3), "alaska")              # Alaska E175 on remote stand B60

# Alaska remote stand: mobile stairs + apron bus
for k, s in enumerate((163, 162, 161)):
    put(s, -39, k, "smooth_quartz_stairs[facing=south,half=bottom]")
    for y in range(0, k):
        put(s, -39, y, "white_concrete")
    put(s, -40, k + 1, "iron_bars")
put(164, -39, 0, "yellow_concrete"); put(164, -40, 0, "yellow_concrete")
pbox(164, 165, -48, -43, 0, 1, "blue_concrete")
pbox(164, 165, -47, -44, 1, 1, "light_blue_stained_glass")
pbox(164, 165, -48, -43, 2, 2, "white_concrete")

# baggage train beside the Emirates jet (clear of wings/engines)
for t in (-52, -50, -48):
    put(140, t, 0, "iron_trapdoor[half=top]" if False else "light_gray_concrete")
    put(140, t, 1, {"blue_shulker_box": 1, "red_shulker_box": 1, "gray_shulker_box": 1})
put(140, -54, 0, "yellow_concrete"); put(140, -54, 1, "black_stained_glass")
# catering truck at the Lufthansa rear door
pbox(150, 151, -47, -45, 0, 1, "white_concrete")
pbox(150, 151, -47, -46, 2, 3, "white_concrete")
put(150, -44, 0, "orange_concrete"); put(151, -44, 0, "orange_concrete")
# fuel truck near the Delta regional
pbox(122, 122, -49, -45, 0, 1, "red_concrete")
put(122, -44, 0, "white_concrete"); put(122, -44, 1, "black_stained_glass")
