# Walled stone manor: great hall, two wings, four towers, courtyard fountain, gardens.
# Run through the `build` tool. Origin = south-west corner of the site at courtyard floor level.
# Footprint 53 x 45 (x 0..52, z 0..44); the gate is in the south wall.

W, D = 52, 44
STONE = {"stone_bricks": 7, "cracked_stone_bricks": 1, "mossy_stone_bricks": 2}
FRAME = "dark_oak_log"
ROOF = "deepslate_tile_stairs"

# ---- site prep: clear terrain/trees above, solid footing below ----------------
b.clear(-2, 0, -2, W + 2, 30, D + 2)
b.box(-2, -6, -2, W + 2, -2, D + 2, "dirt")
b.box(-2, -1, -2, W + 2, -1, D + 2, "grass_block")

# ---- curtain wall with crenellations and a gatehouse -------------------------
b.walls(0, 0, 0, W, 4, D, STONE)
for i in range(0, W + 1, 2):
    b.set(i, 5, 0, "stone_brick_wall"); b.set(i, 5, D, "stone_brick_wall")
for i in range(0, D + 1, 2):
    b.set(0, 5, i, "stone_brick_wall"); b.set(W, 5, i, "stone_brick_wall")
gx = W // 2
b.clear(gx - 2, 0, D, gx + 2, 3, D)
b.box(gx - 3, 4, D - 1, gx + 3, 6, D + 1, STONE)          # gate arch
b.box(gx - 2, 0, D + 1, gx + 2, 0, D + 1, "polished_andesite")
for dx in (-3, 3):
    b.lamp(gx + dx, 7, D + 1)                              # lanterns on top of the arch
b.set(gx - 4, 3, D + 1, "red_wall_banner[facing=south]")
b.set(gx + 4, 3, D + 1, "red_wall_banner[facing=south]")

# ---- corner towers ------------------------------------------------------------
def tower(v):
    """Round tower centred on the view origin, 13 tall with a stepped slate cone."""
    v.cylinder(0, 0, 0, 4, 13, STONE, hollow=True)
    v.cylinder(0, 0, 0, 3, 1, "spruce_planks")
    v.cylinder(0, 6, 0, 3, 1, "spruce_planks")
    v.cylinder(0, 12, 0, 3, 1, "spruce_planks")
    for y in (3, 9):
        for x, z in ((4, 0), (-4, 0), (0, 4), (0, -4)):
            v.set(x, y, z, "iron_bars")                    # arrow slits
    for k in range(7):
        v.cylinder(0, 13 + k, 0, 5 - k * 0.75, 1, "deepslate_tiles", hollow=True)
    v.set(0, 20, 0, "lightning_rod")
    v.lamp(0, 5, 0, hanging=True); v.lamp(0, 11, 0, hanging=True)
    v.ladder(0, 1, 2, 12, "north")
    v.set(0, 6, 2, "ladder[facing=north]"); v.set(0, 12, 2, "ladder[facing=north]")

for cx, cz in ((2, 2), (W - 2, 2), (2, D - 2), (W - 2, D - 2)):
    tower(b.at(cx, 0, cz))
    b.clear(cx, 1, cz + (1 if cz < D / 2 else -1), cx, 2, cz + (1 if cz < D / 2 else -1))

# ---- great hall (north) --------------------------------------------------------
hx1, hz1, hx2, hz2 = 12, 4, 40, 18
b.room(hx1, 0, hz1, hx2, 11, hz2, STONE)
b.frame(hx1, 0, hz1, hx2, 11, hz2, FRAME)
for x in range(hx1 + 4, hx2, 4):                            # buttress beams
    b.box(x, 0, hz2, x, 11, hz2, FRAME + "[axis=y]")
    b.box(x, 0, hz1, x, 11, hz1, FRAME + "[axis=y]")
