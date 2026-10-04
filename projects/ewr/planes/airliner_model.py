"""Aircraft geometry for ewr_planes (imported by build_planes.py).

Feet frame: y up from the ghast's feet, z forward (nose +z), x sideways. Models are built at
narrowbody scale and then scaled by k about the origin. The seat is at (0, seat, 0) and the
model is shifted back (ZO) so the pilot sits just behind the windshield.
"""
import math

PROFILE = [(0.80, 0.56), (0.72, 0.78), (0.56, 0.90)]  # rounded section: (half width, half height)


class Builder:
    def __init__(self, Part, qmul, qaxis, qrot, k=1.0, zo=0.0):
        self.Part, self.qmul, self.qaxis, self.qrot = Part, qmul, qaxis, qrot
        self.k, self.zo, self.P = k, zo, []

    def add(self, center, size, block, rots=()):
        k = self.k
        c = (center[0] * k, center[1] * k, (center[2] + self.zo) * k)
        self.P.append(self.Part(c, tuple(s * k for s in size), block, rots))

    def box(self, x0, x1, y0, y1, z0, z1, block, rots=()):
        self.add(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), block, rots)

    def section(self, z0, z1, yc, s, body, belly=None, split=None, w=1.0):
        for hw, hh in PROFILE:
            hw, hh = hw * s * w, hh * s * w
            y0, y1 = yc - hh, yc + hh
            if belly and split is not None and y0 < split < y1:
                self.box(-hw, hw, y0, split, z0, z1, belly)
                self.box(-hw, hw, split, y1, z0, z1, body)
            else:
                self.box(-hw, hw, y0, y1, z0, z1, body if not (belly and split is not None and y1 <= split) else belly)

    def swept(self, root, sweep, dihedral, segs, block, mirror=True):
        """wing-like surface: segs = [(s0, s1, chord, thick)], root = leading-edge root point"""
        qa, qm = self.qaxis, self.qmul
        q = qm(qa("y", sweep), qa("z", dihedral))
        span, back = self.qrot(q, (1, 0, 0)), self.qrot(q, (0, 0, -1))
        for s0, s1, chord, thick in segs:
            sm = (s0 + s1) / 2
            ctr = tuple(root[i] + span[i] * sm + back[i] * chord / 2 for i in range(3))
            for sx in ((1, -1) if mirror else (1,)):
                self.add((sx * ctr[0], ctr[1], ctr[2]), (s1 - s0, thick, chord), block,
                         [("y", sx * sweep), ("z", sx * dihedral)])
        return span, back

    def nacelle(self, x, y, z1, length, r, cowl, intake="black_concrete"):
        z0 = z1 - length
        for hw, hh in [(r, r * 0.68), (r * 0.68, r), (r * 0.89, r * 0.89)]:
            self.box(x - hw, x + hw, y - hh, y + hh, z0, z1, cowl)
        for hw, hh in [(r * 0.82, r * 0.55), (r * 0.55, r * 0.82), (r * 0.7, r * 0.7)]:
            self.box(x - hw, x + hw, y - hh, y + hh, z1, z1 + 0.04, intake)
        self.box(x - r * 0.18, x + r * 0.18, y - r * 0.18, y + r * 0.18, z1 + 0.02, z1 + 0.12, "light_gray_concrete")
        for hw, hh in [(r * 0.6, r * 0.4), (r * 0.4, r * 0.6)]:
            self.box(x - hw, x + hw, y - hh, y + hh, z0 - length * 0.18, z0, "gray_concrete")

    def fin(self, y0, z_le0, height, sweep_deg, c_root, c_tip, thick, pattern, rows=8, cols=3):
        """vertical fin from stacked horizontal slabs; pattern(i, j) -> block (i row from bottom,
        j chord third from the front). Returns a function (row, frac) -> (y, z) for emblems."""
        h = height / rows
        tb = math.tan(math.radians(sweep_deg))
        for i in range(rows):
            yb = y0 + i * h
            le = z_le0 - (i + 0.5) * h * tb
            ch = c_root + (c_tip - c_root) * i / (rows - 1)
            # merge equal-colour chord pieces
            runs = []
            for j in range(cols):
                blk = pattern(i, j)
                if runs and runs[-1][0] == blk:
                    runs[-1][2] = j + 1
                else:
                    runs.append([blk, j, j + 1])
            for blk, j0, j1 in runs:
                self.box(-thick / 2, thick / 2, yb, yb + h, le - ch * j1 / cols, le - ch * j0 / cols, blk)

        def where(row, frac):
            ch = c_root + (c_tip - c_root) * row / (rows - 1)
            return y0 + (row + 0.5) * h, z_le0 - (row + 0.5) * h * tb - ch * frac
        return where

    def disc(self, x_off, y, z, r, block, both=True):
        """round emblem on a fin side (x = +-x_off)"""
        for sx in ((1, -1) if both else (1,)):
            x0, x1 = sorted((sx * x_off, sx * (x_off + 0.02)))
            self.box(x0, x1, y - r, y + r, z - r * 0.6, z + r * 0.6, block)
            self.box(x0, x1, y - r * 0.6, y + r * 0.6, z - r, z + r, block)
            self.box(x0, x1, y - r * 0.85, y + r * 0.85, z - r * 0.85, z + r * 0.85, block)


