# Move the maintenance stand out of the taxi path; clear x 161..162 across z 54..87 (world origin 0,64,0)
b.box(161, 0, 54, 162, 6, 87, "air")                 # old stand, stairs, extinguishers
b.box(161, 0, 88, 162, 4, 89, "air") if False else None
for z in range(66, 80):                               # restore floor under the old stand
    b.set(161, -1, z, "light_gray_concrete"); b.set(162, -1, z, "light_gray_concrete")
b.set(161, -1, 70, "yellow_concrete"); b.set(162, -1, 70, "yellow_concrete")
# new stand against the north wall: stairs x 163..166, deck x 167..169, z 50..51 (deck top y=4)
b.stairs_run(163, 0, 50, "east", 4, "polished_andesite_stairs", width=2, support="yellow_concrete")
b.box(167, 3, 50, 169, 3, 51, "smooth_stone_slab[type=top]")
for x in (167, 169):
    for z in (50, 51):
        b.box(x, 0, z, x, 2, z, "yellow_concrete")
b.box(167, 4, 52, 169, 4, 52, "iron_bars") if False else None
b.box(163, 4, 52, 169, 4, 52, "air")
b.box(170, 4, 50, 170, 4, 51, "iron_bars")
b.box(167, 4, 51, 169, 4, 51, "air")
b.set(169, 4, 50, "lantern")
# fire extinguishers moved beside the door, outside the path
b.set(162, 0, 52, "red_concrete"); b.set(162, 1, 52, "red_concrete_powder")
b.set(162, 0, 88, "red_concrete"); b.set(162, 1, 88, "red_concrete_powder")
