"""Builder harness for the Newark agents.

  python run.py build  <script.py> <name>        place it (undoable)
  python run.py dry    <script.py> <name>        check size/palette/validation, place nothing
  python run.py render <s1> <s2> <t1> <t2> <y1> <y2> <out.png> [view] [cutaway_y]
        plan-coord box -> PNG (view: south_east | south_west | north_east | north_west | top)
  python run.py scan   <s1> <s2> <t1> <t2> <y1> <y2>   ASCII layers of a small plan box
  python run.py undo   <build_id>

Plan coords: s = north of the 04L threshold, t = east of the 04L centreline; y relative to ground
level (y=0 walking level). World = (60 + t, 64 + y, 310 - s).
"""
import json
import os
import sys
import time

os.environ["MCMCP_KEEP_FORCELOAD"] = "1"
sys.path.insert(0, r"C:\Users\benny\minecraft-mcp")
from mcmcp import server as S  # noqa: E402

OX, OY, OZ = 60, 64, 310


def world_box(s1, s2, t1, t2, y1, y2):
    xs = sorted((OX + t1, OX + t2)); zs = sorted((OZ - s1, OZ - s2)); ys = sorted((OY + y1, OY + y2))
    return xs[0], ys[0], zs[0], xs[1], ys[1], zs[1]


cmd = sys.argv[1]
if cmd in ("build", "dry"):
    script = open(sys.argv[2], encoding="utf-8").read()
    t = time.time()
    for attempt in range(3):
        r = S.build(script, OX, OY, OZ, name=sys.argv[3], dry_run=(cmd == "dry"), seed=7)
        if "not load" in r or "did not load" in r:
            time.sleep(3)
            continue
        break
    try:
        d = json.loads(r)
        print(json.dumps({k: d.get(k) for k in ("id", "blocks", "blocks_changed", "min", "max", "size",
                                                 "palette_top", "printed", "post_errors", "seconds")}, indent=1))
    except Exception:
        print(r[:4000])
    print("elapsed", round(time.time() - t, 1), "s")
elif cmd == "render":
    s1, s2, t1, t2, y1, y2 = map(int, sys.argv[2:8])
    out = sys.argv[8]
    view = sys.argv[9] if len(sys.argv) > 9 else "south_east"
    cut = int(sys.argv[10]) + OY if len(sys.argv) > 10 else None
    x1, yy1, z1, x2, yy2, z2 = world_box(s1, s2, t1, t2, y1, y2)
    img = S.render(x1, yy1, z1, x2, yy2, z2, view=view, cutaway=cut)
    open(out, "wb").write(img.data)
    print("wrote", out)
elif cmd == "scan":
    s1, s2, t1, t2, y1, y2 = map(int, sys.argv[2:8])
    print(S.scan_region(*world_box(s1, s2, t1, t2, y1, y2)))
elif cmd == "undo":
    print(S.undo(sys.argv[2]))
