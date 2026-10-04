"""Render the display-entity car models from parts.json (same transform math the game uses: T * L * S)."""
import json, math, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))
COL = {"red_concrete": "#8e2121", "yellow_concrete": "#f1af15", "orange_concrete": "#e06101", "lime_concrete": "#5ea918",
       "black_concrete": "#08090e", "gray_concrete": "#36393d", "light_gray_concrete": "#7d7d73", "white_concrete": "#f0f4f5",
       "black_stained_glass": "#191919", "gold_block": "#f6d03d"}


def qrot(q, v):
    x, y, z, w = q
    vx, vy, vz = v
    tx = 2 * (y * vz - z * vy); ty = 2 * (z * vx - x * vz); tz = 2 * (x * vy - y * vx)
    return (vx + w * tx + (y * tz - z * ty), vy + w * ty + (z * tx - x * tz), vz + w * tz + (x * ty - y * tx))


def faces(p, yaw=0.0):
    sx, sy, sz = p["s"]
    corners = {}
    for i in (0, 1):
        for j in (0, 1):
            for k in (0, 1):
                v = qrot(p["q"], (i * sx, j * sy, k * sz))
                v = (v[0] + p["t"][0], v[1] + p["t"][1], v[2] + p["t"][2])
                # entity yaw: rotate about Y by -yaw (Minecraft display renderer)
                a = math.radians(-yaw)
                x = v[0] * math.cos(a) + v[2] * math.sin(a)
                z = -v[0] * math.sin(a) + v[2] * math.cos(a)
                corners[(i, j, k)] = (x, z, v[1])   # plot coords: x, z(ground), y(up)
    F = [[(0,0,0),(1,0,0),(1,1,0),(0,1,0)], [(0,0,1),(1,0,1),(1,1,1),(0,1,1)], [(0,0,0),(1,0,0),(1,0,1),(0,0,1)],
         [(0,1,0),(1,1,0),(1,1,1),(0,1,1)], [(0,0,0),(0,1,0),(0,1,1),(0,0,1)], [(1,0,0),(1,1,0),(1,1,1),(1,0,1)]]
    return [[corners[c] for c in f] for f in F]


def draw(ax, parts, elev, azim, title, yaw=0.0):
    polys, cols = [], []
    for p in parts:
        for f in faces(p, yaw):
            polys.append(f)
            c = COL.get(p["block"], "#ff00ff")
            cols.append(c)
    pc = Poly3DCollection(polys, facecolors=cols, edgecolors="#00000030", linewidths=0.2,
                          alpha=1.0)
    ax.add_collection3d(pc)
    ax.set_xlim(-2.9, 2.9); ax.set_ylim(-2.9, 2.9); ax.set_zlim(0, 1.6)
    ax.set_box_aspect((5.8, 5.8, 1.6), zoom=1.35)
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=9)
    ax.set_axis_off()


def main():
    data = json.load(open(os.path.join(HERE, "parts.json")))
    for name, parts in data.items():
        fig = plt.figure(figsize=(18, 10))
        views = [(22, 55, "front 3/4"), (22, -125, "rear 3/4"), (0, 0, "side (from +x)"), (89, -90, "top (nose up)"),
                 (5, 90, "front"), (30, 180, "yaw=90, seen from -x (nose toward camera = west)")]
        for i, (e, a, t) in enumerate(views):
            ax = fig.add_subplot(2, 3, i + 1, projection="3d")
            draw(ax, parts, e, a, t, yaw=90.0 if i == 5 else 0.0)
        fig.suptitle(f"{name}: {len(parts)} block_display parts   (+z = nose)")
        fig.tight_layout()
        out = os.path.join(HERE, f"preview_{name}.png")
        fig.savefig(out, dpi=90)
        plt.close(fig)
        print(out)


if __name__ == "__main__":
    main()
