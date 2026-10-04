# USSS holding cell in the East Wing basement (site-local x 149..161, z 62..75, y -9..-2)
b.box(149, -9, 62, 161, -2, 75, 'deepslate_bricks')
b.box(150, -8, 63, 160, -8, 74, 'polished_deepslate')
b.box(150, -7, 63, 160, -3, 74, 'air')
# guard corridor z 63..65, bars at z 66, cell z 67..74
for x in range(150, 161):
    for y in range(-7, -2):
        b.set(x, y, 66, 'iron_bars')
for x in range(151, 160):
    b.set(x, -7, 74, 'spruce_stairs[facing=south]')          # bench along the back wall (sitter faces north)
b.set(150, -7, 74, 'water_cauldron[level=3]'); b.set(160, -7, 74, 'smooth_quartz_slab')
for x in (152, 155, 158):
    b.set(x, -3, 70, 'lantern[hanging=true]')
    b.set(x, -3, 64, 'lantern[hanging=true]')
b.sign(155, -4, 67, ['', 'USSS', 'HOLDING', 'Cell 1'], 'south')
b.sign(155, -4, 65, ['', 'USSS', 'HOLDING', ''], 'north')
b.chair(152, -7, 64, 'south', 'spruce_stairs'); b.set(153, -7, 63, 'spruce_slab[type=top]'); b.set(153, -6, 63, 'black_stained_glass_pane')
b.sign(158, -5, 63, ['', 'Release: 60 s', 'via North Gate', ''], 'south')