def airliner(c, b, stretch=0.0, engines=2):
    """c = livery dict. Narrowbody geometry; stretch adds cabin length (negative shortens)."""
    st = stretch
    YC = 1.85
    SPLIT = YC - 0.3
    body, belly = c["body"], c["belly"]
    # fuselage
    b.section(-11.0 - st, 3.5, YC, 1.0, body, belly, SPLIT)
    for z0, z1, yc, s in [(3.5, 4.4, 1.83, 0.93), (4.4, 5.2, 1.80, 0.82), (5.2, 5.9, 1.76, 0.66),
                          (5.9, 6.5, 1.73, 0.48), (6.5, 6.95, 1.70, 0.28)]:
        b.section(z0, z1, yc, s, body, belly, SPLIT)
    b.box(-0.08, 0.08, 1.62, 1.78, 6.95, 7.05, c.get("radome", "light_gray_concrete"))
    for z0, z1, yc, s in [(-12.2, -11.0, 1.97, 0.90), (-13.4, -12.2, 2.10, 0.76), (-14.5, -13.4, 2.25, 0.60),
                          (-15.5, -14.5, 2.38, 0.44), (-16.3, -15.5, 2.50, 0.28)]:
        b.section(z0 - st, z1 - st, yc, s, c.get("tailcone", body), belly, SPLIT)
    b.box(-0.1, 0.1, 2.48, 2.66, -16.5 - st, -16.3 - st, "gray_concrete")
    # windshield (sloped) + cockpit side windows
    p0, p1 = (4.3, 2.70), (5.6, 2.30)
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    ang = math.degrees(math.atan2(p0[1] - p1[1], p1[0] - p0[0]))
    b.add((0, (p0[1] + p1[1]) / 2, (p0[0] + p1[0]) / 2), (0.95, 0.05, L), "black_concrete", [("x", ang)])
    for sx in (1, -1):
        x0, x1 = sorted((sx * 0.745, sx * 0.76))
        b.box(x0, x1, 2.05, 2.3, 3.7, 4.35, "black_concrete")
    # cheat line, titles, windows, doors
    for sx in (1, -1):
        x0, x1 = sorted((sx * 0.80, sx * 0.815))
        if c.get("stripe"):
            b.box(x0, x1, 1.70, 1.84, -11.0 - st, 3.5, c["stripe"])
            for z0, z1, hw in [(3.5, 4.4, 0.75), (4.4, 5.2, 0.66), (-12.2 - st, -11.0 - st, 0.73)]:
                xa, xb = sorted((sx * hw, sx * (hw + 0.015)))
                b.box(xa, xb, 1.70, 1.84, z0, z1, c["stripe"])
        if c.get("titles"):
            b.box(x0, x1, 2.26, 2.39, -2.0, 2.4, c["titles"])
        z = -10.2 - st
        while z < 2.3:
            b.box(x0, x1, 2.0, 2.2, z, z + 0.26, "black_stained_glass")
            z += 0.75
        b.box(x0, x1, 1.6, 2.4, 2.75, 3.15, "light_gray_concrete")
        b.box(x0, x1, 1.6, 2.4, -10.95 - st, -10.55 - st, "light_gray_concrete")
    # wings: low, thin, swept, dihedral
    root = (0.0, 1.15, -1.6)
    span, back = b.swept(root, 28.0, 5.0, [(0.0, 3.6, 3.5, 0.22), (3.6, 8.0, 2.3, 0.2), (8.0, 12.4, 1.35, 0.18)],
                         c["wing"])
    b.box(-0.72, 0.72, 0.95, 1.25, -5.4, -1.6, belly)                            # wing-body fairing

    def wpt(s, ch, dy=0.0):
        return tuple(root[i] + span[i] * s + back[i] * ch for i in range(3))

    for sx in (1, -1):                                                         # winglets + nav lights
        wl = wpt(12.3, 0.62)
        b.add((sx * wl[0], wl[1] + 0.5, wl[2]), (0.08, 1.0, 0.85), c["winglet"], [("y", sx * 34), ("z", -sx * 12)])
        nv = wpt(12.25, 0.2)
        b.add((sx * nv[0], nv[1] + 0.12, nv[2]), (0.15, 0.1, 0.2), "lime_concrete" if sx > 0 else "red_concrete",
              [("y", sx * 28)])
    # engines
    stations = [3.5] if engines == 2 else [2.9, 6.9]
    for sta in stations:
        le = wpt(sta, 0.0)
        r = 0.44 if engines == 2 else 0.36
        for sx in (1, -1):
            x = sx * le[0]
            b.nacelle(x, le[1] - 0.18 - r, le[2] + 1.3, 2.3 if engines == 2 else 2.0, r, c["engine"])
            b.box(x - 0.05, x + 0.05, le[1] - 0.25, le[1] - 0.05, le[2] - 0.6, le[2] + 0.5, c["wing"])  # pylon
    # vertical fin (stacked slabs, swept 40 deg) + emblem
    where = b.fin(2.55, -11.7 - st, 3.6, 40.0, 3.2, 1.3, 0.16, c["fin"])
    if c.get("emblem"):
        row, frac, rad, blk = c["emblem"][:4]
        y, z = where(row, frac)
        b.disc(0.08, y, z, rad, blk)
        if len(c["emblem"]) > 4:
            b.disc(0.1, y, z, rad * 0.45, c["emblem"][4])
    b.add((0, 2.72, -11.0 - st), (0.12, 0.1, 1.6), body, [("x", -8.0)])        # dorsal fillet
    # horizontal stabilisers
    b.swept((0.0, 2.3, -13.4 - st), 32.0, 4.0, [(0.0, 2.2, 1.5, 0.12), (2.2, 4.2, 0.95, 0.12)], c["wing"])
    # landing gear
    b.box(-0.06, 0.06, 0.35, 1.2, 4.8, 4.92, "gray_concrete")
    b.box(-0.16, 0.16, 0.0, 0.42, 4.65, 5.07, "black_concrete")
    for sx in (1, -1):
        x = sx * 0.95
        b.box(x - 0.06, x + 0.06, 0.4, 1.1, -4.3, -4.18, "gray_concrete")
        b.box(x - 0.22, x + 0.22, 0.0, 0.48, -4.75, -3.75, "black_concrete")
    return b.P


