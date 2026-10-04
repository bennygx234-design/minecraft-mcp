"""Flight profile: speed, altitude, pitch and bank along the route, sampled once per game tick.

Produces TIMELINE: list of per-tick states from departure (pushback start) to the stop at the stand:
    dict(x, y, z, yaw, pitch, roll, phase, s)
yaw/pitch are Minecraft entity angles of the plane (pitch < 0 = nose up); roll in degrees (+ = right
wing down). Roll is shown through the display transformations, updated as keyframes every RK ticks
(interpolated by the client), so TIMELINE roll is the piecewise-linear roll the client actually shows.
"""
import math
import route
import model as MD

RK = 4                 # roll keyframe spacing (ticks) = client interpolation_duration
ROLL_STEP = 2.0        # roll levels (deg)
G_EFF = 0.0387         # bank = atan(v^2 * kappa / G_EFF): ~26 deg in the orbit at 1.15 b/t
MAX_BANK = 32.0

ORBIT_Y = 222.0
TD_Z = 78.0            # touchdown point on 22R (z)
ROT_Z = 87.0           # rotation point on 04L (2/3 of the runway, s = 223)
GAMMA_FINAL = 12.0     # final approach path angle (deg); see notes (vertical scale is exaggerated)
FINAL_PITCH = 1.5      # nose slightly up on the final
FLARE_LEN = 34.0
GAMMA_CLIMB1 = 13.0   # initial climb gradient (clears the city edge north/east of the runway)


def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def ramp(s, s0, s1, a, b):
    return a + (b - a) * smooth((s - s0) / (s1 - s0)) if s1 != s0 else (b if s >= s1 else a)


# ------------------------------------------------------------------ speed profile on a path
def speed_profile(path, zones, a_up, a_dn, v0=0.0, v_end=0.0, ds=0.25):
    """zones: list of (s_from, vmax) (piecewise constant from s_from); a_up/a_dn: f(s) -> accel limit
    (blocks/tick^2). Returns sample list of (s, v)."""
    L = path.length
    n = int(L / ds) + 1
    S = [min(L, i * ds) for i in range(n)]
    if S[-1] < L:
        S.append(L)

    def vmax(s):
        v = zones[0][1]
        for s0, vv in zones:
            if s >= s0:
                v = vv
        return v
    V = [vmax(s) for s in S]
    V[0] = min(V[0], v0)
    for i in range(1, len(S)):                    # forward (acceleration) pass
        h = S[i] - S[i - 1]
        V[i] = min(V[i], math.sqrt(V[i - 1] ** 2 + 2 * a_up(S[i - 1]) * h))
    V[-1] = min(V[-1], v_end)
    for i in range(len(S) - 2, -1, -1):           # backward (braking) pass
        h = S[i + 1] - S[i]
        V[i] = min(V[i], math.sqrt(V[i + 1] ** 2 + 2 * a_dn(S[i]) * h))
    return S, V


def time_samples(S, V, smooth_ticks=8):
    """invert s(t) at integer ticks; then smooth the per-tick speed (gaussian) for gentle jerk."""
    T = [0.0]
    for i in range(1, len(S)):
        vm = 0.5 * (V[i] + V[i - 1])
        h = S[i] - S[i - 1]
        T.append(T[-1] + (h / vm if vm > 1e-9 else 0.0))
    total = T[-1]
    nt = int(math.ceil(total))
    out, j = [], 0
    for t in range(nt + 1):
        while j < len(T) - 2 and T[j + 1] < t:
            j += 1
        if t >= total:
            out.append(S[-1]); continue
        u = (t - T[j]) / (T[j + 1] - T[j]) if T[j + 1] > T[j] else 0
        out.append(S[j] + (S[j + 1] - S[j]) * u)
    if smooth_ticks and len(out) > 3:
        d = [out[i + 1] - out[i] for i in range(len(out) - 1)]
        sig = smooth_ticks
        k = [math.exp(-0.5 * (i / sig) ** 2) for i in range(-3 * sig, 3 * sig + 1)]
        sm = []
        for i in range(len(d)):
            acc = w = 0.0
            for jj, kk in enumerate(k):
                ii = i + jj - 3 * sig
                if 0 <= ii < len(d):
                    acc += d[ii] * kk; w += kk
                else:
                    w += kk                 # outside = standing still (keeps starts/stops soft)
            sm.append(acc / w)
        scale = (out[-1] - out[0]) / sum(sm)
        s = [out[0]]
        for v in sm:
            s.append(s[-1] + v * scale)
        # pad so the smoothed motion fully settles
        out = s
    return out


