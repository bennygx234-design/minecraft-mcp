# smooth the first rows north of the T-junction per lane, and clear floating leaves over the junction
def surf(x, z):
    for y in range(80, 60, -1):
        s = world_block(x, y, z) or 'minecraft:air'
        if s.endswith(':air') or 'lantern' in s or 'leaves' in s or 'grass' in s and 'block' not in s:
            continue
        if 'slab' in s and 'type=top' not in s and 'double' not in s:
            return y + 0.5, s
        return y + 1, s
S = {}
for x in range(-34, -25):
    S[(x, -64)] = surf(x, -64)[0]
for z in range(-65, -71, -1):
    for x in range(-34, -25):
        cur, st = surf(x, z)
        allow = S[(x, z + 1)] + 0.5
        S[(x, z)] = min(cur, allow)
        if cur > allow:
            h2 = int(allow * 2)
            kind = 'curb' if x in (-34, -26) else 'road'
            if h2 % 2 == 0:
                y = h2 // 2 - 1
                b.set(x, y, z, 'smooth_stone' if kind == 'curb' else ('yellow_concrete' if x == -30 else 'gray_concrete'))
            else:
                y = (h2 - 1) // 2
                b.set(x, y, z, 'smooth_stone_slab' if kind == 'curb' else 'polished_deepslate_slab')
            for yy in range(y + 1, int(cur) + 1):
                b.set(x, yy, z, 'air')
            print('fixed', x, z, cur, '->', allow)
for x in range(-40, -20):
    for z in range(-72, -60):
        for y in range(70, 84):
            s = world_block(x, y, z) or ''
            if 'acacia_leaves' in s or 'acacia_log' in s and z <= -65:
                b.set(x, y, z, 'air')
