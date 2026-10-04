exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
# Rental car center: remove the 1x2 block "cars", link the counters to the rental decks in garage P-A.
CARS = {"white_concrete", "black_concrete", "gray_concrete", "light_gray_concrete", "red_concrete",
        "blue_concrete", "yellow_concrete", "green_concrete", "cyan_concrete", "orange_concrete"}
def name(s, t, y):
    x, z = P(s, t)
    return str(world_block(x, y, z)).replace("minecraft:", "").split("[")[0]
n = 0
for s in range(32, 50):
    for t in (-141, -140, -138, -137):             # return lanes: cars were inlaid in the floor (y 0)
        if name(s, t, 0) in CARS - {"light_gray_concrete"}:
            put(s, t, 0, "light_gray_concrete"); n += 1
    for t in (-141, -140, -137, -136, -133, -132):  # ready deck (walk y 6)
        if name(s, t, 6) in CARS:
            put(s, t, 6, "air"); n += 1
for s in range(33, 37):                             # apron "ready" cars
    for t in (-126, -125):
        if name(s, t, 0) in CARS:
            put(s, t, 0, "air"); n += 1
print("removed car blocks:", n)
# walkway RCC north wall (s 50) -> garage P-A south wall (s 54), plan t -137..-136
for t in (-137, -136):
    put(50, t, 1, "air"); put(50, t, 2, "air")
    put(51, t, 0, "smooth_stone_slab[type=bottom]")
    put(54, t, 0, "air")
rect(51, 53, -137, -136, -1, "smooth_stone")
for s in (51, 53):
    put(s, -138, 0, "stone_brick_wall"); put(s, -138, 1, "lantern[hanging=false]")
x, z = P(49, -139); b.sign(x, 2, z, ["RENTAL CARS", "pick-up & return", "Garage P-A", "levels 1-6  ->"], facing="south")
x, z = P(52, -135); b.sign(x, 0, z, ["Rental counters", "v  this way", "Rental cars", "^  P-A L1-L6"], facing="east", wall=False)
x, z = P(55, -138); b.sign(x, 1, z, ["Rental Car", "Center", "counters", "v (south)"], facing="north")
