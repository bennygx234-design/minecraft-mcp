"""Sample every ridden plane's position ~every 5 ticks for N minutes and log speeds, throttle,
flying_speed, vehicle snap-back warnings and server tick time.  python speed_probe.py [minutes]"""
import math, re, sys, time
sys.path.insert(0, r"C:\Users\benny\minecraft-mcp")
from mcmcp.engine import Engine

e = Engine()
LOG = r"C:\Users\benny\minecraft-mcp\server\logs\latest.log"
mins = float(sys.argv[1]) if len(sys.argv) > 1 else 10
end = time.time() + mins * 60
prev = {}
best = {}
log_pos = len(open(LOG, encoding="utf-8", errors="replace").read())
last_tick = 0
while time.time() < end:
    t = time.time()
    r = e.cmd("execute as @e[type=happy_ghast,tag=ewr_plane,tag=!ewr_parked] run data get entity @s Pos")
    ids = e.cmd("execute as @e[type=happy_ghast,tag=ewr_plane,tag=!ewr_parked] run scoreboard players get @s ewr_id")
    vls = e.cmd("execute as @e[type=happy_ghast,tag=ewr_plane,tag=!ewr_parked] run scoreboard players get @s ewr_vl")
    thr = e.cmd("execute as @e[type=happy_ghast,tag=ewr_plane,tag=!ewr_parked] run scoreboard players get @s ewr_thr")
    names = re.findall(r"(.+?) has the following entity data: \[([-\d.]+)d, ([-\d.]+)d, ([-\d.]+)d\]", r)
    idl = [int(x) for x in re.findall(r"has (-?\d+) \[ewr_id\]", ids)]
    vl = [int(x) for x in re.findall(r"has (-?\d+) \[ewr_vl\]", vls)]
    th = [int(x) for x in re.findall(r"has (-?\d+) \[ewr_thr\]", thr)]
    for k, (nm, x, y, z) in enumerate(names):
        pid = idl[k] if k < len(idl) else nm
        p = (float(x), float(y), float(z))
        if pid in prev:
            (pp, pt) = prev[pid]
            dt = t - pt
            v = math.dist(p, pp) / dt
            fs = vl[k] / 1000 if k < len(vl) else None
            key = (nm.split("has")[0].strip(), pid)
            if v > best.get(key, (0,))[0]:
                best[key] = (v, fs, th[k] if k < len(th) else None)
            if v > 30:
                print(f"{time.strftime('%H:%M:%S')} {nm.strip()} id{pid} {v:6.1f} b/s ({v/20:.2f} b/t) "
                      f"fs={fs} thr={th[k] if k < len(th) else '?'} y={p[1]:.0f}", flush=True)
        prev[pid] = (p, t)
    txt = open(LOG, encoding="utf-8", errors="replace").read()
    for line in txt[log_pos:].splitlines():
        if "moved too quickly" in line or "moved wrongly" in line or "Can't keep up" in line:
            print("LOG", line[-160:], flush=True)
    log_pos = len(txt)
    if t - last_tick > 30:
        q = e.cmd("tick query")
        m = re.search(r"Average time per tick: ([\d.]+)ms.*P95: ([\d.]+)ms P99: ([\d.]+)ms", q.replace("\n", " "))
        if m:
            print(f"{time.strftime('%H:%M:%S')} tick avg {m.group(1)} ms P95 {m.group(2)} P99 {m.group(3)}", flush=True)
        last_tick = t
    time.sleep(max(0.0, 0.25 - (time.time() - t)))
print("BEST", {f"{k[0]} id{k[1]}": (round(v[0], 1), v[1], v[2]) for k, v in best.items()}, flush=True)