b.floor(hx1 + 1, hz1 + 1, hx2 - 1, hz2 - 1, 0, {"polished_andesite": 3, "andesite": 1})
b.floor(hx1 + 1, hz1 + 1, hx2 - 1, hz2 - 1, 6, "spruce_planks")       # upper floor
for x in range(hx1 + 2, hx2 - 1, 4):                                   # tall windows
    for z in (hz1, hz2):
        b.window(x, 2, z, x + 1, 4, z, "glass_pane")
        b.window(x, 8, z, x + 1, 9, z, "glass_pane")
b.hip_roof(hx1, hz1, hx2, hz2, 12, ROOF, overhang=1, top="deepslate_tile_slab")
# entrance
ex = (hx1 + hx2) // 2
b.clear(ex - 1, 1, hz2, ex + 1, 3, hz2)
b.double_door(ex - 1, 1, hz2, "north", "dark_oak_door")
b.door(ex + 1, 1, hz2, "north", "dark_oak_door", hinge="right")
b.stairs_run(ex - 1, 0, hz2 + 1, "north", 1, "stone_brick_stairs", width=3)
b.set(ex - 2, 3, hz2 + 1, "wall_torch[facing=south]"); b.set(ex + 2, 3, hz2 + 1, "wall_torch[facing=south]")

# great hall interior (ground floor): banquet tables, carpet runner, throne, fireplace, chandeliers
b.carpet(ex - 1, hz1 + 3, ex + 1, hz2 - 1, 1, "red")
for tz in (hz1 + 4, hz2 - 4):
    b.long_table(hx1 + 4, tz, ex - 3, tz, 1, "dark_oak_slab")
    b.long_table(ex + 3, tz, hx2 - 4, tz, 1, "dark_oak_slab")
    for x in list(range(hx1 + 4, ex - 2)) + list(range(ex + 3, hx2 - 3)):
        b.chair(x, 1, tz - 1, "south", "spruce_stairs")
        b.chair(x, 1, tz + 1, "north", "spruce_stairs")
        if x % 3 == 0:
            b.set(x, 2, tz, "candle[candles=3,lit=true]")
# dais + throne at the north wall
b.box(ex - 2, 1, hz1 + 1, ex + 2, 1, hz1 + 2, "polished_deepslate")
b.chair(ex, 2, hz1 + 1, "south", "quartz_stairs")
b.set(ex - 1, 2, hz1 + 1, "gold_block"); b.set(ex + 1, 2, hz1 + 1, "gold_block")
b.set(ex - 1, 3, hz1 + 1, "lantern"); b.set(ex + 1, 3, hz1 + 1, "lantern")
for dx in (-3, 3):
    b.set(ex + dx, 3, hz1 + 1, "red_wall_banner[facing=south]")
# fireplace on the west wall
b.box(hx1 + 1, 1, 9, hx1 + 1, 4, 13, "bricks")
b.clear(hx1 + 1, 1, 10, hx1 + 1, 2, 12)
b.set(hx1 + 1, 1, 11, "campfire[facing=east,lit=true]")
b.set(hx1 + 1, 1, 10, "iron_bars"); b.set(hx1 + 1, 1, 12, "iron_bars")
b.box(hx1 + 1, 5, 10, hx1 + 1, 11, 12, "bricks")                       # chimney
# chandeliers
for x in range(hx1 + 6, hx2 - 3, 8):
    for z in (hz1 + 5, hz2 - 5):
        b.set(x, 5, z, "iron_chain[axis=y]")
        b.set(x, 4, z, "lantern[hanging=true]")
# staircase to the upper floor along the east wall
b.stairs_run(hx2 - 1, 1, hz2 - 1, "north", 5, "spruce_stairs", width=1)
b.clear(hx2 - 1, 6, hz2 - 6, hx2 - 1, 6, hz2 - 2)
b.set(hx2 - 2, 6, hz2 - 2, "spruce_fence")

