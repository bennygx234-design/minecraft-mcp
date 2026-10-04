import sys, math
sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp.engine import Engine
e = Engine(); w = e.world
AIRS = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air", "minecraft:light"}
cx0, cz0 = 170, -135
R = 95
mx = {}
for cx in range((cx0 - R) >> 4, ((cx0 + R) >> 4) + 1):
    for cz in range((cz0 - R) >> 4, ((cz0 + R) >> 4) + 1):
        ch = w.chunk(cx, cz)
        if not ch: continue
        for sy, sec in ch.sections.items():
            if sy * 16 < 90: continue
            if len(sec.palette) == 1 and sec.palette[0].split('[')[0] in AIRS: continue
            for ly in range(16):
                y = sy * 16 + ly
                for lz in range(16):
                    for lx in range(16):
                        st = sec.block(lx, ly, lz)
                        if st.split('[')[0] in AIRS: continue
                        x, z = cx * 16 + lx, cz * 16 + lz
                        d = math.hypot(x + 0.5 - cx0, z + 0.5 - cz0)
                        b = y // 10 * 10
                        if d > mx.get(b, (0,))[0]: mx[b] = (round(d, 1), x, y, z, st)
for b in sorted(mx): print(b, mx[b])
