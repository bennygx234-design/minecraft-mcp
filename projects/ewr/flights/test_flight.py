"""Full scheduled-flight test with an armor-stand passenger.

    python test_flight.py            # waits for the next scheduled departure, logs every ~20 ticks

1. summons an invisible armor stand at gate A10 tagged ewr_flt_booked + ewr_flt_test
2. waits for the next scheduled departure; logs the passenger, its vehicle and the plane (brain)
   every ~20 game ticks until the plane is parked again and the passenger released
3. checks: plane path vs the precomputed timeline, passenger rode a seat the whole flight, live
   block probes (execute if block ... air) at the plane centre, nose, tail and both wing tips
   along the logged path, passenger released at the gate; tick query before/during/after
Writes test_log.json.
"""
import json
import math
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, r"C:\Users\benny\minecraft-mcp")
sys.path.insert(0, HERE)
from mcmcp.engine import Engine  # noqa: E402
import model as MD  # noqa: E402

e = Engine()
meta = json.load(open(os.path.join(HERE, "meta.json")))
TL = json.load(open(os.path.join(HERE, "timeline.json")))
B, A, GATE = meta["BOARD_T"], meta["A"], meta["GATE"]
NUM = r"(-?[\d.]+(?:E-?\d+)?)"


def vec(s):
    return [float(v) for v in re.findall(NUM + r"[df]", s)]


def score(target, obj):
    r = e.cmd(f"scoreboard players get {target} {obj}")
    m = re.search(r"has (-?\d+)", r)
    return int(m.group(1)) if m else None


def tickq():
    r = e.cmd("tick query")
    m = re.search(r"Average time per tick: ([\d.]+)ms.*P50: ([\d.]+)ms P95: ([\d.]+)ms P99: ([\d.]+)ms", r, re.S)
    return dict(avg=float(m.group(1)), p50=float(m.group(2)), p95=float(m.group(3)), p99=float(m.group(4))) if m else r


log = dict(tick_before=tickq())
print("tick before:", log["tick_before"])
e.cmd("kill @e[type=armor_stand,tag=ewr_flt_test]")
gx, gy, gz = GATE
print(e.cmd(f'summon armor_stand {gx} {gy} {gz} {{Tags:["ewr_flt","ewr_flt_test","ewr_flt_booked"],'
            f'Invisible:1b,Invulnerable:1b,NoGravity:1b,Small:1b,CustomName:"Test passenger"}}'))
clock = score("#clock", "ewrf_t")
wait = (B - clock) % meta.get("PERIOD", 4800)
print(f"clock {clock}: next departure in {wait} ticks ({wait / 20:.0f} s)")
samples = []
t0 = time.time()
departed = released = False
during = []
while True:
    time.sleep(0.95)
    ft = None
    r = e.cmd("execute as @e[type=marker,tag=ewr_flt_brain] run scoreboard players get @s ewrf_ft")
    fts = [int(v) for v in re.findall(r"has (\d+)", r)]
    stand = vec(e.cmd("data get entity @e[type=armor_stand,tag=ewr_flt_test,limit=1] Pos"))
    tags = e.cmd("data get entity @e[type=armor_stand,tag=ewr_flt_test,limit=1] Tags")
    onv = "passed" in e.cmd("execute as @e[type=armor_stand,tag=ewr_flt_test] on vehicle if entity @s[tag=ewr_flt_seat]")
    pax_id = score("@e[type=armor_stand,tag=ewr_flt_test,limit=1]", "ewrf_id")
    brain = None
    if pax_id is not None:
        bsel = f"@e[type=marker,tag=ewr_flt_brain,scores={{ewrf_id={pax_id}}},limit=1]"
        bp = vec(e.cmd(f"data get entity {bsel} Pos"))
        br = vec(e.cmd(f"data get entity {bsel} Rotation"))
        ft = score(bsel, "ewrf_ft")
        brain = dict(pos=bp, rot=br, ft=ft)
    elif departed and fts:
        ft = max(fts)
    s = dict(t=round(time.time() - t0, 2), stand=stand, onv=onv, pax="ewr_flt_pax" in tags,
             booked="ewr_flt_booked" in tags, brain=brain)
    samples.append(s)
    if brain and not departed:
        departed = True
        print("departed: passenger", "seated" if onv else "NOT seated", "flight", pax_id)
    if brain and len(samples) % 10 == 0:
        i = brain["ft"] - B
        ph = TL[i]["phase"] if 0 <= i < len(TL) else "parked"
        print(f"  t+{s['t']:6.1f}s ft {brain['ft']:5d} {ph:9s} plane ({brain['pos'][0]:7.1f},{brain['pos'][1]:6.1f},"
              f"{brain['pos'][2]:7.1f}) passenger ({stand[0]:7.1f},{stand[1]:6.1f},{stand[2]:7.1f}) on seat {onv}")
        if ph in ("orbit", "climb", "descent") and len(during) < 3:
            during.append(tickq())
    if departed and not s["pax"] and not brain:
        released = True
        print("released at", stand)
        break
    if time.time() - t0 > wait / 20 + 260:
        print("TIMEOUT")
        break