# ------------------------------------------------------------------ vertical profile (main path)
def vertical_main(p):
    mk = p.marks
    s_rot = LINEUP_S(p, ROT_Z)
    s_lo = s_rot + 26.0
    s_oi, s_oo = mk["orbit_in"], mk["orbit_out"]
    s_fin = mk["final"]
    s_td = s_fin + (TD_Z - route.FINAL_START_Z)
    s_fl = s_td - FLARE_LEN

    def build(gc, gd):
        """gamma(s) in degrees for climb gc and descent gd; returns (gamma_fn, pitch_fn)"""
        def gamma(s):
            if s < s_lo:
                return 0.0
            if s < s_oi:
                g = ramp(s, s_lo, s_lo + 60, 0.0, GAMMA_CLIMB1)
                if s > s_lo + 260:
                    g = ramp(s, s_lo + 260, s_lo + 340, GAMMA_CLIMB1, gc)
                return min(g, ramp(s, s_oi - 130, s_oi, gc, 0.0)) if s > s_oi - 130 else g
            if s < s_oo:
                return 0.0
            if s < s_fl:
                g = ramp(s, s_oo, s_oo + 90, 0.0, -gd)
                if s > s_fin - 90:
                    g = ramp(s, s_fin - 90, s_fin + 40, -gd, -GAMMA_FINAL)
                return g
            if s < s_td:
                return ramp(s, s_fl, s_td, -GAMMA_FINAL, -0.8)
            return 0.0
        return gamma

    def integrate(gamma, s0, y0, s1, ds=0.25):
        y, s = y0, s0
        while s < s1 - 1e-9:
            h = min(ds, s1 - s)
            y += math.tan(math.radians(0.5 * (gamma(s) + gamma(s + h)))) * h
            s += h
        return y

    # solve climb gamma so y(orbit_in) = ORBIT_Y, then descent gamma so y(touchdown) = ground
    def climb_err(gc):
        return integrate(build(gc, 5.0), s_lo, MD.CENTRE_GROUND, s_oi) - ORBIT_Y
    gc = 10.0
    for _ in range(40):
        e0 = climb_err(gc)
        e1 = climb_err(gc + 0.01)
        gc -= e0 / ((e1 - e0) / 0.01)
        if abs(e0) < 1e-4:
            break

    def desc_err(gd):
        return integrate(build(gc, gd), s_oo, ORBIT_Y, s_td) - MD.CENTRE_GROUND
    gd = 4.0
    for _ in range(40):
        e0 = desc_err(gd)
        e1 = desc_err(gd + 0.01)
        gd -= e0 / ((e1 - e0) / 0.01)
        if abs(e0) < 1e-4:
            break
    gamma = build(gc, gd)

    # tabulate y(s)
    ds = 0.25
    n = int(p.length / ds) + 2
    Ys = [0.0] * n
    y = MD.CENTRE_GROUND
    for i in range(n):
        s = i * ds
        if i:
            y += math.tan(math.radians(0.5 * (gamma(s - ds) + gamma(s)))) * ds
        if s <= s_lo or s >= s_td:
            y = MD.CENTRE_GROUND
        Ys[i] = y

    def alt(s):
        i = max(0, min(n - 2, int(s / ds)))
        u = (s - i * ds) / ds
        return Ys[i] + (Ys[i + 1] - Ys[i]) * u

    def pitch(s):
        """nose-up attitude (deg)"""
        if s < s_rot:
            return 0.0
        if s < s_lo:
            return ramp(s, s_rot, s_lo, 0.0, 8.0)                       # rotation on the main gear
        if s < s_oi:
            th = gamma(s) + ramp(s, s_lo, s_lo + 60, 8.0, 2.0)
            return th
        if s < s_oo:
            return 2.0
        if s < s_fl:
            a = 2.0 if s < s_fin - 90 else ramp(s, s_fin - 90, s_fin + 40, 2.0, GAMMA_FINAL + FINAL_PITCH)
            return gamma(s) + a
        if s < s_td:
            return ramp(s, s_fl, s_td, FINAL_PITCH, 4.5)               # flare
        return ramp(s, s_td, s_td + 32, 4.5, 0.0)                      # derotate, nose wheel down
    info = dict(gamma_climb=gc, gamma_desc=gd, s_rot=s_rot, s_lo=s_lo, s_td=s_td, s_fl=s_fl)
    return alt, pitch, info


