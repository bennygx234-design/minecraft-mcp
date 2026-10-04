exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\lightrail\lr_lib.py").read())
STOP = globals().get('STOP', 'ALL')

def pane_run(cells, blk='light_gray_stained_glass_pane'):
    cs = set(cells)
    for (x, y, z) in cells:
        st = []
        for dn, (ddx, ddz) in (('north', (0, -1)), ('south', (0, 1)), ('east', (1, 0)), ('west', (-1, 0))):
            if (x + ddx, y, z + ddz) in cs:
                st.append(dn + '=true')
        plan(x, y, z, blk + ('[' + ','.join(st) + ']' if st else ''))

def roof(x1, x2, z1, z2, y, lights=()):
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            edge = x in (x1, x2) or z in (z1, z2)
            blk = 'sea_lantern' if (x, z) in lights else ('light_gray_concrete' if edge else 'smooth_quartz')
            plan(x, y, z, blk)

def post(x, z, y1, y2, blk='light_gray_concrete'):
    for y in range(y1, y2 + 1):
        plan(x, y, z, blk)

def lift_tower(x1, x2, z1, z2, ybot, ytop, open_sides):
    """glass-sided lift frame: corner posts ybot..ytop-1, roof at ytop, glass on the non-open sides from ybot+3"""
    for (x, z) in ((x1, z1), (x1, z2), (x2, z1), (x2, z2)):
        post(x, z, ybot, ytop - 1)
    glass = []
    for y in range(ybot + 3, ytop):
        if 'W' not in open_sides:
            glass += [(x1, y, z) for z in range(z1 + 1, z2)]
        if 'E' not in open_sides:
            glass += [(x2, y, z) for z in range(z1 + 1, z2)]
        if 'N' not in open_sides:
            glass += [(x, y, z1) for x in range(x1 + 1, x2)]
        if 'S' not in open_sides:
            glass += [(x, y, z2) for x in range(x1 + 1, x2)]
    pane_run(glass, 'glass_pane')
    # light band at the top of the posts' level
    cx, cz = (x1 + x2) // 2, (z1 + z2) // 2
    roof(x1, x2, z1, z2, ytop, lights={(cx, cz), (cx + 1, cz)})

if STOP in ('ALL', 'HAN'):
    # Hangars stop (4,64,5): rider drops from (4,74,10) heading north. Apron at y=63.
    lift_tower(1, 6, 2, 11, 64, 76, open_sides='S')
    print('HAN tower')

if STOP in ('ALL', 'CAR'):
    # Cargo stop (-10,64,278): rider arrives from the west at y~72 then drops north to z=278.
    lift_tower(-13, -8, 276, 282, 64, 84, open_sides='W')
    print('CAR tower')

if STOP in ('ALL', 'MAN'):
    # Manor stop (83,75,-97): landing strip along the manor's south gate at floor y=74 (top 75).
    for x in range(80, 86):
        PLAN[(x, 75, -97)] = 'air'            # ramp's last step sits too high: lower it to the platform
    for x in (80, 85):
        PLAN[(x, 76, -97)] = 'air'
    for x in range(78, 89):
        PLAN[(x, 74, -97)] = 'smooth_quartz' if not nogo(x, -97) else None
    for x in (78, 79, 86, 87, 88):
        plan(x, 74, -96, 'smooth_quartz')
        plan(x, 73, -96, 'light_gray_concrete')
    for x in range(78, 89):
        plan(x, 73, -97, 'light_gray_concrete')
    # south edge rail on the wings
    pane_run([(x, 75, -95) for x in (78, 79)] + [(x, 75, -95) for x in (86, 87, 88)])
    for x in (78, 79, 86, 87, 88):
        plan(x, 74, -95, 'light_gray_concrete')
    # canopy: posts on the wings, roof over the landing
    post(78, -96, 75, 79); post(88, -96, 75, 79)
    roof(78, 88, -97, -96, 80, lights={(80, -97), (86, -97), (83, -96)})
    # stairs down to the road edge (ground y=71) at both ends
    for i, (x, sx) in enumerate(((89, 'west'), (90, 'west'))):
        y = 73 - i
        for z in (-97, -96):
            plan(x, y, z, 'smooth_quartz_stairs[facing=%s]' % sx)
            for yy in range(72, y):
                plan(x, yy, z, 'light_gray_concrete')
    for i, (x, sx) in enumerate(((77, 'east'), (76, 'east'))):
        y = 73 - i
        for z in (-97, -96):
            plan(x, y, z, 'smooth_quartz_stairs[facing=%s]' % sx)
            for yy in range(72, y):
                plan(x, yy, z, 'light_gray_concrete')
    for k in list(PLAN):
        if PLAN[k] is None:
            del PLAN[k]
    print('MAN platform')

if STOP in ('ALL', 'BUR'):
    # Burj lobby stop (145,69,-122): platform floor y=68 (top 69) on the plaza (67).
    for x in range(143, 147):
        PLAN[(x, 69, -122)] = 'air'           # ramp's last slab -> flat platform
    for x in range(142, 147):
        for z in range(-126, -120):
            plan(x, 68, z, 'smooth_quartz')
    for x in range(143, 147):
        PLAN[(x, 68, -122)] = 'smooth_quartz'
    # step slabs on the open west / north edges
    for z in range(-126, -120):
        plan(141, 68, z, 'smooth_quartz_slab[type=bottom]')
    for x in range(141, 147):
        plan(x, 68, -127, 'smooth_quartz_slab[type=bottom]')
    post(141, -126, 68, 72); post(141, -121, 68, 72)
    roof(141, 146, -126, -121, 73, lights={(143, -124), (144, -123)})
    print('BUR platform')

flush()