# upper floor: library (west) and lord's bedroom (east), divided by a wall with a door
b.walls(ex, 7, hz1 + 1, ex, 10, hz2 - 1, "spruce_planks")
b.door(ex, 7, hz1 + 7, "east", "spruce_door")
b.bookshelves(hx1 + 1, 7, hz1 + 1, ex - 1, 9, hz1 + 1)
b.bookshelves(hx1 + 1, 7, hz1 + 2, hx1 + 1, 9, hz2 - 1)
b.set(hx1 + 6, 7, hz1 + 7, "enchanting_table")
b.set(hx1 + 9, 7, hz1 + 5, "lectern[facing=south]")
b.long_table(hx1 + 4, hz2 - 4, hx1 + 8, hz2 - 4, 7, "spruce_slab")
for x in range(hx1 + 4, hx1 + 9):
    b.chair(x, 7, hz2 - 3, "north", "oak_stairs")
b.carpet(hx1 + 3, hz1 + 3, ex - 2, hz2 - 6, 7, "green")
for x in range(hx1 + 3, ex, 5):
    b.lamp(x, 10, hz1 + 7, hanging=True)
b.bed(ex + 6, 7, hz1 + 3, "north", "purple")
b.bed(ex + 7, 7, hz1 + 3, "north", "purple")
b.chest(ex + 3, 7, hz1 + 1, "south", [("diamond", 3), ("gold_ingot", 12)], double=True)
b.carpet(ex + 3, hz1 + 5, hx2 - 3, hz2 - 3, 7, "purple", border="black")
for x in (ex + 3, hx2 - 2):
    b.barrel(x, 7, hz2 - 1, "up"); b.barrel(x, 8, hz2 - 1, "up")
b.lamp(hx2 - 2, 7, hz1 + 2)
b.lamp(ex + 6, 10, hz1 + 8, hanging=True)
b.plant(ex + 2, 7, hz1 + 2, "potted_flowering_azalea_bush")

# ---- wings (west: kitchen + storage; east: guest quarters) ---------------------
def wing(v, kind):
    """Wing in its own frame: x 6..16, z 18..36, door on the courtyard (east) side."""
    x1, z1, x2, z2 = 6, 19, 16, 37
    v.room(x1, 0, z1, x2, 6, z2, STONE)
    v.frame(x1, 0, z1, x2, 6, z2, FRAME)
    v.floor(x1 + 1, z1 + 1, x2 - 1, z2 - 1, 0, "spruce_planks")
    for z in range(z1 + 2, z2 - 1, 4):
        v.window(x1, 2, z, x1, 3, z + 1, "glass_pane")
        v.window(x2, 2, z, x2, 3, z + 1, "glass_pane")
    v.gable_roof(x1, z1, x2, z2, 7, "spruce_stairs", ridge="z", overhang=1, gable=STONE)
    dz = (z1 + z2) // 2
    v.clear(x2, 1, dz, x2, 2, dz)
    v.door(x2, 1, dz, "west", "spruce_door")
    v.set(x2 + 1, 3, dz - 1, "wall_torch[facing=east]"); v.set(x2 + 1, 3, dz + 1, "wall_torch[facing=east]")
    for z in range(z1 + 3, z2 - 1, 5):
        v.lamp(x1 + 5, 5, z, hanging=True)
    if kind == "kitchen":
        v.kitchen(x1 + 1, 1, z2 - 1, "north", length=5)
        v.box(x1 + 1, 1, z2 - 3, x1 + 1, 1, z2 - 2, "smooth_stone_slab[type=top]")
        v.set(x1 + 1, 1, z2 - 4, "brewing_stand")
        v.long_table(x1 + 3, z2 - 6, x1 + 6, z2 - 5, 1, "oak_slab")
        for x in range(x1 + 3, x1 + 7):
            v.chair(x, 1, z2 - 7, "south"); v.chair(x, 1, z2 - 4, "north")
        # storage half
        for z in range(z1 + 1, z1 + 8):
            v.barrel(x1 + 1, 1, z, "east", [("wheat", 32), ("carrot", 16)] if z % 2 else None)
            v.barrel(x1 + 1, 2, z, "east")
        v.chest(x1 + 3, 1, z1 + 1, "south", [("iron_ingot", 20), ("coal", 48)], double=True)
        v.chest(x1 + 6, 1, z1 + 1, "south", [("oak_log", 64)], double=True)
        v.set(x1 + 4, 1, z1 + 5, "anvil[facing=east]")
        v.set(x1 + 6, 1, z1 + 5, "grindstone[face=floor,facing=east]")
        v.set(x1 + 8, 1, z1 + 1, "crafting_table")
        v.set(x1 + 9, 1, z1 + 1, "smithing_table")
    else:
        for i, z in enumerate(range(z1 + 2, z2 - 1, 4)):
            v.bed(x1 + 1, 1, z, "west", ["light_blue", "lime", "yellow", "pink"][i % 4])
            v.table(x1 + 1, 1, z + 1, "spruce_fence", "potted_cornflower")
            v.chest(x1 + 4, 1, z, "west")
            v.carpet(x1 + 2, z, x1 + 3, z + 1, 1, "white")
        v.sofa(x2 - 1, 1, z1 + 2, "west", length=4, seat="spruce_stairs", arm="spruce_trapdoor")
        v.table(x2 - 3, 1, z1 + 3)

