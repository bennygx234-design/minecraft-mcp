exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
# light the enclosed pod bases (y0..3) so nothing spawns, and stand-number signs on the stop bars
for sc in (127, 143, 158):
    for ds, dt in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
        put(sc + ds, -73 + dt, 3, "sea_lantern")
