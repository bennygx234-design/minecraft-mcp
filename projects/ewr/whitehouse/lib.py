# shared White House helpers (exec'd at the top of each build script)
NG = 8          # north terrace walking level (z <= 44)
SG = 0          # south grade walking level
RX0, RZ0 = 48, 45   # residence local origin (85 x 43): x 48..132, z 45..87
LEAF = 'oak_leaves[persistent=true]'
FLAG_NBT = ('{patterns:[{pattern:"minecraft:stripe_top",color:"red"},{pattern:"minecraft:stripe_middle",color:"red"},'
            '{pattern:"minecraft:stripe_bottom",color:"red"},{pattern:"minecraft:square_top_left",color:"blue"}]}')

def grade(z):
    return NG if z <= 44 else SG

def tree(x, z, y=None, h=None, r=None, kind='oak'):
    y = grade(z) if y is None else y
    h = h or rng.randint(5, 8)
    r = r or rng.randint(3, 4)
    leaf = f'{kind}_leaves[persistent=true]'
    for (dx, dz, dy, rr) in [(0, 0, h, r), (rng.randint(-2, 2), rng.randint(-2, 2), h + 2, r - 1),
                            (rng.randint(-2, 2), rng.randint(-2, 2), h - 1, r - 1)]:
        b.ellipsoid(x + dx, y + dy, z + dz, rr, max(2, rr - 1), rr, leaf)
    for yy in range(y, y + h + 1):
        b.set(x, yy, z, f'{kind}_log')
    b.set(x, y + h - 2, z + 1, f'{kind}_log[axis=z]'); b.set(x + 1, y + h - 1, z, f'{kind}_log[axis=x]')

def lamp_post(x, z, y=None, h=3):
    y = grade(z) if y is None else y
    b.set(x, y, z, 'polished_blackstone')
    for yy in range(y + 1, y + h + 1):
        b.set(x, yy, z, 'polished_blackstone_wall')
    b.set(x, y + h + 1, z, 'lantern')

def balustrade(x1, z1, x2, z2, y, post_every=5, top='smooth_quartz_slab', bal='diorite_wall', post='smooth_quartz'):
    """straight run of balustrade along x or z, base at y (balusters), rail slab at y+1"""
    n = 0
    xs = range(min(x1, x2), max(x1, x2) + 1); zs = range(min(z1, z2), max(z1, z2) + 1)
    for x in xs:
        for z in zs:
            if n % post_every == 0:
                b.set(x, y, z, post); b.set(x, y + 1, z, top)
            else:
                b.set(x, y, z, bal); b.set(x, y + 1, z, top)
            n += 1

def flag(x, y, z, facing='east'):
    b.set(x, y, z, f'white_wall_banner[facing={facing}]', nbt=FLAG_NBT)

def flagpole(x, z, y=None, h=12, facing='east'):
    y = grade(z) if y is None else y
    b.set(x, y, z, 'smooth_quartz')
    for yy in range(y + 1, y + h + 1):
        b.set(x, yy, z, 'iron_bars' if yy < y + h else 'end_rod')
    dx, dz = DIRS[facing]
    flag(x + dx, y + h - 2, z + dz, facing)

def disc(cx, cz, r, y, block, r0=-1.0):
    for x in range(int(cx - r - 1), int(cx + r + 2)):
        for z in range(int(cz - r - 1), int(cz + r + 2)):
            d = math.hypot(x - cx, z - cz)
            if r0 < d <= r:
                b.set(x, y, z, block)
