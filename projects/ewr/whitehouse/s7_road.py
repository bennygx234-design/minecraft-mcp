# White House access road (WORLD coordinates; build origin 0,0,0).
# T-junction on the north side of the airport-manor highway at x -33..-27 (z -64), north to z -99,
# then west along z -99..-93 to the White House east security gate at x -93.
# Style of the existing highway: gray concrete, yellow centre line, white edge dashes, smooth-stone curbs,
# andesite-wall lamp posts with a slab arm + hanging lantern every 16 blocks. Max slope 1 in 2 (slabs).
HW_SLAB = 'polished_deepslate_slab'
path = []                     # (kind, coord) ; kind 'B' -> row z (x -33..-27), 'A' -> column x (z -99..-93)
for z in range(-65, -100, -1):
    path.append(('B', z))
for x in range(-34, -93, -1):
    path.append(('A', x))
def cross(p):
    k, c = p
    return [(x, c) for x in range(-33, -26)] if k == 'B' else [(c, z) for z in range(-99, -92)]
def med(v):
    v = sorted(v); return v[len(v) // 2]
des = []
for p in path:
    des.append(2 * (med([ground(x, z) for (x, z) in cross(p)]) + 1))
N = len(path)
h0 = 2 * 70          # highway surface at x -30, z -63 (gray concrete at y 69)
hN = 2 * 72          # White House grade (block y 71)
h = []
for i, d in enumerate(des):
    lo = max(h0 - (i + 1), hN - (N - 1 - i))
    hi = min(h0 + (i + 1), hN + (N - 1 - i))
    h.append(min(max(d, lo), hi))
for _ in range(4):
    prev = h0
    for i in range(N):
        h[i] = min(max(h[i], prev - 1), prev + 1); prev = h[i]
    nxt = hN
    for i in range(N - 1, -1, -1):
        h[i] = min(max(h[i], nxt - 1), nxt + 1); nxt = h[i]
print('profile', [x / 2 for x in h[::5]])

def put_road(x, z, h2, kind):
    """kind: gray | yellow | white | curb"""
    full = h2 % 2 == 0
    y = h2 // 2 - 1 if full else (h2 - 1) // 2
    g = ground(x, z)
    for yy in range(min(g, y) - 2, y):
        b.set(x, yy, z, 'stone_bricks' if kind == 'curb' else 'stone')
    if full:
        blk = {'gray': 'gray_concrete', 'yellow': 'yellow_concrete', 'white': 'white_concrete', 'curb': 'smooth_stone'}[kind]
    else:
        blk = 'smooth_stone_slab' if kind == 'curb' else HW_SLAB
    b.set(x, y, z, blk)
    for yy in range(y + 1, y + 9):
        b.set(x, yy, z, 'air')
    return y

def lamp(x, z, h2, ax, az):
    y = h2 // 2 if h2 % 2 == 0 else (h2 + 1) // 2      # first free y above the curb
    for yy in range(y, y + 4):
        b.set(x, yy, z, 'andesite_wall')
    b.set(x, y + 4, z, 'smooth_stone'); b.set(x, y + 5, z, 'smooth_stone_slab')
    b.set(ax, y + 4, az, 'smooth_stone_slab'); b.set(ax, y + 3, az, 'lantern[hanging=true]')

for i, p in enumerate(path):
    k, c = p
    h2 = h[i]
    if k == 'B':
        z = c
        for x in range(-33, -26):
            kind = 'yellow' if x == -30 else ('white' if x in (-33, -27) and z % 4 in (0, 1) else 'gray')
            put_road(x, z, h2, kind)
        put_road(-34, z, h2, 'curb'); put_road(-26, z, h2, 'curb')
        if z % 16 == 0 and z < -68:
            lamp(-35, z, h2, -34, z)
    else:
        x = c
        for z in range(-99, -92):
            kind = 'yellow' if z == -96 else ('white' if z in (-99, -93) and x % 4 in (0, 1) else 'gray')
            if x == -91:
                kind = 'white'                      # STOP line
            put_road(x, z, h2, kind)
        put_road(x, -100, h2, 'curb'); put_road(x, -92, h2, 'curb')
        if x % 16 == 0 and x < -36:
            lamp(x, -101, h2, x, -100)
# the corner square's outer curbs
for x in range(-34, -25):
    put_road(x, -100, h[path.index(('B', -99))], 'curb')
for z in range(-100, -92):
    put_road(-26, z, h[path.index(('B', -96))], 'curb')

# junction row z -64: open the highway curb and match the highway's own surface exactly (copy z -63)
for x in range(-33, -26):
    st = world_block(x, 69, -63) or ''
    if 'slab' in st:
        b.set(x, 69, -64, HW_SLAB); b.set(x, 68, -64, 'stone')
        for yy in range(70, 76):
            b.set(x, yy, -64, 'air')
    elif (world_block(x, 69, -63) or '').endswith('concrete'):
        b.set(x, 69, -64, 'gray_concrete')
        for yy in range(70, 76):
            b.set(x, yy, -64, 'air')
    else:
        b.set(x, 68, -64, 'gray_concrete')
        for yy in range(69, 76):
            b.set(x, yy, -64, 'air')
    print('junction', x, st)

# green direction signs (warped wood = green) on boards
def board(x, y, z, facing, lines, posts_axis):
    px, pz = (1, 0) if posts_axis == 'x' else (0, 1)
    for k in (-1, 1):
        for yy in range(y, y + 3):
            b.set(x + px * k, yy, z + pz * k, 'andesite_wall')
    for k in (-1, 0, 1):
        b.set(x + px * k, y + 3, z + pz * k, 'green_concrete'); b.set(x + px * k, y + 4, z + pz * k, 'green_concrete')
    dx, dz = DIRS[facing]
    b.sign(x + dx, y + 3, z + dz, lines, facing, wood='warped')
    b.sign(x + dx, y + 4, z + dz, ['', '', '', ''], facing, wood='warped') if False else None
def gy(x, z):
    return ground(x, z) + 1
board(-38, gy(-38, -66), -66, 'west', ['', '<- WHITE HOUSE', '1600 Penn. Ave', ''], 'z')
board(-22, gy(-22, -66), -66, 'east', ['', 'WHITE HOUSE ->', '1600 Penn. Ave', ''], 'z')
board(-37, gy(-37, -70), -70, 'north', ['<- Manor', 'Airport ->', '(via bridge)', ''], 'x')
board(-30, 0, -55, 'south', ['', 'WHITE HOUSE', '^ north ^', ''], 'x') if False else None
