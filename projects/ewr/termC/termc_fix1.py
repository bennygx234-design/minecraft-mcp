exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
# Fix round 1: doorway from the AirTrain station into the skybridge + arrivals-hall furnishing.
CS, CT, R = 200.0, -53.0, 44.0


def dd(s, t):
    return math.hypot(s - CS, t - CT)


# doorway through the station's east glass wall (t=-100) into the Terminal C skybridge
for s in (183, 184, 185):
    for y in (9, 10):
        put(s, -100, y, "air")

# arrivals hall (feet y=0): benches along the inner side of the facade, info desk, rental counters
for s in range(176, 225):
    for t in range(-100, -78):
        dv = dd(s, t)
        if 40.5 <= dv < 41.5 and s % 4 in (1, 2) and not (191 <= s <= 197 or 203 <= s <= 209) and s not in (178, 179, 186, 187, 214, 215, 222, 223):
            x, z = P(s, t)
            b.chair(x, 0, z, "east", "birch_stairs")
# information desk between the stairs
for s in range(199, 202):
    put(s, -89, 0, "smooth_quartz")
put(200, -90, 0, "light_blue_concrete")
x, z = P(200, -89)
b.sign(x, 1, z, ["Information", "Terminal C", "", ""], facing="west", wall=False, wood="birch")
# rental-car / ground transport counters at the two ends of the hall
for s0, lbl in ((176, "Rental Cars"), (224, "Rideshare")):
    for t in range(-86, -81):
        put(s0, t, 0, "smooth_quartz")
        put(s0, t, 1, "air")
    x, z = P(s0, -84)
    b.sign(x, 1, z, [lbl, "AirTrain ->", "", ""], facing="north" if s0 < 200 else "south", wall=False,
           wood="birch")
# plants + lanterns in arrivals
for s in (190, 198, 202, 210):
    x, z = P(s, -79)
    b.plant(x, 0, z, "potted_bamboo")
for s in range(178, 224, 6):
    for t in (-90, -84, -78):
        if dd(s, t) < 43 and t < -78:
            x, z = P(s, t)
            b.set(x, 4, z, "lantern[hanging=true]")
# departures: self-service kiosks in front of the counter arc, a few planters
for s in range(179, 225, 7):
    for t in range(-100, -78):
        if 41.5 <= dd(s, t) < 42.5:
            x, z = P(s, t)
            b.set(x, 6, z, "polished_andesite")
            b.set(x, 7, z, "stone_button[face=floor]")
            break
