"""Inventory of the block-built static planes + their replacement flyable planes.

  python static_planes.py check     # count planned vs still-matching cells per plane (no changes)
  python static_planes.py remove    # one undoable build: matching plane cells -> air
  python static_planes.py spawn     # spawn the flyable replacements (function ewr_planes:spawn_at ...)

Plan frame: build origin (60, 64, 310); builder x = t, z = -s; world = (60 + t, 64 + y, 310 - s).
A view's local north (-z) is the nose; rot = quarter turns clockwise (0=N, 1=E, 2=S, 3=W).
"""
import json
import math
import os
import sys

sys.path.insert(0, r"C:\Users\benny\minecraft-mcp")
from mcmcp.canvas import Canvas, View  # noqa: E402
from mcmcp.engine import Engine  # noqa: E402
from mcmcp import blocks  # noqa: E402

EWR = r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr"
OX, OY, OZ = 60, 64, 310
YAW = {0: 180, 1: -90, 2: 0, 3: 90}     # rot -> Minecraft yaw of the nose
HDG = {0: (0, -1), 1: (1, 0), 2: (0, 1), 3: (-1, 0)}   # rot -> world (dx, dz) of the nose


def load_funcs(b):
    g = {"b": b, "math": math}
    exec(open(os.path.join(EWR, "kit.py"), encoding="utf-8").read(), g)
    src = open(os.path.join(EWR, "termB", "b3_planes.py"), encoding="utf-8").read()
    a = src.index("def rplane"); e = src.index("\n\n\n", a)
    exec(src[a:e], g)
    exec(open(os.path.join(EWR, "north", "lib.py"), encoding="utf-8").read(), g)
    return g


# (zone, s, t, rot, static kind, static args, flyable livery, flyable size)
#   static kind: plane(livery, big) | rplane(livery) | bizjet(stripe)
PLANES = [
    ("termA A20", 59, -61, 0, "plane", ("jetblue", False), "jetblue", "narrow"),
    ("termA A24", 59, -38, 0, "plane", ("american", False), "american", "narrow"),
    ("termA A21", 93, -61, 2, "plane", ("delta", False), "delta", "narrow"),
    ("termA A25", 93, -38, 2, "plane", ("alaska", False), "alaska", "narrow"),
    ("termB B51", 135, -42, 3, "plane", ("emirates", True), "emirates", "wide"),
    ("termB B62", 155, -54, 3, "plane", ("lufthansa", False), "lufthansa", "narrow"),
    ("termB B42", 127, -57, 3, "rplane", ("delta",), "delta", "regional"),
    ("termB B60", 159, -34, 3, "rplane", ("alaska",), "alaska", "regional"),
    ("termC C1", 179, -45, 3, "plane", ("united", False), "united", "narrow"),
    ("termC C2", 200, -38, 3, "plane", ("united", False), "united", "narrow"),
    ("termC C3", 221, -45, 3, "plane", ("united", False), "united", "narrow"),
    ("hangar 1", 330, -84, 2, "plane", ("united", True), "united", "wide"),
    ("hangar 2", 332, -56, 2, "plane", ("fedex", False), "fedex", "narrow"),
    ("hangar 3", 332, -32, 2, "plane", ("delta", False), "delta", "narrow"),
    ("FBO bizjet", 308, -25, 2, "bizjet", ("blue_concrete",), "pj_blue", "private"),
    ("cargo FedEx", 31, -45, 3, "plane", ("fedex", True), "fedex", "wide"),
    ("cargo UPS", 6, -50, 3, "plane", ("ups", False), "ups", "narrow"),
]
# extra private jets on the FBO ramp (no static plane to remove)
EXTRA = [("FBO ramp 2", 303, -35, 2, "pj_red", "private", 6),
         ("FBO ramp 3", 303, -46, 2, "pj_gold", "private", 6)]
# the two planes from the first job (world coords given as plan (s, t); nose offset 0 = ghast at the spot)
ORIGINAL = [("north apron", 310 - 22, 4 - 60, 3, "ewr", "narrow", 0),     # world (4, 64, 22) facing west
            ("rwy 04L end", 310 - 293, 0, 0, "delta", "narrow", 0)]     # world (60, 64, 293) facing north

# nose position of the static plane relative to its view origin (local -z), per kind
STATIC_NOSE = {("plane", False): 12, ("plane", True): 16, ("rplane", None): 8, ("bizjet", None): 6}


def plane_cells(entry):
    zone, s, t, rot, kind, args = entry[:6]
    c = Canvas()
    root = View(c, 0, 0, 0, 0)
    g = load_funcs(root)
    v = g["at"](s, t, 0, rot)
    g[kind](v, *args)
    return {(x + OX, y + OY, z + OZ): st for (x, y, z), (st, nbt) in c.voxels.items()}


def nose_offset(entry):
    kind, args = entry[4], entry[5]
    return STATIC_NOSE[(kind, args[1] if kind == "plane" else None)]


def main():
    from build_planes import SIZES
    e = Engine()
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode in ("check", "remove"):
        e.flush()
        all_air = {}
        for p in PLANES:
            cells = plane_cells(p)
            snap = e.snapshot(cells.keys(), "minecraft:overworld")
            match = {pos for pos, st in cells.items()
                     if blocks.canonical(snap[pos][0]) == blocks.canonical(st)}
            ys = [pos[1] for pos in cells]
            print(f"{p[0]:12s} planned {len(cells):4d} matching {len(match):4d}  y {min(ys)}..{max(ys)}")
            for pos in match:
                all_air[pos] = ("minecraft:air", None)
        if mode == "remove":
            r = e.place_cells(all_air, "ewr_planes remove static planes", origin=(OX, OY, OZ))
            print(json.dumps({k: r.get(k) for k in ("id", "blocks_changed", "min", "max")}))
    elif mode == "spawn":
        for p in PLANES:
            zone, s, t, rot, kind, args, livery, size = p
            spawn(e, zone, s, t, rot, livery, size, nose_offset(p))
        for zone, s, t, rot, livery, size, nose in EXTRA:
            spawn(e, zone, s, t, rot, livery, size, nose)
        for zone, s, t, rot, livery, size, _ in ORIGINAL:
            spawn(e, zone, s, t, rot, livery, size, SIZES[size]["nose"])


def spawn(e, zone, s, t, rot, livery, size, static_nose):
    from build_planes import SIZES
    nose = SIZES[size]["nose"]          # nose distance ahead of the ghast for the flyable model
    d = static_nose - nose               # put the ghast so both noses coincide
    dx, dz = HDG[rot]
    x = OX + t + 0.5 + dx * d
    z = OZ - s + 0.5 + dz * d
    cmd = (f'function ewr_planes:spawn_at {{x:{x:.2f},y:{OY},z:{z:.2f},yaw:{YAW[rot]},'
           f'livery:"{livery}",size:"{size}"}}')
    print(zone, livery, size, f"({x:.1f}, {OY}, {z:.1f}) yaw {YAW[rot]}", e.cmd(cmd))


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
