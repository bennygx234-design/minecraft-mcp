# level the site: local x 0..179, z 0..155. North terrace (z<=44) grade top y=7, south grade top y=-1
W, D = 180, 156
for x in range(W):
    for z in range(D):
        ty = 7 if z <= 44 else -1
        g = ground(x, z)
        lo = min(g, ty) - 1
        for y in range(max(lo, ty - 14), ty):
            b.set(x, y, z, 'dirt')
        b.set(x, ty, z, 'grass_block')
        top = max(g, ty) + 14
        for y in range(ty + 1, min(top, 60) + 1):
            b.set(x, y, z, 'air')
