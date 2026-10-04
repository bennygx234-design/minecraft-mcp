"""Flight path geometry for ewr_flights (world coordinates, Minecraft yaw convention).

yaw: 0 = facing +z (south), 90 = -x (west), 180 = -z (north), -90 = +x (east).
direction(yaw) = (-sin yaw, cos yaw). A right turn increases yaw (curvature kappa > 0).
Paths are built from straight lines and turns (entry clothoid - arc - exit clothoid), so curvature
(and therefore yaw rate and bank) is continuous along every leg.
"""
import math

DS = 0.02  # integration step (blocks)


def wrap(a):
    return (a + 180.0) % 360.0 - 180.0


class Path:
    """Samples every DS blocks: s, x, z, yaw (deg, motion direction), kappa (rad/block, + = right)."""

    def __init__(self, x, z, yaw, reverse=False):
        self.reverse = reverse
        self.S = [0.0]; self.X = [x]; self.Z = [z]; self.Y = [yaw]; self.K = [0.0]
        self.marks = {}

    @property
    def end(self):
        return self.X[-1], self.Z[-1], self.Y[-1]

    @property
    def length(self):
        return self.S[-1]

    def mark(self, name):
        self.marks[name] = self.S[-1]

    def _step(self, kappa_fn, L):
        n = max(1, int(round(L / DS)))
        h = L / n
        for i in range(n):
            k0, k1 = kappa_fn(i * h), kappa_fn((i + 1) * h)
            yaw0 = self.Y[-1]
            yaw1 = yaw0 + math.degrees(0.5 * (k0 + k1) * h)
            ym = math.radians(0.5 * (yaw0 + yaw1))
            self.X.append(self.X[-1] - math.sin(ym) * h)
            self.Z.append(self.Z[-1] + math.cos(ym) * h)
            self.Y.append(yaw1)
            self.K.append(k1)
            self.S.append(self.S[-1] + h)

    def line(self, L):
        if L < 0:
            raise ValueError(f"negative line length {L:.2f}")
        if L > 0:
            self._step(lambda u: 0.0, L)
        return self

    def turn(self, delta_deg, R, Ls):
        """signed heading change (deg, + = right), radius R, clothoid length Ls at each end"""
        d = math.radians(abs(delta_deg))
        sg = 1.0 if delta_deg > 0 else -1.0
        km = 1.0 / R
        if Ls * km > d:            # too short for a full arc: two clothoids meeting at a lower peak
            Ls = max(d * R, 1e-6)      # each clothoid turns d/2 = Ls*km/2
            La = 0.0
        else:
            La = (d - Ls * km) / km
        self._step(lambda u: sg * km * u / Ls, Ls)
        if La > 0:
            self._step(lambda u: sg * km, La)
        self._step(lambda u: sg * km * (1 - u / Ls), Ls)
        return self

    def at(self, s):
        """interpolated (x, z, yaw, kappa) at arc length s"""
        s = max(0.0, min(self.S[-1], s))
        i = min(len(self.S) - 2, int(s / DS))
        while i > 0 and self.S[i] > s:
            i -= 1
        while i < len(self.S) - 2 and self.S[i + 1] < s:
            i += 1
        s0, s1 = self.S[i], self.S[i + 1]
        u = 0.0 if s1 == s0 else (s - s0) / (s1 - s0)
        lerp = lambda A: A[i] + (A[i + 1] - A[i]) * u
        return lerp(self.X), lerp(self.Z), lerp(self.Y), lerp(self.K)

    def first_s(self, pred, start=0.0):
        i0 = int(start / DS)
        for i in range(i0, len(self.S)):
            if pred(self.X[i], self.Z[i], self.Y[i]):
                return self.S[i]
        return None


