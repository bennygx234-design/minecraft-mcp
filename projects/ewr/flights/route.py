"""Burj Khalifa Scenic Flight: the ground + air track (plan view), solved so every leg lands exactly
where it must (taxiway / runway centrelines, an orbit centred on the Burj, the final on 22R).

Airport frame (BRIEF.md): world = (60 + t, 64 + y, 310 - s). 04L centreline = world x 60.5 (block
centres), threshold z 310, north end z -25. Burj centre (170.5, -134.5).
"""
import math
from path import Path, clone, solve1, solve2

RWY_X = 60.5
TWY_X = 46.5                      # taxiway t = -14 centreline
CONN_OUT_Z = 264.5                # connector to the 04L threshold area (s = 46)
CONN_IN_Z = 192.5                 # connector at s = 118 (exit after landing on 22R)
LINEUP = (RWY_X, 257.5)           # line-up point (centre of the plane), facing north
STAND = (24.6, 194.5, 90.0)       # stand A10: plane centre + yaw (nose west, toward Terminal A)
BURJ = (170.5, -134.5)
ORBIT_R = 70.0
FINAL_START_Z = -322.0
TURN1_Z = 48.0                    # right turn starts here (just after lift-off)
CLIMB_WEST = 75.0                 # westbound climbing leg north of the Burj            # 22R final starts here (x = 60.5), ~400 blocks of straight final


def left_normal(yaw):
    r = math.radians(yaw)
    return math.cos(r), math.sin(r)


def orbit_centre(p, s0, s1, R):
    """mean centre of the constant-curvature part of a left orbit between arc lengths s0..s1"""
    cx = cz = n = 0
    for i in range(len(p.S)):
        if s0 <= p.S[i] <= s1 and abs(abs(p.K[i]) - 1.0 / R) < 1e-9:
            lx, lz = left_normal(p.Y[i])
            sg = -1 if p.K[i] < 0 else 1           # left turn: centre on the left
            cx += p.X[i] - sg * R * lx; cz += p.Z[i] - sg * R * lz; n += 1
    return cx / n, cz / n


def build_pushback():
    """reverse from the stand: tail moves east, then swings north; ends on the taxiway facing south"""
    x, z, yaw = STAND
    base = Path(x, z, yaw - 180.0, reverse=True)      # motion heading = east (-90)
    base.line(6.0)

    def add(p, R):
        return p.turn(-90.0, R, 4.0)
    R, p = solve1(base, add, 15.0, lambda p: p.end[0] - TWY_X)
    return p


def build_taxi(start):
    x, z, yaw = start                                 # plane yaw (forward)
    base = Path(x, z, yaw)
    # straight south on the taxiway, left turn east onto the connector, left turn north onto 04L
    R = 5.0

    def a1(p, L):
        return p.line(L).turn(-90.0, R, 3.0)
    L1, p1 = solve1(base, a1, 70.0, lambda p: p.end[1] - CONN_OUT_Z)
    p1.mark("conn")

    def a2(p, L):
        return p.line(L).turn(-90.0, R, 3.0)
    L2, p2 = solve1(p1, a2, 2.0, lambda p: p.end[0] - RWY_X)

    def a3(p, L):
        return p.line(L)
    L3, p3 = solve1(p2, a3, 0.5, lambda p: p.end[1] - LINEUP[1])
    return p3


