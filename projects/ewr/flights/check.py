"""Swept-volume clearance check of the whole flight against the world (top solid block per column,
read from the region files after save-all flush; plants ignored, leaves/water count as solid).

For every tick, every part's rotated box is transformed to world space; every block column under its
bounding box must have its top solid block strictly below the part's lowest point.
"""
import math
import pickle
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model as MD
import flight


def load_hmap(name="hmap_solid.pkl"):
    d = pickle.load(open(os.path.join(HERE, name), "rb"))
    return d["H"], d["X1"], d["Z1"], d.get("T", {})


def check(TL, H, X1, Z1, T, every=1, report=True):
    worst = {}
    viol = []
    unknown = 0
    nx, nz = len(H), len(H[0])
    for i in range(0, len(TL), every):
        st = TL[i]
        M = MD.rot_matrix(st["yaw"], st["pitch"], st["roll"])
        cx, cy, cz = st["x"], st["y"], st["z"]
        lo_clear = 1e9
        for pi, cs in enumerate(MD.CORNERS):
            xs = []; ys = []; zs = []
            for (a, b, c) in cs:
                xs.append(cx + M[0][0] * a + M[0][1] * b + M[0][2] * c)
                ys.append(cy + M[1][0] * a + M[1][1] * b + M[1][2] * c)
                zs.append(cz + M[2][0] * a + M[2][1] * b + M[2][2] * c)
            ymin = min(ys)
            for bx in range(math.floor(min(xs)), math.floor(max(xs)) + 1):
                for bz in range(math.floor(min(zs)), math.floor(max(zs)) + 1):
                    ix, iz = bx - X1, bz - Z1
                    if not (0 <= ix < nx and 0 <= iz < nz):
                        unknown += 1; continue
                    h = H[ix][iz]
                    if h <= -64:
                        unknown += 1; continue
                    c = ymin - (h + 1)
                    if c < lo_clear:
                        lo_clear = c
                    if c < -1e-3:
                        viol.append((i, st["phase"], pi, bx, h, bz, round(ymin, 2), T.get((bx, bz), "?")))
        ph = st["phase"]
        if ph not in worst or lo_clear < worst[ph][0]:
            worst[ph] = (lo_clear, i, round(cx, 1), round(cy, 1), round(cz, 1))
    if report:
        print("lowest clearance per phase (blocks between plane and the top solid block below it):")
        for ph, w in worst.items():
            print(f"  {ph:9s} {w[0]:7.2f}  at tick {w[1]} pos {w[2:]}")
        print("violations:", len(viol), " columns outside scanned/generated area:", unknown)
        for v in viol[:40]:
            print("  ", v)
    return worst, viol


def burj_distance(TL):
    """closest horizontal distance of the plane centre to the Burj axis while above the plaza level"""
    bx, bz = 170.5, -134.5
    best = min((math.hypot(s["x"] - bx, s["z"] - bz), i) for i, s in enumerate(TL) if s["y"] > 90)
    return best


if __name__ == "__main__":
    TL, info, _ = flight.build()
    H, X1, Z1, T = load_hmap()
    check(TL, H, X1, Z1, T)
    d, i = burj_distance(TL)
    print(f"closest approach to the Burj axis: {d:.1f} blocks (tick {i}, y {TL[i]['y']:.0f}, phase {TL[i]['phase']})")
    orb = [s for s in TL if s["phase"] == "orbit"]
    rr = [math.hypot(s["x"] - 170.5, s["z"] + 134.5) for s in orb]
    print(f"orbit radius {min(rr):.1f}..{max(rr):.1f}, y {min(s['y'] for s in orb):.1f}..{max(s['y'] for s in orb):.1f}, "
          f"bank {min(s['roll'] for s in orb):.0f}..{max(s['roll'] for s in orb):.0f}")