log["tick_during"] = during
log["tick_after"] = tickq()
log["samples"] = samples
print("tick during:", during)
print("tick after:", log["tick_after"])

# ---- analysis
fl = [s for s in samples if s["brain"]]
dev = []
for s in fl:
    i = s["brain"]["ft"] - B
    if 0 <= i < len(TL):
        st = TL[i]
        p = s["brain"]["pos"]
        dev.append(math.dist(p, (st["x"], st["y"], st["z"])))
seated = sum(1 for s in fl if s["onv"])
print(f"logged {len(fl)} in-flight samples; passenger on its seat in {seated}/{len(fl)}; "
      f"max deviation from plan {max(dev) if dev else -1:.3f} blocks")
ph_seen = sorted({TL[s['brain']['ft'] - B]['phase'] for s in fl if 0 <= s['brain']['ft'] - B < len(TL)})
print("phases seen:", ph_seen)
alts = [s["brain"]["pos"][1] for s in fl]
print(f"altitude range {min(alts):.1f}..{max(alts):.1f}")
orb = [s for s in fl if 0 <= s["brain"]["ft"] - B < len(TL) and TL[s["brain"]["ft"] - B]["phase"] == "orbit"]
if orb:
    rr = [math.hypot(s["brain"]["pos"][0] - 170.5, s["brain"]["pos"][2] + 134.5) for s in orb]
    print(f"orbit samples {len(orb)}: radius {min(rr):.1f}..{max(rr):.1f}, y {min(s['brain']['pos'][1] for s in orb):.1f}")
# live block probes: centre, nose, tail, wing tips (from the logged pose + planned roll)
probes = bad = 0
badl = []
for s in fl:
    i = s["brain"]["ft"] - B
    if not (0 <= i < len(TL)) or not TL[i].get("airborne"):
        continue
    (x, y, z), (yaw, pit) = s["brain"]["pos"], s["brain"]["rot"]
    M = MD.rot_matrix(yaw, pit, TL[i]["roll"])
    for off in ((0, 0, 0), (0, 0, 11.5), (0, 0, -11.7), (10.8, 0.9, -2.5), (-10.8, 0.9, -2.5), (0, 4.0, -10.5)):
        w = [x + sum(M[0][k] * off[k] for k in range(3)), y + sum(M[1][k] * off[k] for k in range(3)),
             z + sum(M[2][k] * off[k] for k in range(3))]
        r = e.cmd(f"execute positioned {w[0]:.2f} {w[1]:.2f} {w[2]:.2f} if block ~ ~ ~ #minecraft:air")
        probes += 1
        if "passed" not in r:
            bad += 1; badl.append((i, [round(v, 1) for v in w], r[:60]))
print(f"live block probes along the flown path: {probes}, non-air: {bad}", badl[:10])
end = samples[-1]["stand"]
print("passenger final position", end, "gate", GATE, "dist", round(math.dist(end, GATE), 2) if end else None)
log.update(probes=probes, probes_bad=badl, max_dev=max(dev) if dev else None, seated=seated, n=len(fl),
           released=released, final=end)
json.dump(log, open(os.path.join(HERE, "test_log.json"), "w"), indent=0)
e.cmd("kill @e[type=armor_stand,tag=ewr_flt_test]")