def private_jet(c, b):
    """Small business jet (~11 long, ~10.5 span): T-tail, rear-mounted engines."""
    W = 0.62               # cross-section scale vs the airliner profile (diameter ~1.1)
    YC = 1.05
    body = c["body"]
    b.section(-3.6, 2.4, YC, 1.0, body, w=W)
    for z0, z1, yc, s in [(2.4, 3.1, 1.02, 0.9), (3.1, 3.7, 0.99, 0.74), (3.7, 4.2, 0.96, 0.55),
                          (4.2, 4.55, 0.94, 0.35)]:
        b.section(z0, z1, yc, s, body, w=W)
    for z0, z1, yc, s in [(-4.5, -3.6, 1.12, 0.86), (-5.4, -4.5, 1.22, 0.68), (-6.2, -5.4, 1.32, 0.48),
                          (-6.8, -6.2, 1.40, 0.3)]:
        b.section(z0, z1, yc, s, body, w=W)
    # windshield + cockpit side windows
    p0, p1 = (2.55, 1.6), (3.5, 1.33)
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    ang = math.degrees(math.atan2(p0[1] - p1[1], p1[0] - p0[0]))
    b.add((0, (p0[1] + p1[1]) / 2, (p0[0] + p1[0]) / 2), (0.6, 0.04, L), "black_concrete", [("x", ang)])
    hw = 0.8 * W
    for sx in (1, -1):
        x0, x1 = sorted((sx * hw, sx * (hw + 0.015)))
        b.box(x0, x1, 0.86, 0.98, -6.0, 3.6, c["stripe"])                       # cheat line
        b.box(x0, x1, 0.80, 0.86, -6.0, 3.6, c.get("stripe2", c["stripe"]))
        for i in range(5):                                                      # oval cabin windows
            z = -2.6 + i * 0.85
            b.box(x0, x1, 1.12, 1.36, z, z + 0.34, "black_stained_glass")
        xa, xb = sorted((sx * 0.46, sx * 0.475))
        b.box(xa, xb, 1.18, 1.36, 2.35, 2.8, "black_concrete")                  # cockpit side window
        b.box(x0, x1, 0.78, 1.5, 1.6, 2.1, "light_gray_concrete")               # airstair door outline
    # wings: low, swept, winglets
    root = (0.0, 0.62, -0.6)
    span, back = b.swept(root, 25.0, 4.0, [(0.0, 2.6, 1.9, 0.14), (2.6, 5.4, 1.1, 0.12)], c["wing"])
    for sx in (1, -1):
        tip = tuple(root[i] + span[i] * 5.35 + back[i] * 0.5 for i in range(3))
        b.add((sx * tip[0], tip[1] + 0.35, tip[2]), (0.06, 0.7, 0.6), c["stripe"], [("y", sx * 34), ("z", -sx * 10)])
        nv = tuple(root[i] + span[i] * 5.3 + back[i] * 0.15 for i in range(3))
        b.add((sx * nv[0], nv[1] + 0.08, nv[2]), (0.1, 0.08, 0.14), "lime_concrete" if sx > 0 else "red_concrete")
    b.box(-0.42, 0.42, 0.42, 0.62, -2.6, -0.5, body)                            # wing box fairing
    # rear-mounted engines on pylons
    for sx in (1, -1):
        x = sx * 0.95
        b.nacelle(x, 1.38, -3.5, 1.7, 0.3, c.get("engine", "light_gray_concrete"))
        b.box(min(sx * 0.4, sx * 0.7), max(sx * 0.4, sx * 0.7), 1.33, 1.43, -4.8, -3.9, body)
    # T-tail: swept fin + stabiliser on top
    b.fin(1.3, -4.2, 2.2, 35.0, 1.8, 1.0, 0.12, c["fin"], rows=6, cols=2)
    top_z = -4.2 - (2.2 - 0.18) * math.tan(math.radians(35))
    b.swept((0.0, 3.52, top_z + 0.05), 22.0, 2.0, [(0.0, 1.9, 0.8, 0.09)], c["wing"])
    # gear
    b.box(-0.05, 0.05, 0.2, 0.6, 3.2, 3.3, "gray_concrete")
    b.box(-0.08, 0.08, 0.0, 0.26, 3.1, 3.4, "black_concrete")
    for sx in (1, -1):
        b.box(sx * 0.6 - 0.12, sx * 0.6 + 0.12, 0.0, 0.3, -2.0, -1.55, "black_concrete")
        b.box(sx * 0.6 - 0.04, sx * 0.6 + 0.04, 0.28, 0.6, -1.82, -1.72, "gray_concrete")
    return b.P