def LINEUP_S(p, z):
    """arc length on the main path where it crosses world z (first time, northbound on 04L)"""
    return route.LINEUP[1] - z


# ------------------------------------------------------------------ assemble the timeline
def build():
    pb = route.build_pushback()
    tx = route.build_taxi((pb.end[0], pb.end[1], pb.end[2] + 180.0))
    mn, rinfo = route.build_main()
    mk = mn.marks
    alt, pitch, vinfo = vertical_main(mn)
    s_td, s_lo, s_rot = vinfo["s_td"], vinfo["s_lo"], vinfo["s_rot"]

    # pushback: slow, symmetric
    S, V = speed_profile(pb, [(0, 0.13)], lambda s: 0.0015, lambda s: 0.0015)
    pb_s = time_samples(S, V, 6)
    # taxi out: 0.32 straight, 0.13 in the tight turns
    c1 = tx.marks["conn"]
    zones = [(0, 0.4), (c1 - 9.5, 0.14), (c1 + 0.5, 0.14)]
    S, V = speed_profile(tx, zones, lambda s: 0.003, lambda s: 0.0035)
    tx_s = time_samples(S, V, 6)
    # main: takeoff roll at constant thrust, then air speeds, landing roll, taxi in
    a_roll = 1.05 ** 2 / (2 * s_rot)
    zones = [(0, 1.27), (mk["orbit_in"] - 120, 1.15), (mk["orbit_out"] + 40, 1.32),
             (mk["final"] - 140, 1.0), (vinfo["s_fl"] - 30, 0.9), (s_td + 1, 0.9),
             (mk["exit"] - 2, 0.2), (mk["conn_in"] + 2, 0.3), (mk["stand_line"] - 12, 0.16)]

    def a_up(s):
        return a_roll if s < s_rot else (0.0016 if s < s_td else 0.003)

    def a_dn(s):
        return 0.0055 if s > s_td else 0.0014
    S, V = speed_profile(mn, zones, a_up, a_dn)
    mn_s = time_samples(S, V, 8)

    TL = []

    def emit(path, svals, phase, vert=None, pitchf=None, reverse=False):
        for s in svals:
            x, z, yaw, k = path.at(s)
            yaw_plane = yaw + 180.0 if reverse else yaw
            y = vert(s) if vert else MD.CENTRE_GROUND
            th = pitchf(s) if pitchf else 0.0
            TL.append(dict(x=x, y=y, z=z, yaw=yaw_plane, pitch=-th, kappa=0.0 if reverse else k,
                           phase=phase, s=s, airborne=bool(vert) and s_lo < s < s_td))

    emit(pb, pb_s, "pushback", reverse=True)
    for _ in range(50):                                     # tug disconnect, engine start
        TL.append(dict(TL[-1], phase="hold"))
    emit(tx, tx_s, "taxi")
    for _ in range(60):                                     # line up and wait
        TL.append(dict(TL[-1], phase="lineup"))
    phase_of = lambda s: ("takeoff" if s < s_lo else "climb" if s < mk["orbit_in"] else "orbit"
                          if s < mk["orbit_out"] else "descent" if s < mk["final"] else "final"
                          if s < s_td else "landing" if s < mk["exit"] else "taxi_in")
    i0 = len(TL)
    emit(mn, mn_s, "main", vert=alt, pitchf=pitch)
    for st in TL[i0:]:
        st["phase"] = phase_of(st["s"])

    # yaw continuity (unwrap) then wrap for output
    for i in range(1, len(TL)):
        d = (TL[i]["yaw"] - TL[i - 1]["yaw"] + 180) % 360 - 180
        TL[i]["yaw"] = TL[i - 1]["yaw"] + d

    # bank: from turn rate (coordinated-turn look), smoothed, clamped near the ground, keyframed
    n = len(TL)
    tgt = []
    for i in range(n):
        st = TL[i]
        v = math.hypot(TL[min(n - 1, i + 1)]["x"] - st["x"], TL[min(n - 1, i + 1)]["z"] - st["z"])
        if st["phase"] in ("climb", "orbit", "descent", "final", "takeoff") and st.get("airborne"):
            b = math.degrees(math.atan(v * v * st["kappa"] / G_EFF))
            b = max(-MAX_BANK, min(MAX_BANK, b))
        else:
            b = 0.0
        tgt.append(b)
    # gaussian smoothing (sigma 12 ticks) then rate limit 0.5 deg/tick
    sig = 12
    ker = [math.exp(-0.5 * (j / sig) ** 2) for j in range(-3 * sig, 3 * sig + 1)]
    sm = []
    for i in range(n):
        acc = w = 0.0
        for j, kk in enumerate(ker):
            ii = min(n - 1, max(0, i + j - 3 * sig))
            acc += tgt[ii] * kk; w += kk
        sm.append(acc / w)
    for i in range(n):                                      # wing-tip ground clearance clamp
        h = TL[i]["y"] - MD.GROUND_Y - 2.0
        lim = 0.0 if h <= 0 else math.degrees(math.asin(min(1.0, h / 12.0)))
        if not TL[i].get("airborne"):
            lim = 0.0
        sm[i] = max(-lim, min(lim, sm[i]))
    # keyframes every RK ticks at ROLL_STEP levels, at most one level per keyframe
    levels = {}
    cur = 0.0
    for t0 in range(0, n, RK):
        want = sm[min(n - 1, t0 + RK)]
        lv = ROLL_STEP * round(want / ROLL_STEP)
        lv = max(cur - ROLL_STEP, min(cur + ROLL_STEP, lv))
        if t0 + RK >= n - 1:
            lv = 0.0 if abs(cur) <= ROLL_STEP else cur - math.copysign(ROLL_STEP, cur)
        if lv != cur:
            levels[t0] = (cur, lv)
            cur = lv
    assert cur == 0.0, cur
    cur = 0.0
    for i in range(n):
        k0 = (i // RK) * RK
        if k0 in levels:
            a, b = levels[k0]
            v = a + (b - a) * (i - k0) / RK
        else:
            v = cur
        TL[i]["roll"] = v
        TL[i]["roll_kf"] = levels[i][1] if i in levels else None
        if i - k0 == RK - 1 and k0 in levels:
            cur = levels[k0][1]
    info = dict(rinfo, **vinfo, n=n, keyframes=len(levels),
                pushback_ticks=len(pb_s), taxi_ticks=len(tx_s), main_ticks=len(mn_s))
    return TL, info, (pb, tx, mn)


if __name__ == "__main__":
    import time
    t = time.time()
    TL, info, _ = build()
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in info.items()})
    ph = {}
    for i, st in enumerate(TL):
        ph.setdefault(st["phase"], [i, i])[1] = i
    for k, (a, b) in ph.items():
        print(f"{k:9s} ticks {a:5d}..{b:5d}  ({(b - a + 1) / 20:5.1f} s)")
    print("total", len(TL), "ticks =", round(len(TL) / 20, 1), "s;  max |roll|", max(abs(s["roll"]) for s in TL))
    for i in range(0, len(TL), 100):
        st = TL[i]
        print(f"{i:5d} {st['phase']:8s} ({st['x']:7.1f},{st['y']:6.1f},{st['z']:7.1f}) yaw {st['yaw'] % 360:6.1f} "
              f"pitch {st['pitch']:5.1f} roll {st['roll']:5.1f}")
    print(round(time.time() - t, 1), "s")
