"""section.py t s1 s2 y1 y2 -> side section at fixed t (rows y high->low, cols s low->high)"""
import os, sys
os.environ["MCMCP_KEEP_FORCELOAD"] = "1"
sys.path.insert(0, r"C:\Users\benny\minecraft-mcp")
from mcmcp.server import engine, block_name
OX, OY, OZ = 60, 64, 310
t, s1, s2, y1, y2 = map(int, sys.argv[1:6])
cells = engine.read_cells(OX + t, OY + y1, OZ - s2, OX + t, OY + y2, OZ - s1, "minecraft:overworld")
M = {"air": ".", "smooth_stone_slab": "_", "smooth_stone": "#", "light_gray_concrete": "L", "gray_concrete": "=",
     "white_concrete": "w", "sea_lantern": "*", "stone_bricks": "B"}
leg = {}
print("     " + "".join(str(s % 10) for s in range(s1, s2 + 1)))
for y in range(y2, y1 - 1, -1):
    row = ""
    for s in range(s1, s2 + 1):
        n = block_name(cells[(OX + t, OY + y, OZ - s)][0]).replace("minecraft:", "")
        c = M.get(n)
        if c is None:
            c = leg.setdefault(n, "abcdefghijklmnopqrstuvxyz"[len(leg) % 25])
        row += c
    print(f"{y:4d} {row}")
print(leg)
