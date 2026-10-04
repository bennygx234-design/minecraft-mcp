# EWR Cars dealership showroom. Builder origin = world (88, 71, -86): local x = wx-88, y = wy-71, z = wz+86.
# Building x 90..111, z -85..-72 (local x 2..23, z 1..14), floor block y=71 (walk y=72).
# Forecourt x 90..111, z -71..-66 (local z 15..20); apron/driveway x 88..89, z -84..-66 (local x 0..1, z 2..20).
X1, X2, Z1, Z2 = 2, 23, 1, 14
H = 7                       # roof slab at local y=7 (world 78)

# ---- ground work: foundation + level pad -------------------------------------------------------
b.box(0, -4, 1, 25, -1, 21, 'stone')
b.box(X1, -1, Z1, X2, -1, Z2, 'polished_andesite')          # skirt row under the walls (shows on the low east side)
b.box(0, 1, 1, 25, 12, 21, 'air')                         # clear grass/plants above the pad
# apron + driveway (dark asphalt, white edge) and the forecourt
b.box(0, 0, 2, 1, 0, 20, 'gray_concrete')
b.box(0, 0, 2, 1, 0, 2, 'white_concrete'); b.box(0, 0, 5, 1, 0, 5, 'white_concrete')   # driveway edge marks
b.box(2, 0, 15, 25, 0, 20, 'smooth_stone')
b.box(2, 0, 15, 25, 0, 15, 'polished_andesite')
for x in range(4, 24, 6):                                 # parking bay lines
    b.box(x, 0, 17, x, 0, 20, 'white_concrete')
b.box(24, 0, 1, 25, 0, 21, 'grass_block'); b.box(0, 0, 21, 25, 0, 21, 'grass_block')
for (px, pz) in [(25, 3), (25, 9), (25, 14), (25, 20), (2, 21), (12, 21), (22, 21)]:
    b.set(px, 1, pz, 'azalea_leaves[persistent=true]')

# ---- shell -----------------------------------------------------------------------------------
b.box(X1, 0, Z1, X2, 0, Z2, 'smooth_quartz')               # polished floor
for x in range(X1 + 1, X2, 3):                            # subtle floor grid
    b.box(x, 0, Z1 + 1, x, 0, Z2 - 1, 'white_concrete')
for z in range(Z1 + 1, Z2, 3):
    b.box(X1 + 1, 0, z, X2 - 1, 0, z, 'white_concrete')
b.box(X1, 1, Z1, X2, H - 1, Z2, 'glass', hollow=True)      # curtain walls
b.box(X1 + 1, 1, Z1 + 1, X2 - 1, H - 1, Z2 - 1, 'air')
# black mullions every 4-5 blocks + corner posts + transom
for x in (X1, 7, 12, 17, X2):
    b.box(x, 1, Z1, x, H - 1, Z1, 'black_concrete'); b.box(x, 1, Z2, x, H - 1, Z2, 'black_concrete')
for z in (Z1, 5, 10, Z2):
    b.box(X1, 1, z, X1, H - 1, z, 'black_concrete'); b.box(X2, 1, z, X2, H - 1, z, 'black_concrete')
b.box(X1, 5, Z1, X2, 5, Z2, 'black_concrete', hollow=True)
b.box(X1 + 1, 5, Z1 + 1, X2 - 1, 5, Z2 - 1, 'air')
# base kerb inside the glass
# roof: white slab with fascia band (black) that carries the brand sign
b.box(X1 - 1, H, Z1 - 1, X2 + 1, H, Z2 + 1, 'smooth_quartz')
b.box(X1 - 1, H, Z1 - 1, X2 + 1, H + 1, Z2 + 1, 'black_concrete', hollow=True)
b.box(X1, H + 1, Z1, X2, H + 1, Z2, 'air')
b.box(X1, H + 1, Z1, X2, H + 1, Z2, 'smooth_quartz_slab')
for x in range(X1 + 3, X2 - 2, 4):                        # skylight strips
    b.box(x, H, Z1 + 2, x + 1, H, Z2 - 2, 'glass')
    b.box(x, H + 1, Z1 + 2, x + 1, H + 1, Z2 - 2, 'air')
