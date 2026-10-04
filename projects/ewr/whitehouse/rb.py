"""White House harness: python wb.py dry|build <script> <name> ; render x1 x2 z1 z2 y1 y2 out [view] [cut]  (LOCAL coords)"""
import json, os, sys, time
os.environ["MCMCP_KEEP_FORCELOAD"] = "1"
sys.path.insert(0, r"C:\Users\benny\minecraft-mcp")
from mcmcp import server as S
OX, OY, OZ = 0, 0, 0
cmd = sys.argv[1]
if cmd in ("build", "dry"):
    script = open(sys.argv[2], encoding="utf-8").read()
    t = time.time()
    for attempt in range(3):
        r = S.build(script, OX, OY, OZ, name=sys.argv[3], dry_run=(cmd == "dry"), seed=7)
        if "not load" in r:
            time.sleep(3); continue
        break
    try:
        d = json.loads(r)
        print(json.dumps({k: d.get(k) for k in ("id", "blocks", "blocks_changed", "min", "max", "size", "entities",
                                                 "palette_top", "printed", "post_errors", "seconds")}, indent=1))
    except Exception:
        print(r[:4000])
    print("elapsed", round(time.time() - t, 1), "s")
elif cmd == "render":
    x1, x2, z1, z2, y1, y2 = map(int, sys.argv[2:8])
    view = sys.argv[9] if len(sys.argv) > 9 else "south_east"
    cut = int(sys.argv[10]) + OY if len(sys.argv) > 10 else None
    img = S.render(OX + x1, OY + y1, OZ + z1, OX + x2, OY + y2, OZ + z2, view=view, cutaway=cut)
    open(sys.argv[8], "wb").write(img.data)
    print("wrote", sys.argv[8])
elif cmd == "undo":
    print(S.undo(sys.argv[2]))