wing(b, "kitchen")
wing(b.at(W, 0, 56, rot=2), "quarters")    # 180 deg: x -> W - x, z -> 56 - z

# ---- courtyard -----------------------------------------------------------------
cx1, cz1, cx2, cz2 = 18, 20, 34, 42
b.floor(cx1, cz1, cx2, cz2, -1, {"stone_bricks": 5, "andesite": 2, "cobblestone": 1})
b.floor(gx - 1, cz1, gx + 1, D, -1, "polished_andesite")          # processional path
b.floor(ex - 1, hz2 + 2, ex + 1, cz1, -1, "polished_andesite")
fz = 31
# Square basin: water only spreads orthogonally, so a solid, edge-connected rim keeps it in.
b.box(gx - 4, -2, fz - 4, gx + 4, -1, fz + 4, "stone_bricks")
b.walls(gx - 4, 0, fz - 4, gx + 4, 0, fz + 4, "chiseled_stone_bricks")
b.box(gx - 3, 0, fz - 3, gx + 3, 0, fz + 3, "water")
b.box(gx, 0, fz, gx, 2, fz, "chiseled_stone_bricks")
b.set(gx, 3, fz, "water")                      # spills one block out and falls back into the basin
for dx, dz in ((-4, -4), (4, -4), (-4, 4), (4, 4)):
    b.set(gx + dx, 1, fz + dz, "stone_brick_wall"); b.set(gx + dx, 2, fz + dz, "lantern")
for dx, dz in ((-6, -6), (6, -6), (-6, 6), (6, 6)):
    b.lamp(gx + dx, 0, fz + dz, post="dark_oak_fence")
    b.set(gx + dx, 2, fz + dz, "lantern")
# gardens along the inner wall: hedges, flowers, trees
for x1, x2 in ((7, 16), (36, 45)):
    b.box(x1, 0, D - 6, x2, 0, D - 6, "spruce_leaves")
    b.floor(x1, D - 5, x2, D - 1, -1, "grass_block")
    for x in range(x1, x2 + 1):
        for z in range(D - 5, D - 1):
            if (x + z) % 3 == 0:
                b.set(x, 0, z, rng.choice(["poppy", "cornflower", "oxeye_daisy", "allium", "azure_bluet", "lily_of_the_valley"]))
for tx in (11, 41):
    b.set(tx, 0, D - 3, "air")
    b.command("place feature minecraft:fancy_oak {x} {y} {z}", tx, 0, D - 3)
print("planned", len(b.c.voxels), "blocks")