# ceiling lights: froglight panels + end-rod spotlights over each car
for x in range(X1 + 2, X2 - 1, 3):
    for z in (Z1 + 2, Z1 + 6, Z1 + 10):
        if b.get(x, H, z) and 'glass' in str(b.get(x, H, z)):
            continue
        b.set(x, H, z, 'pearlescent_froglight')
# entrance: drive-through opening on the west face (z -84..-81 = local 2..5), 3 tall
b.box(X1, 1, 2, X1, 3, 5, 'air')
b.box(X1, 4, 2, X1, 4, 5, 'black_concrete')
b.box(X1 - 1, 0, 2, X1, 0, 5, 'polished_andesite')
# pedestrian doors to the forecourt (south face)
b.box(11, 1, Z2, 13, 3, Z2, 'air')
b.box(11, 1, Z2, 11, 3, Z2, 'air')
# canopy over the south doors
b.box(10, 4, Z2 + 1, 14, 4, Z2 + 2, 'smooth_quartz_slab[type=top]')

# ---- interior ------------------------------------------------------------------------------
# turntable podiums (dark, quartz ring) - cars park on top of the slabs
def podium(cx, cz, r=2.1):
    b.cylinder(cx, 0, cz, r + 0.7, 1, "polished_diorite")
    b.cylinder(cx, 1, cz, r, 1, 'polished_blackstone_slab')
for cx in (6, 12, 18):
    podium(cx, 9)
podium(10, 4, 2.1)
# spotlights over the cars (end rods hanging from the ceiling)
for (cx, cz) in [(6, 9), (12, 9), (18, 9), (10, 4)]:
    for dx, dz in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        b.set(cx + dx, H - 1, cz + dz, 'end_rod[facing=down]')
# reception desk + lounge in the NE corner
b.box(17, 1, 2, 22, 1, 2, 'white_concrete'); b.box(17, 1, 2, 17, 1, 4, 'white_concrete')
b.box(17, 2, 2, 22, 2, 2, 'smooth_quartz_slab'); b.box(17, 2, 2, 17, 2, 4, 'smooth_quartz_slab')
b.box(18, 1, 2, 22, 1, 2, 'red_concrete')
for z in (4, 5):
    b.set(22, 1, z, 'polished_blackstone_stairs[facing=west]')    # lounge chairs
b.set(20, 1, 4, 'black_wool'); b.set(20, 1, 5, 'black_wool')        # ottomans
b.set(21, 1, 4, 'glass'); b.set(21, 1, 5, 'glass')                  # coffee table
b.set(21, 2, 4, 'potted_flowering_azalea_bush')
b.set(19, 1, 3, 'polished_blackstone_stairs[facing=north]')         # receptionist chair
for (px, pz) in [(3, 13), (22, 13), (16, 2), (3, 6)]:
    b.set(px, 1, pz, 'potted_bamboo')
# brand wall on the north side: red (Ferrari) and yellow/gold (Lamborghini) panels with lamps
b.box(3, 1, 1, 7, 4, 1, 'red_concrete')
b.box(12, 1, 1, 16, 4, 1, 'yellow_concrete')
b.box(4, 2, 1, 6, 3, 1, 'black_concrete'); b.set(5, 3, 1, 'yellow_concrete')   # stylised shield
b.box(13, 2, 1, 15, 3, 1, 'black_concrete'); b.set(14, 2, 1, 'gold_block')     # stylised bull shield
b.sign(5, 1, 2, ['FERRARI', 'Rosso Corsa'], facing='south', wall=True)
b.sign(14, 1, 2, ['LAMBORGHINI', 'Automobili'], facing='south', wall=True)
# information plaques in front of the south-row cars
# exterior lighting on the forecourt
for x in (4, 12, 20):
    b.set(x, 1, 20, 'polished_blackstone_wall'); b.set(x, 2, 20, 'polished_blackstone_wall'); b.set(x, 3, 20, 'sea_lantern')
print('ok')