def build_main():
    p = Path(LINEUP[0], LINEUP[1], 180.0)
    p.mark("lineup")
    p.line(LINEUP[1] - TURN1_Z)                       # takeoff roll + initial climb, north on 04L
    p.mark("turn1")
    p.turn(+90.0, 58.0, 40.0)                         # climbing right turn, out over the bay
    p.mark("east")
    base = clone(p)

    # east leg L3, then a climbing left loop (R4) around the Burj's east side that spirals straight
    # into the orbit (compound transition R4 -> 70), one full 360 deg orbit, roll-out heading south.
    # Solve (L3, R4) so the orbit circle is centred on the Burj; the loop's arc length follows from
    # the heading budget (E -> ... -> S after the orbit = 270 + 360 deg of left turn).
    LS4, LC, LO = 60.0, 50.0, 50.0
    L4 = CLIMB_WEST
    ko = -1.0 / ORBIT_R

    def add_orbit(q, v):
        L3, R4 = v
        k4 = -1.0 / R4
        q.line(L3)
        q.mark("t270")
        a1 = (math.pi - LS4 * abs(k4)) / abs(k4)              # left turn E -> N -> W
        q.ramp_to(k4, LS4).arc(a1).ramp_to(0.0, LS4)
        q.mark("westbound")
        q.line(L4)                                           # westbound climbing leg north of the Burj
        q.mark("loop2")
        turn = math.radians(90.0 + 360.0)
        used = LS4 * abs(k4) / 2 + LC * (abs(k4) + abs(ko)) / 2 + 2 * math.pi + LO * abs(ko) / 2
        A4 = (turn - used) / abs(k4)
        q.ramp_to(k4, LS4).arc(A4)
        q.mark("compound")
        q.ramp_to(ko, LC)
        q.mark("orbit_in")
        q.arc(2 * math.pi * ORBIT_R)
        q.mark("orbit_out")
        q.ramp_to(0.0, LO)
        q.mark("south_out")
        return q

    def r_orbit(q):
        cx, cz = orbit_centre(q, q.marks["orbit_in"], q.marks["orbit_out"], ORBIT_R)
        return cx - BURJ[0], cz - BURJ[1]
    (L3, L5), p = solve2(base, add_orbit, (90.0, 89.0), r_orbit, tol=1e-3)

    # exit south, descending right U-turn (R8) to a northbound leg west of the airport, right U-turn
    # (R=60) onto the 22R final: solve R8 so the final is on the centreline, L9 for its start.
    p.line(40.0)
    p.mark("u1")
    base = clone(p)

    def add_u(q, v):
        R8, L9 = v
        q.turn(+180.0, R8, 50.0)
        q.mark("north")
        q.line(L9)
        q.mark("u2")
        q.turn(+180.0, 60.0, 50.0)
        q.mark("final")
        return q
    (R8, L9), p = solve2(base, add_u, (80.0, 250.0),
                         lambda q: (q.end[0] - RWY_X, q.end[1] - FINAL_START_Z), tol=1e-3)
    base = clone(p)

    # final + landing roll on 22R, right turn onto the s=118 connector
    def add_exit(q, L):
        q.line(L)
        q.mark("exit")
        return q.turn(+90.0, 9.0, 4.0)
    L11, p = solve1(base, add_exit, 500.0, lambda q: q.end[1] - CONN_IN_Z)
    p.mark("conn_in")
    base = clone(p)

    # west along the connector to x=44, small S-bend onto the stand line z=194.5, stop at the stand
    def add_s(q, th):
        q.line(q.end[0] - 44.0)
        q.turn(-th, 14.0, 3.0)
        q.turn(+th, 14.0, 3.0)
        return q
    th, p = solve1(base, add_s, 10.0, lambda q: q.end[1] - STAND[1])
    p.mark("stand_line")
    base = clone(p)
    L16, p = solve1(base, lambda q, L: q.line(L), 10.0, lambda q: q.end[0] - STAND[0])
    p.mark("stop")
    info = dict(L3=L3, L5=L5, R8=R8, L9=L9, L11=L11, sbend=th, L16=L16)
    return p, info


if __name__ == "__main__":
    import time
    t = time.time()
    pb = build_pushback()
    print("pushback", round(pb.length, 2), [round(v, 3) for v in pb.end])
    tx = build_taxi((pb.end[0], pb.end[1], pb.end[2] + 180.0))
    print("taxi", round(tx.length, 2), [round(v, 3) for v in tx.end])
    m, info = build_main()
    print("main", round(m.length, 1), [round(v, 3) for v in m.end], {k: round(v, 2) for k, v in info.items()})
    for k, s in m.marks.items():
        x, z, y, kk = m.at(s)
        print(f"  {k:10s} s={s:7.1f}  ({x:7.1f}, {z:7.1f}) yaw {y:7.1f}")
    print("orbit centre", orbit_centre(m, m.marks["orbit_in"], m.marks["orbit_out"], ORBIT_R))
    print(round(time.time() - t, 1), "s")
