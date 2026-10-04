"""Airliner display model for the scenic flight: the ewr_planes geometry + Emirates livery
(narrowbody, 2 engines). Re-centred on the fuselage centre so the whole plane rotates about it.

Part frame (from airliner_model.py): x = left wing (+x), y = up, z = forward (nose +z), y = 0 at the
wheels. The plane centre C is the fuselage axis at mid-length.
"""
import math
import os
import sys

PLANES = r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\planes"
sys.path.insert(0, PLANES)
import build_planes as BP  # noqa: E402  (module import only builds geometry; it writes nothing)

LIVERY, SIZE = "emirates", "narrow"
PARTS = BP.model(LIVERY, SIZE)
_cs = [c for p in PARTS for c in p.corners()]
NOSE = max(c[2] for c in _cs)
TAIL = min(c[2] for c in _cs)
CY = 1.85 * BP.SIZES[SIZE].get("k", 1.0)          # fuselage axis height above the wheels
CZ = round((NOSE + TAIL) / 2, 3)                   # mid-length
C = (0.0, CY, CZ)
GROUND_Y = 64.0                                    # wheel contact (top of the runway blocks)
CENTRE_GROUND = GROUND_Y + CY                      # centre height when standing on the ground

qmul, qrot = BP.qmul, BP.qrot


def qz(deg):
    h = math.radians(deg) / 2
    return (0.0, 0.0, math.sin(h), math.cos(h))


def part_nbt(p, roll_deg, idx, extra_tags=()):
    """block_display NBT (relative to the centre) with the roll baked in."""
    q_r = qz(roll_deg)
    half = qrot(p.q, tuple(s / 2 for s in p.size))
    t = tuple(p.center[i] - C[i] - half[i] for i in range(3))
    t = qrot(q_r, t)
    q = qmul(q_r, p.q)
    return transformation(q, t, p.size)


def fnum(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return (s if s not in ("-0", "") else "0") + "f"


def transformation(q, t, size):
    lst = lambda vs: "[" + ",".join(fnum(v) for v in vs) + "]"
    return ("{left_rotation:%s,right_rotation:[0f,0f,0f,1f],translation:%s,scale:%s}"
            % (lst(q), lst(t), lst(size)))


# corner offsets relative to the centre (for clearance checks)
CORNERS = [[tuple(c[i] - C[i] for i in range(3)) for c in p.corners()] for p in PARTS]


def rot_matrix(yaw, pitch_mc, roll):
    """display orientation: Ry(-yaw) * Rx(pitch) * Rz(roll) (degrees), as a 3x3 row-major matrix"""
    a, b, c = math.radians(-yaw), math.radians(pitch_mc), math.radians(roll)
    ca, sa, cb, sb, cc, sc = math.cos(a), math.sin(a), math.cos(b), math.sin(b), math.cos(c), math.sin(c)
    Ry = [[ca, 0, sa], [0, 1, 0], [-sa, 0, ca]]
    Rx = [[1, 0, 0], [0, cb, -sb], [0, sb, cb]]
    Rz = [[cc, -sc, 0], [sc, cc, 0], [0, 0, 1]]
    mm = lambda A, B: [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return mm(mm(Ry, Rx), Rz)


def lowest(pitch_mc, roll):
    """lowest model point relative to the centre (blocks, negative) at this attitude"""
    M = rot_matrix(0, pitch_mc, roll)
    return min(M[1][0] * x + M[1][1] * y + M[1][2] * z for cs in CORNERS for (x, y, z) in cs)


if __name__ == "__main__":
    print(len(PARTS), "parts; nose", NOSE, "tail", TAIL, "centre", C)
    for th in (0, 2, 3, 4, 5, 6, 8):
        print("nose-up", th, "lowest", round(lowest(-th, 0), 3))
    for r in (0, 10, 20, 30):
        print("roll", r, "lowest", round(lowest(0, r), 3))
    M = rot_matrix(90, 0, 0)
    print("yaw 90: nose ->", [round(sum(M[i][k] * v for k, v in enumerate((0, 0, 10))), 2) for i in range(3)])
    M = rot_matrix(0, 0, 30)
    print("right bank 30: right wing tip (-10,0,0) ->", [round(sum(M[i][k] * v for k, v in enumerate((-10, 0, 0))), 2) for i in range(3)])