def solve(build, x0, residual, tol=1e-3, iters=40):
    """Newton solve with finite differences: build(params) -> path, residual(path) -> list (same len as x0)."""
    x = list(x0)
    for _ in range(iters):
        p = build(x)
        r = residual(p)
        if max(abs(v) for v in r) < tol:
            return x, p
        J = []
        for j in range(len(x)):
            xp = list(x); h = 1e-3 * max(1.0, abs(x[j]))
            xp[j] += h
            rp = residual(build(xp))
            J.append([(rp[i] - r[i]) / h for i in range(len(r))])
        # solve J^T (columns = params) * dx = -r  (small dense system, Gauss)
        n = len(x)
        A = [[J[j][i] for j in range(n)] + [-r[i]] for i in range(n)]
        for c in range(n):
            piv = max(range(c, n), key=lambda rr: abs(A[rr][c]))
            A[c], A[piv] = A[piv], A[c]
            for rr in range(n):
                if rr != c and A[c][c] != 0:
                    f = A[rr][c] / A[c][c]
                    A[rr] = [a - f * b for a, b in zip(A[rr], A[c])]
        dx = [A[i][n] / A[i][i] for i in range(n)]
        x = [a + b for a, b in zip(x, dx)]
    p = build(x)
    raise RuntimeError(f"solve did not converge: x={x} r={residual(p)}")


def clone(p):
    q = Path(0, 0, 0, p.reverse)
    q.S, q.X, q.Z, q.Y, q.K = list(p.S), list(p.X), list(p.Z), list(p.Y), list(p.K)
    q.marks = dict(p.marks)
    return q


def solve1(base, add, x0, resid, tol=1e-4, iters=30):
    """1-D secant solve: add(clone(base), x) -> path; resid(path) -> float. Returns (x, path)."""
    def f(x):
        p = add(clone(base), x)
        return resid(p), p
    a, (fa, pa) = x0, f(x0)
    b = x0 + max(0.5, abs(x0) * 0.01)
    fb, pb = f(b)
    for _ in range(iters):
        if abs(fb) < tol:
            return b, pb
        if fb == fa:
            break
        c = b - fb * (b - a) / (fb - fa)
        a, fa = b, fb
        b = c
        fb, pb = f(b)
    if abs(fb) < tol * 10:
        return b, pb
    raise RuntimeError(f"solve1 failed x={b} r={fb}")


def solve2(base, add, x0, resid, tol=1e-4, iters=30):
    """2-D Newton (finite differences): add(clone(base), (a, b)) -> path; resid -> (r1, r2)."""
    x = list(x0)
    for _ in range(iters):
        p = add(clone(base), x)
        r = resid(p)
        if max(abs(v) for v in r) < tol:
            return x, p
        J = []
        for j in range(2):
            xp = list(x); xp[j] += 0.05
            rp = resid(add(clone(base), xp))
            J.append([(rp[i] - r[i]) / 0.05 for i in range(2)])
        # J[j][i] = d r_i / d x_j
        a11, a12, a21, a22 = J[0][0], J[1][0], J[0][1], J[1][1]
        det = a11 * a22 - a12 * a21
        dx0 = (-r[0] * a22 + r[1] * a12) / det
        dx1 = (-r[1] * a11 + r[0] * a21) / det
        m = max(abs(dx0), abs(dx1), 1e-9)
        f = min(1.0, 15.0 / m)
        x = [x[0] + f * dx0, x[1] + f * dx1]
    raise RuntimeError(f"solve2 failed x={x} r={r}")


def _ramp_to(self, k1, L):
    """curvature changes linearly from the current value to k1 over L (clothoid / compound transition)"""
    k0 = self.K[-1]
    self._step(lambda u: k0 + (k1 - k0) * u / L, L)
    return self


def _arc(self, L):
    k = self.K[-1]
    if L < 0:
        raise ValueError(f"negative arc length {L:.2f}")
    if L > 0:
        self._step(lambda u: k, L)
    return self


Path.ramp_to = _ramp_to
Path.arc = _arc