def b2_spirit(c, b):
    """B-2 Spirit flying wing: span ~33, length ~13.2, 33 deg leading edge, double-W trailing edge,
    raised centre body, engine humps with dorsal intakes, 4 cockpit windows, no tail."""
    body, dark = c["body"], c.get("dark", "black_concrete")
    NOSE, SW = 7.0, math.tan(math.radians(33.0))
    HALF = 16.5
    TE = [(0.0, -6.2), (4.1, -3.7), (7.9, -6.2), (HALF, -4.4)]   # trailing-edge vertices (|x|, z)
    BOT = 0.75

    def le(x):
        return NOSE - SW * x

    def te(x):
        for (x0, z0), (x1, z1) in zip(TE, TE[1:]):
            if x0 <= x <= x1:
                return z0 + (z1 - z0) * (x - x0) / (x1 - x0)
        return TE[-1][1]

    def thick(x):
        return 0.34 - 0.2 * (x / HALF)

    # chordwise strips (kept a little inside the edges; edge bands below give the clean outline)
    n = 22
    for i in range(n):
        xa, xb = HALF * i / n, HALF * (i + 1) / n
        zf = le(xb) - 0.05
        zb = max(te(xa), te(xb), *[z for x, z in TE if xa <= x <= xb]) + 0.05
        t = thick((xa + xb) / 2)
        for sx in (1, -1):
            x0, x1 = sorted((sx * xa, sx * xb))
            b.box(x0, x1, BOT, BOT + t, zb, zf, body)

    # straight edge bands (rotated thin plates whose outer edge is exactly the outline)
    def band(p1, p2, width, interior_dz):
        (x1, z1), (x2, z2) = p1, p2
        L = math.hypot(x2 - x1, z2 - z1)
        dx, dz = (x2 - x1) / L, (z2 - z1) / L
        nx, nz = -dz, dx                       # a normal; flip it toward the interior
        if nz * interior_dz < 0:
            nx, nz = -nx, -nz
        mx, mz = (x1 + x2) / 2 + nx * width / 2, (z1 + z2) / 2 + nz * width / 2
        a = math.degrees(math.atan2(-dz, dx))
        t = thick(abs((x1 + x2) / 2)) * 0.92
        for sx in (1, -1):
            b.add((sx * mx, BOT + t / 2, mz), (L, t, width), body, [("y", sx * a)])

    band((0.0, NOSE), (HALF, le(HALF)), 0.9, -1)            # leading edge (interior is aft)
    for p1, p2 in zip(TE, TE[1:]):
        band(p1, p2, 0.9, +1)                                # trailing edge (interior is forward)

    # raised centre body (stacked layers tapering fore and aft) + cockpit bump
    top = BOT + thick(0)
    for hw, z0, z1 in [(3.0, -4.0, 4.6), (2.2, -3.4, 5.0), (1.4, -2.6, 5.4), (0.8, -1.2, 4.9)]:
        b.box(-hw, hw, top, top + 0.3, z0, z1, body)
        top += 0.3
    # sloped windscreen fairing ahead of the bump
    p0, p1 = (4.6, top - 0.02), (5.7, top - 0.42)
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    ang = math.degrees(math.atan2(p0[1] - p1[1], p1[0] - p0[0]))
    b.add((0, (p0[1] + p1[1]) / 2 - 0.08, (p0[0] + p1[0]) / 2), (1.5, 0.16, L), body, [("x", ang)])
    # four dark cockpit windows: two forward, two side, on the sloped front
    for xa, xb in [(0.04, 0.34), (0.40, 0.68)]:
        for sx in (1, -1):
            x0, x1 = sorted((sx * xa, sx * xb))
            b.add(((x0 + x1) / 2, (p0[1] + p1[1]) / 2 + 0.01, (p0[0] + p1[0]) / 2 + 0.12),
                  (x1 - x0, 0.03, L * 0.55), dark, [("x", ang)])

    # engine humps with dorsal intakes and exhausts
    ptop = BOT + thick(3.6)
    for sx in (1, -1):
        x = sx * 3.6
        b.box(x - 1.0, x + 1.0, ptop, ptop + 0.32, -3.3, 3.3, body)
        b.box(x - 0.65, x + 0.65, ptop + 0.32, ptop + 0.62, -2.6, 2.6, body)
        b.box(x - 0.55, x + 0.55, ptop + 0.5, ptop + 0.63, 1.9, 2.6, dark)            # intake
        b.box(x - 0.85, x + 0.85, ptop + 0.2, ptop + 0.33, 2.7, 3.3, dark)            # intake lip
        b.box(x - 0.6, x + 0.6, ptop + 0.2, ptop + 0.33, -3.3, -2.6, dark)            # exhaust trough

    # landing gear (belly doors read well from below)
    b.box(-0.06, 0.06, 0.2, BOT, 3.6, 3.72, "light_gray_concrete")
    b.box(-0.14, 0.14, 0.0, 0.32, 3.45, 3.85, dark)
    for sx in (1, -1):
        x = sx * 3.2
        b.box(x - 0.06, x + 0.06, 0.25, BOT, -0.6, -0.48, "light_gray_concrete")
        b.box(x - 0.2, x + 0.2, 0.0, 0.42, -1.0, -0.1, dark)
        b.box(x - 0.5, x + 0.5, BOT - 0.03, BOT, -1.6, 0.4, "black_concrete")         # gear-bay door outline
    return b.P
