"""Heightmap of the airport/city region (top non-air block per column) -> hmap.npz + hmap.png"""
import sys, os, time
sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
import pickle
from mcmcp.engine import Engine
from mcmcp.world import block_name
HERE = os.path.dirname(os.path.abspath(__file__))
X1, X2, Z1, Z2 = -300, 480, -700, 520
AIRS = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air", "minecraft:light"}
e = Engine(); e.flush(); w = e.world
H = [[-64] * (Z2 - Z1 + 1) for _ in range(X2 - X1 + 1)]
T = {}
t0 = time.time()
for cx in range(X1 >> 4, (X2 >> 4) + 1):
    for cz in range(Z1 >> 4, (Z2 >> 4) + 1):
        ch = w.chunk(cx, cz)
        if ch is None:
            continue
        secs = sorted(ch.sections, reverse=True)
        for lx in range(16):
            x = cx * 16 + lx
            if not X1 <= x <= X2: continue
            for lz in range(16):
                z = cz * 16 + lz
                if not Z1 <= z <= Z2: continue
                done = False
                for sy in secs:
                    sec = ch.sections[sy]
                    if len(sec.palette) == 1 and sec.palette[0].split('[')[0] in AIRS:
                        continue
                    for ly in range(15, -1, -1):
                        st = sec.block(lx, ly, lz)
                        if st.split('[')[0] not in AIRS:
                            H[x - X1][z - Z1] = sy * 16 + ly
                            T[(x, z)] = st
                            done = True
                            break
                    if done: break
print("scan", round(time.time() - t0, 1), "s")
pickle.dump(dict(H=H, X1=X1, Z1=Z1, T=T), open(os.path.join(HERE, "hmap.pkl"), "wb"))
from PIL import Image
im = Image.new("RGB", (X2 - X1 + 1, Z2 - Z1 + 1))
px = im.load()
for i in range(X2 - X1 + 1):
    for j in range(Z2 - Z1 + 1):
        v = max(0, min(255, int((H[i][j] - 60) * 2.5)))
        px[i, j] = (v, v, v) if H[i][j] > 63 else ((0, 0, 120) if 'water' in T.get((i + X1, j + Z1), '') else (0, 60, 0))
im.resize((im.width * 2, im.height * 2), Image.NEAREST).save(os.path.join(HERE, "hmap.png"))
print(max(max(c) for c in H))
