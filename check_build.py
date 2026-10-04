"""Check a build script OFFLINE, with no server needed.

    python check_build.py my_build.py [--render out.png]

Runs the script against the same builder API the live MCP uses, validates every block id and
property against the 26.3 catalog, and prints the size, block count and palette. With --render (and
data/client-26.3.jar present) it also draws the build by itself as an isometric PNG.
ground() returns 0 offline, so terrain-following scripts plan as if the ground were flat.
"""

import math
import sys
from collections import Counter

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))

from mcmcp import canvas as canvas_mod  # noqa: E402
from mcmcp.blocks import OPPOSITE, BlockError  # noqa: E402
from mcmcp.canvas import COLORS, DIRS, Canvas, left_of, right_of  # noqa: E402


def main():
    path = sys.argv[1]
    c = Canvas(7)
    b = canvas_mod.View(c, 0, 0, 0, 0)
    g = {"b": b, "ground": lambda lx, lz: 0, "world_block": lambda *a: None, "rng": c.rng, "random": c.rng,
         "math": math, "DIRS": DIRS, "COLORS": COLORS, "OPPOSITE": OPPOSITE, "right_of": right_of,
         "left_of": left_of, "__builtins__": __builtins__}
    try:
        exec(compile(open(path, encoding="utf-8").read(), path, "exec"), g)
    except BlockError as e:
        print("BLOCK ERROR:", e)
        sys.exit(1)
    bb = c.bbox()
    if not bb:
        print("script placed no blocks")
        return
    (x1, y1, z1), (x2, y2, z2) = bb
    pal = Counter(s.split("[")[0] for s, _ in c.voxels.values())
    print(f"OK: {len(c.voxels)} blocks, local box ({x1},{y1},{z1})..({x2},{y2},{z2}), "
          f"size {x2 - x1 + 1}x{y2 - y1 + 1}x{z2 - z1 + 1}, {len(pal)} block types, {len(c.entities)} entities")
    for name, n in pal.most_common(12):
        print(f"  {n:7d}  {name}")
    if "--render" in sys.argv:
        from mcmcp.render import render_cells
        out = sys.argv[sys.argv.index("--render") + 1]
        cells = {p: v for p, v in c.voxels.items() if not v[0].endswith(":air")}
        open(out, "wb").write(render_cells(cells))
        print("rendered", out)


if __name__ == "__main__":
    main()
