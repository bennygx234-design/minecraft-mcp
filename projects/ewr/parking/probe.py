"""probe.py s1 s2 t1 t2 y1 y2  -> plan maps per y (rows = s high->low, cols = t low->high)"""
import os, sys
os.environ["MCMCP_KEEP_FORCELOAD"] = "1"
sys.path.insert(0, r"C:\Users\benny\minecraft-mcp")
from mcmcp import server as S
from mcmcp.server import engine, block_name
OX, OY, OZ = 60, 64, 310
s1, s2, t1, t2, y1, y2 = map(int, sys.argv[1:7])
cells = engine.read_cells(OX + t1, OY + y1, OZ - s2, OX + t2, OY + y2, OZ - s1, "minecraft:overworld")
leg = {}
CH = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#$%&*+=?@"
def ch(n):
    n = n.replace("minecraft:", "")
    if n in ("air", "cave_air", "void_air"): return "."
    if n not in leg: leg[n] = CH[len(leg) % len(CH)]
    return leg[n]
for y in range(y2, y1 - 1, -1):
    print(f"y={y}  (cols t {t1}..{t2})")
    for s in range(s2, s1 - 1, -1):
        row = "".join(ch(block_name(cells[(OX + t, OY + y, OZ - s)][0])) for t in range(t1, t2 + 1))
        print(f"{s:4d} {row}")
print("legend:", ", ".join(f"{c}={n}" for n, c in leg.items()))
