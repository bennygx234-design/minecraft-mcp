"""Generate the ewr_planes datapack (flyable airliners + private jets on harnessed happy ghasts).

Vanilla Minecraft Java 26.3 (data pack format 121.0). Re-run this script, then `/reload`.

    python build_planes.py            # writes the pack
    python build_planes.py --preview  # also writes preview_<livery>_<size>.png (top/side/front/3-4 view)

Design
- Vehicle: adult happy_ghast wearing a harness, invisible, silent, invulnerable, boosted
  minecraft:flying_speed and shrunk with minecraft:scale (the seat height is 4 * scale), so the
  rider sits in the cockpit of a slim fuselage. Unridden: NoAI on (no wandering / turning) and it
  sinks gently to the ground. Ridden: NoAI off so the player can steer.
- Model: block_display parts. They are teleported to the ghast (teleport_duration 1 = smooth)
  every tick while it is ridden, and only when something changed while parked (plus a resync
  every 10 s), rotated to the ghast's yaw and half the pilot's pitch, pivoting at the seat.
- Parts and ghast share a scoreboard id (ewr_id) so any number of planes can exist; orphaned
  parts (ghast gone) are removed every 2 s.
"""
from __future__ import annotations

import json
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import airliner_model as AM  # noqa: E402

PACK = r"C:\Users\benny\minecraft-mcp\server\world\datapacks\ewr_planes"
NS = "ewr_planes"

# Happy ghast ridden physics (26.3 bytecode): input = (strafe, pitch-y, forward) * 3.9 * flying_speed,
# normalised if longer than 1, accelerated by flying_speed * 5/3 per tick, air drag 0.91/tick. So the
# top speed in blocks/tick is ~ 72.2 * fs^2 for fs < 0.256 and ~ 18.5 * fs above.
# The vanilla vehicle check snaps a ridden vehicle back if one move packet exceeds 10 blocks (d^2 > 100),
# independent of gamerules -> keep top speeds below ~9 blocks/tick.
def top_bpt(fs):
    return (5.0 / 3.0) * fs * min(1.0, 3.9 * fs) / 0.09


# flying_speed x1000 per class: taxi (on the ground), cruise (airborne, no throttle), max (full throttle)
CLASS_SPEED = {"airliner": dict(taxi=80, cru=170, max=204),
               "private": dict(taxi=80, cru=165, max=197),
               "b2": dict(taxi=80, cru=180, max=217)}
# throttle caps: fraction of the way from cruise to the class max (slow = below cruise)
TIERS = {"slow": -1, "cruise": 0.0, "fast": 0.33, "turbo": 0.66, "max": 1.0}
DEFAULT_SPEED = 0.08
RAMP = 80   # ticks of holding W to go from cruise to the cap (4 s)

# k = model scale, stretch = extra cabin length (narrowbody units), zo = model shift (seat -> cockpit)
SIZES = {
    "regional": dict(k=0.78, stretch=-2.5, zo=-3.4, kind="airliner"),
    "narrow": dict(k=1.0, stretch=0.0, zo=-3.4, kind="airliner"),
    "wide": dict(k=1.25, stretch=1.0, zo=-3.4, kind="airliner"),
    "private": dict(k=1.0, stretch=0.0, zo=-2.0, kind="private"),
    "b2": dict(k=1.0, stretch=0.0, zo=-3.0, kind="b2"),
}

W, LG, G, BK = "white_concrete", "light_gray_concrete", "gray_concrete", "black_concrete"
NAVY, BLUE, TEAL = "blue_concrete", "light_blue_concrete", "cyan_concrete"


def solid(blk):
    return lambda i, j: blk


LIVERIES = {
    "ewr": dict(label="EWR Air", body=W, belly=LG, stripe=TEAL, titles=TEAL, wing=LG, engine=LG,
                winglet=TEAL, fin=lambda i, j: BLUE if i in (2, 3) else TEAL, harness="cyan_harness",
                size="narrow"),
    "united": dict(label="United", body=W, belly=NAVY, stripe=NAVY, titles=NAVY, wing=LG, engine=NAVY,
                   winglet=NAVY, fin=solid(NAVY), emblem=(4.0, 0.5, 0.75, BLUE, NAVY),
                   harness="blue_harness", size="narrow"),
    "delta": dict(label="Delta", body=W, belly=NAVY, stripe=None, titles=NAVY, wing=LG, engine=NAVY,
                  winglet=NAVY, harness="red_harness", size="narrow",
                  fin=lambda i, j: NAVY if i <= 1 or (j == 2 and i <= 4) else
                  ("red_concrete" if j == 0 or i >= 5 else "red_terracotta")),
    "american": dict(label="American", body=LG, belly=G, stripe=None, titles=NAVY, wing=G,
                     engine=LG, winglet="red_concrete", harness="light_gray_harness", size="narrow",
                     fin=lambda i, j: ["red_concrete", "red_concrete", W, "red_concrete", W, NAVY, NAVY,
                                       NAVY][i]),
    "jetblue": dict(label="JetBlue", body=W, belly=NAVY, stripe=None, titles=NAVY, wing=LG, engine=NAVY,
                    winglet=NAVY, harness="blue_harness", size="narrow",
                    fin=lambda i, j: NAVY if (i + j) % 2 else BLUE),
    "alaska": dict(label="Alaska", body=W, belly=W, stripe=TEAL, titles=NAVY, wing=LG, engine=NAVY,
                   winglet=TEAL, harness="cyan_harness", size="narrow",
                   fin=lambda i, j: TEAL if i <= 1 or (j == 0 and i <= 3) else NAVY,
                   emblem=(5.0, 0.55, 0.5, W)),
    "spirit": dict(label="Spirit", body="yellow_concrete", belly="yellow_concrete", stripe=BK, titles=BK,
                   wing="yellow_concrete", engine="yellow_concrete", winglet=BK, harness="yellow_harness",
                   size="narrow", fin=lambda i, j: BK if i >= 6 else "yellow_concrete"),
    "lufthansa": dict(label="Lufthansa", body=W, belly=LG, stripe=None, titles=NAVY, wing=LG, engine=NAVY,
                      winglet=NAVY, fin=solid(NAVY), emblem=(4.0, 0.5, 0.8, "yellow_concrete", NAVY),
                      harness="blue_harness", size="narrow"),
    "emirates": dict(label="Emirates", body=W, belly=W, stripe=None, titles="gold_block", wing=LG, engine=W,
                     winglet="red_concrete", harness="red_harness", size="wide", engines=4,
                     fin=lambda i, j: (W if i <= 1 else "red_concrete") if j == 0 else
                     ([W, W, BK, BK, W, W, "green_concrete", "green_concrete"][i])),
    "fedex": dict(label="FedEx", body=W, belly=LG, stripe=None, titles="purple_concrete", wing=LG,
                  engine="purple_concrete", winglet="purple_concrete", harness="purple_harness", size="wide",
                  fin=lambda i, j: "orange_concrete" if 2 <= i <= 4 and j >= 1 else "purple_concrete"),
    "ups": dict(label="UPS", body=W, belly="brown_concrete", stripe="yellow_concrete", titles="brown_concrete",
                wing=LG, engine="brown_concrete", winglet="brown_concrete", harness="brown_harness",
                size="narrow", tailcone="brown_concrete",
                fin=solid("brown_concrete"), emblem=(3.6, 0.45, 0.7, "yellow_concrete", "brown_concrete")),
    # private jets (size "private")
    "pj_blue": dict(label="Private jet", body=W, stripe=NAVY, stripe2=BLUE, wing=LG, engine=LG,
                    fin=lambda i, j: NAVY if i >= 4 else W, harness="white_harness", size="private"),
    "pj_red": dict(label="Private jet", body=W, stripe="red_concrete", stripe2=G, wing=LG, engine=LG,
                   fin=lambda i, j: "red_concrete" if i >= 4 else W, harness="white_harness", size="private"),
    "pj_gold": dict(label="Private jet", body=W, stripe="gold_block", stripe2=BK, wing=LG, engine=G,
                    fin=lambda i, j: "gold_block" if i >= 4 else W, harness="white_harness", size="private"),
    # military
    "b2": dict(label="B-2 Spirit", body=G, dark=BK, harness="gray_harness", size="b2"),
}
AIRLINES = [n for n, c in LIVERIES.items() if c["size"] not in ("private", "b2")]
PRIVATE = [n for n, c in LIVERIES.items() if c["size"] == "private"]


# ---------------------------------------------------------------- geometry helpers
def qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
            aw * bw - ax * bx - ay * by - az * bz)


def qaxis(axis, deg):
    h = math.radians(deg) / 2
    s = math.sin(h)
    x, y, z = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[axis]
    return (x * s, y * s, z * s, math.cos(h))


def qrot(q, v):
    x, y, z, w = q
    r = qmul(qmul(q, (v[0], v[1], v[2], 0.0)), (-x, -y, -z, w))
    return r[:3]


class Part:
    """A box: centre (feet frame), size, block, rotations [(axis, deg)] about the centre."""

    def __init__(self, center, size, block, rots=()):
        self.center, self.size, self.block = center, size, block
        q = (0.0, 0.0, 0.0, 1.0)
        for axis, deg in rots:
            q = qmul(q, qaxis(axis, deg))
        self.q = q

    def corners(self):
        sx, sy, sz = self.size
        out = []
        for dx in (-.5, .5):
            for dy in (-.5, .5):
                for dz in (-.5, .5):
                    r = qrot(self.q, (dx * sx, dy * sy, dz * sz))
                    out.append(tuple(self.center[i] + r[i] for i in range(3)))
        return out

    def nbt(self, seat):
        half = qrot(self.q, tuple(s / 2 for s in self.size))
        t = [self.center[0] - half[0], self.center[1] - seat - half[1], self.center[2] - half[2]]
        f = lambda v: (f"{v:.4f}".rstrip("0").rstrip(".") + "f") if abs(v) > 5e-5 else "0f"
        lst = lambda vs: "[" + ",".join(f(v) for v in vs) + "]"
        return ("{block_state:\"minecraft:%s\",teleport_duration:1,view_range:3f,"
                "Tags:[\"ewr_part\",\"ewr_new\"],transformation:{left_rotation:%s,"
                "right_rotation:[0f,0f,0f,1f],translation:%s,scale:%s}}"
                % (self.block, lst(self.q), lst(t), lst(self.size)))


def model(livery, size):
    c = LIVERIES[livery]
    sz = SIZES[size]
    b = AM.Builder(Part, qmul, qaxis, qrot, k=sz["k"], zo=sz["zo"])
    if sz["kind"] == "private":
        return AM.private_jet(c, b)
    if sz["kind"] == "b2":
        return AM.b2_spirit(c, b)
    return AM.airliner(c, b, stretch=sz["stretch"], engines=c.get("engines", 2) if size == "wide" else 2)


def size_info(size):
    """seat height (= 4 * ghast scale) a bit below the fuselage top; nose distance ahead of the ghast"""
    sz = SIZES[size]
    top = (1.05 + 0.9 * 0.62) if sz["kind"] == "private" else (1.85 + 0.9) * sz["k"]
    seat = round(top - (0.6 if sz["kind"] == "private" else 0.75), 2)
    if sz["kind"] == "b2":
        seat = 2.0
    parts = model({"private": "pj_blue", "b2": "b2"}.get(sz["kind"], "ewr"), size)
    cs = [cn for p in parts for cn in p.corners()]
    nose, tail = max(c[2] for c in cs), min(c[2] for c in cs)
    return dict(seat=seat, scale=round(seat / 4, 4), nose=round(nose, 2), length=round(nose - tail, 1),
                span=round(max(c[0] for c in cs) * 2, 1), height=round(max(c[1] for c in cs), 1))


for _s in SIZES:
    SIZES[_s].update(size_info(_s))


# ---------------------------------------------------------------- pack writer
def w(rel, text):
    path = os.path.join(PACK, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text.strip() + "\n")


def F(name, text):
    w(f"data/{NS}/function/{name}.mcfunction", text)


GHAST_NBT = ("{Tags:[\"ewr_plane\",\"ewr_new\",\"ewr_parked\",\"ewr_dirty\"],"
             "equipment:{body:{id:\"minecraft:%s\",count:1}},drop_chances:{body:0f},"
             "PersistenceRequired:1b,Silent:1b,Invulnerable:1b,NoAI:1b,home_radius:0,"
             "active_effects:[{id:\"minecraft:invisibility\",duration:-1,amplifier:0b,show_particles:0b,"
             "show_icon:0b,ambient:1b}],attributes:[{id:\"minecraft:flying_speed\",base:%sd},"
             "{id:\"minecraft:scale\",base:%sd}],CustomName:\"%s\",CustomNameVisible:0b}")


def tell(text):
    return 'tellraw @s [{"text":"[Planes] ","color":"aqua"},{"text":"%s","color":"white"}]' % text


def cls(size):
    return {"private": "private", "b2": "b2"}.get(SIZES[size]["kind"], "airliner")


def build_pack():
    if os.path.isdir(PACK):
        shutil.rmtree(PACK)
    w("pack.mcmeta", json.dumps({"pack": {
        "description": "EWR flyable airliners + private jets (happy ghast + block displays)",
        "min_format": [121, 0], "max_format": [121, 0]}}, indent=2))
    w("data/minecraft/tags/function/tick.json", json.dumps({"values": [f"{NS}:tick"]}, indent=2))
    w("data/minecraft/tags/function/load.json", json.dumps({"values": [f"{NS}:load"]}, indent=2))

    F("load", """
scoreboard objectives add ewr_id dummy
scoreboard objectives add ewr_pl dummy
scoreboard objectives add ewr_seat dummy
scoreboard objectives add ewr_thr dummy
scoreboard objectives add ewr_vl dummy
scoreboard objectives add ewr_taxi dummy
scoreboard objectives add ewr_cru dummy
scoreboard objectives add ewr_max dummy
scoreboard objectives add ewr_top dummy
function ewr_planes:internal/migrate
execute unless score #next ewr_id matches 1.. run scoreboard players set #next ewr_id 0
""")
    F("tick", f"""
execute as @e[type=happy_ghast,tag=ewr_plane] at @s run function {NS}:internal/plane_tick
scoreboard players add #t ewr_pl 1
execute if score #t ewr_pl matches 40.. run function {NS}:internal/maintain
""")
    F("internal/plane_tick", f"""
scoreboard players set #ridden ewr_pl 0
execute on controller if entity @s[type=player] run scoreboard players set #ridden ewr_pl 1
execute if score #ridden ewr_pl matches 1 if entity @s[tag=ewr_parked] run function {NS}:internal/wake
execute if score #ridden ewr_pl matches 0 if entity @s[tag=!ewr_parked] run function {NS}:internal/park
execute if score #ridden ewr_pl matches 0 run function {NS}:internal/settle
execute if score #ridden ewr_pl matches 0 unless entity @s[tag=ewr_dirty] run return 0
tag @s remove ewr_dirty
execute if score #ridden ewr_pl matches 1 run function {NS}:internal/throttle
scoreboard players operation #cur ewr_id = @s ewr_id
scoreboard players set #pitch ewr_pl 0
execute if score #ridden ewr_pl matches 1 on controller store result score #pitch ewr_pl run data get entity @s Rotation[1] 0.5
execute if score #pitch ewr_pl matches 21.. run scoreboard players set #pitch ewr_pl 20
execute if score #pitch ewr_pl matches ..-21 run scoreboard players set #pitch ewr_pl -20
execute store result storage {NS}:tmp pitch int 1 run scoreboard players get #pitch ewr_pl
execute store result storage {NS}:tmp seat float 0.01 run scoreboard players get @s ewr_seat
data modify storage {NS}:tmp r set value 32
execute if entity @s[tag=ewr_far] run data modify storage {NS}:tmp r set value 100000
tag @s remove ewr_far
function {NS}:internal/sync with storage {NS}:tmp
""")
    F("internal/sync", """
$execute as @e[type=block_display,tag=ewr_part,distance=..$(r)] if score @s ewr_id = #cur ewr_id run tp @s ~ ~$(seat) ~ ~ $(pitch)
""")
    F("internal/wake", """
data merge entity @s {NoAI:0b}
tag @s remove ewr_parked
scoreboard players set @s ewr_thr 0
scoreboard players set @s ewr_vl -1
""")
    F("internal/throttle", f"""
# forward held -> throttle +1/tick (RAMP ticks to full), released -> -2/tick; grounded -> taxi speed
scoreboard players set #fwd ewr_pl 0
execute on controller if predicate {NS}:forward run scoreboard players set #fwd ewr_pl 1
execute if score #fwd ewr_pl matches 1 run scoreboard players add @s ewr_thr 1
execute if score #fwd ewr_pl matches 0 run scoreboard players remove @s ewr_thr 2
execute if score @s ewr_thr matches {RAMP}.. run scoreboard players set @s ewr_thr {RAMP}
execute if score @s ewr_thr matches ..-1 run scoreboard players set @s ewr_thr 0
scoreboard players set #gnd ewr_pl 0
execute unless block ~ ~-0.3 ~ #minecraft:air run scoreboard players set #gnd ewr_pl 1
execute if score #gnd ewr_pl matches 1 run scoreboard players set @s ewr_thr 0
# v = cru + (top - cru) * thr / RAMP ; slow tier (top < cru) = flat top ; ground = taxi
scoreboard players operation #v ewr_pl = @s ewr_top
scoreboard players operation #v ewr_pl -= @s ewr_cru
scoreboard players operation #v ewr_pl *= @s ewr_thr
scoreboard players set #ramp ewr_pl {RAMP}
scoreboard players operation #v ewr_pl /= #ramp ewr_pl
scoreboard players operation #v ewr_pl += @s ewr_cru
execute if score @s ewr_top < @s ewr_cru run scoreboard players operation #v ewr_pl = @s ewr_top
execute if score #gnd ewr_pl matches 1 run scoreboard players operation #v ewr_pl = @s ewr_taxi
execute if score #v ewr_pl = @s ewr_vl run return 0
scoreboard players operation @s ewr_vl = #v ewr_pl
execute store result storage {NS}:tmp v double 0.001 run scoreboard players get #v ewr_pl
function {NS}:internal/set_speed with storage {NS}:tmp
""")
    F("internal/set_speed", """
$attribute @s minecraft:flying_speed base set $(v)
""")
    w("data/" + NS + "/predicate/forward.json", json.dumps({
        "type": "minecraft:entity_properties", "entity": "this",
        "predicate": {"minecraft:type_specific/player": {"input": {"forward": True}}}}, indent=2))
    F("internal/park", """
data merge entity @s {NoAI:1b,Motion:[0.0d,0.0d,0.0d]}
tag @s add ewr_parked
tag @s add ewr_dirty
""")
    # unridden: sink slowly while the ghast's footprint (5 probes) is over air
    F("internal/settle", f"""
execute if block ~ ~-0.15 ~ #minecraft:air if block ~0.6 ~-0.15 ~0.6 #minecraft:air if block ~-0.6 ~-0.15 ~0.6 #minecraft:air if block ~0.6 ~-0.15 ~-0.6 #minecraft:air if block ~-0.6 ~-0.15 ~-0.6 #minecraft:air if entity @s[y=-60,dy=400] run function {NS}:internal/sink
""")
    F("internal/sink", """
tp @s ~ ~-0.125 ~
tag @s add ewr_dirty
""")
    F("internal/maintain", f"""
scoreboard players set #t ewr_pl 0
execute as @e[type=happy_ghast,tag=ewr_plane] unless items entity @s armor.body #minecraft:harnesses run item replace entity @s armor.body with minecraft:white_harness
execute as @e[type=happy_ghast,tag=ewr_plane,tag=ewr_parked] run data merge entity @s {{NoAI:1b,Motion:[0.0d,0.0d,0.0d]}}
effect give @e[type=happy_ghast,tag=ewr_plane] minecraft:invisibility infinite 0 true
scoreboard players add #t2 ewr_pl 1
execute if score #t2 ewr_pl matches 3 run function {NS}:internal/orphans
execute if score #t2 ewr_pl matches 5.. run tag @e[type=happy_ghast,tag=ewr_plane] add ewr_dirty
execute if score #t2 ewr_pl matches 5.. run scoreboard players set #t2 ewr_pl 0
""")
    # orphan parts (ghast gone): every ghast tags its own parts nearby, untagged parts are removed
    F("internal/orphans", f"""
execute as @e[type=happy_ghast,tag=ewr_plane] at @s run function {NS}:internal/tag_own
kill @e[type=block_display,tag=ewr_part,tag=!ewr_ok]
tag @e[type=block_display,tag=ewr_ok] remove ewr_ok
""")
    F("internal/tag_own", """
scoreboard players operation #cur ewr_id = @s ewr_id
execute as @e[type=block_display,tag=ewr_part,distance=..40] if score @s ewr_id = #cur ewr_id run tag @s add ewr_ok
""")
    F("resync", """
tag @e[type=happy_ghast,tag=ewr_plane] add ewr_dirty
tag @e[type=happy_ghast,tag=ewr_plane] add ewr_far
""")

    # --- build functions per livery x size
    count = {}
    for lv, c in LIVERIES.items():
        sizes = [c["size"]] if c["size"] in ("private", "b2") else ["regional", "narrow", "wide"]
        for size in sizes:
            sz = SIZES[size]
            parts = model(lv, size)
            count[(lv, size)] = len(parts)
            lines = [
                f"# {c['label']} {size}: {len(parts)} parts. context: position = ghast feet (ground), rotation = heading",
                "scoreboard players add #next ewr_id 1",
                "summon happy_ghast ~ ~ ~ " + GHAST_NBT % (c["harness"], DEFAULT_SPEED, sz["scale"],
                                                          f"{c['label']} ({size})"),
            ]
            lines += [f"summon block_display ~ ~{sz['seat']} ~ " + p.nbt(sz["seat"]) for p in parts]
            lines += [
                "scoreboard players operation @e[tag=ewr_new] ewr_id = #next ewr_id",
                f"scoreboard players set @e[type=happy_ghast,tag=ewr_new] ewr_seat {int(round(sz['seat'] * 100))}",
                f"execute as @e[type=happy_ghast,tag=ewr_new] run function {NS}:internal/class_{cls(size)}",
                "execute as @e[type=happy_ghast,tag=ewr_new] run tp @s ~ ~ ~ ~ 0",
                f"execute as @e[type=block_display,tag=ewr_new] run tp @s ~ ~{sz['seat']} ~ ~ 0",
                "tag @e[tag=ewr_new] remove ewr_new",
            ]
            F(f"internal/build_{lv}_{size}", "\n".join(lines))

    # --- player spawn: cockpit 8 blocks ahead (3 to the left so you stand beside the fuselage)
    def player_spawn(fname, lv, size):
        c = LIVERIES[lv]
        F(fname, f"""
# Spawns a {c['label']} {size} plane: cockpit 8 blocks ahead of you, nose facing where you look.
execute at @s rotated ~ 0 positioned ^3 ^ ^8 align y run function {NS}:internal/ground {{b:"{lv}_{size}"}}
{tell(f"{c['label']} ({size}) spawned. Right-click the cockpit (just behind the nose) to board.")}
""")

    for lv in AIRLINES:
        player_spawn(f"spawn_{lv}", lv, LIVERIES[lv]["size"])
        for size in ("regional", "narrow", "wide"):
            player_spawn(f"spawn/{lv}_{size}", lv, size)
    player_spawn("spawn", "ewr", "narrow")
    for lv in PRIVATE:
        player_spawn(f"spawn_private_{lv[3:]}", lv, "private")
    player_spawn("spawn_private", "pj_blue", "private")
    player_spawn("spawn_b2", "b2", "b2")

    # ground search (macro): move up out of blocks / down onto the ground, then build
    F("internal/ground", f"""
scoreboard players set #steps ewr_pl 0
$function {NS}:internal/seek {{b:"$(b)"}}
""")
    F("internal/seek", f"""
scoreboard players add #steps ewr_pl 1
$execute if score #steps ewr_pl matches 64.. run return run function {NS}:internal/build_$(b)
$execute unless block ~ ~ ~ #minecraft:replaceable positioned ~ ~1 ~ run return run function {NS}:internal/seek {{b:"$(b)"}}
$execute if block ~ ~-1 ~ #minecraft:replaceable unless block ~ ~-1 ~ minecraft:water positioned ~ ~-1 ~ run return run function {NS}:internal/seek {{b:"$(b)"}}
$function {NS}:internal/build_$(b)
""")
    F("spawn_at", f"""
# usage: function {NS}:spawn_at {{x:4,y:64,z:22,yaw:90,livery:"united",size:"narrow"}}
#   livery: {" | ".join(AIRLINES)}  (size regional | narrow | wide)
#           {" | ".join(PRIVATE)}  (size private)
#           b2  (size b2)
#   y = ground level (top of the ground block + 1). yaw: 0=S 90=W 180=N -90=E
$execute positioned $(x) $(y) $(z) rotated $(yaw) 0 run function {NS}:internal/build_$(livery)_$(size)
""")

    # --- removal
    F("remove_nearest", f"""
execute as @e[type=happy_ghast,tag=ewr_plane,sort=nearest,limit=1] at @s run function {NS}:internal/remove_self
{tell("Removed the nearest plane.")}
""")
    F("remove_all", f"""
execute as @e[type=happy_ghast,tag=ewr_plane] at @s run function {NS}:internal/remove_self
kill @e[type=block_display,tag=ewr_part]
""")
    F("internal/remove_self", """
scoreboard players operation #cur ewr_id = @s ewr_id
execute as @e[type=block_display,tag=ewr_part] if score @s ewr_id = #cur ewr_id run kill @s
execute on passengers run ride @s dismount
tp @s ~ -100 ~
kill @s
""")

    # --- speed presets (the plane you ride, else the nearest one)
    for cname, cs in CLASS_SPEED.items():
        F(f"internal/class_{cname}", f"""
scoreboard players set @s ewr_taxi {cs['taxi']}
scoreboard players set @s ewr_cru {cs['cru']}
scoreboard players set @s ewr_max {cs['max']}
scoreboard players set @s ewr_top {cs['max']}
scoreboard players set @s ewr_thr 0
scoreboard players set @s ewr_vl -1
""")
    # migrate planes spawned before the throttle existed (no ewr_max score yet)
    mig = []
    for lv, c in LIVERIES.items():
        for size in ([c["size"]] if c["size"] in ("private", "b2") else ["regional", "narrow", "wide"]):
            mig.append(f'execute as @e[type=happy_ghast,tag=ewr_plane,name="{c["label"]} ({size})"] '
                       f'unless score @s ewr_max matches 1.. run function {NS}:internal/class_{cls(size)}')
    mig.append(f"execute as @e[type=happy_ghast,tag=ewr_plane,tag=ewr_parked] run attribute @s "
               f"minecraft:flying_speed base set {DEFAULT_SPEED}")
    F("internal/migrate", "\n".join(mig))
    for tname, frac in TIERS.items():
        body = ["scoreboard players operation @s ewr_top = @s ewr_cru",
                "scoreboard players operation #d ewr_pl = @s ewr_max",
                "scoreboard players operation #d ewr_pl -= @s ewr_cru",
                f"scoreboard players set #f ewr_pl {int(round(max(frac, 0) * 100))}",
                "scoreboard players operation #d ewr_pl *= #f ewr_pl",
                "scoreboard players set #f ewr_pl 100",
                "scoreboard players operation #d ewr_pl /= #f ewr_pl",
                "scoreboard players operation @s ewr_top += #d ewr_pl"]
        if frac < 0:
            body += ["scoreboard players operation @s ewr_top = @s ewr_taxi", "scoreboard players add @s ewr_top 40"]
        body.append("scoreboard players set @s ewr_vl -1")
        F(f"internal/tier_{tname}", "\n".join(body))
        F(f"speed/{tname}", f"""
scoreboard players set #onv ewr_pl 0
execute on vehicle if entity @s[tag=ewr_plane] store success score #onv ewr_pl run function {NS}:internal/tier_{tname}
execute if score #onv ewr_pl matches 0 as @e[type=happy_ghast,tag=ewr_plane,sort=nearest,limit=1] run function {NS}:internal/tier_{tname}
{tell(f"Throttle limit set to {tname}. Hold W in the air to accelerate (about 4 s to full).")}
""")

    F("help", """
tellraw @s {"text":"--- EWR Planes ---","color":"aqua","bold":true}
tellraw @s {"text":"Spawn: /function ewr_planes:spawn_<airline>  (united delta american jetblue alaska spirit lufthansa emirates fedex ups ewr)","color":"white"}
tellraw @s {"text":"Other sizes: /function ewr_planes:spawn/<airline>_regional | _narrow | _wide","color":"white"}
tellraw @s {"text":"Private jet: /function ewr_planes:spawn_private  (or spawn_private_red / spawn_private_gold)","color":"white"}
tellraw @s {"text":"Military: /function ewr_planes:spawn_b2  (B-2 Spirit flying wing)","color":"white"}
tellraw @s {"text":"Board: right-click the cockpit. Fly: look to steer, W forward, Space climb, look down to descend, Shift = get off.","color":"white"}
tellraw @s {"text":"Speed: hold W in the air to throttle up (4 s). Limit: /function ewr_planes:speed/slow | cruise | fast | turbo | max (default max)","color":"white"}
tellraw @s {"text":"Top speeds: airliners ~60 blocks/s, private jets ~56, B-2 ~68 (vanilla rubber-bands faster vehicles). On the ground it taxis slowly.     Remove: /function ewr_planes:remove_nearest","color":"white"}
""")
    return count


# ---------------------------------------------------------------- preview (sanity check)
COLORS = {"white_concrete": (235, 235, 235), "light_gray_concrete": (160, 160, 155), "gray_concrete": (70, 72, 77),
          "black_concrete": (12, 14, 20), "cyan_concrete": (21, 120, 136), "light_blue_concrete": (36, 137, 199),
          "blue_concrete": (45, 47, 143), "red_concrete": (142, 33, 33), "lime_concrete": (94, 169, 24),
          "black_stained_glass": (25, 25, 30), "yellow_concrete": (240, 175, 21), "gold_block": (246, 208, 61),
          "green_concrete": (73, 91, 36), "purple_concrete": (100, 32, 156), "orange_concrete": (224, 97, 1),
          "brown_concrete": (96, 60, 32), "red_terracotta": (143, 61, 46)}


def preview(livery, size, out=None):
    from PIL import Image, ImageDraw
    parts = model(livery, size)
    img = Image.new("RGB", (1600, 1000), (120, 170, 220))
    d = ImageDraw.Draw(img)
    faces = [((0, 1, 3, 2), (-1, 0, 0)), ((4, 5, 7, 6), (1, 0, 0)), ((0, 1, 5, 4), (0, -1, 0)),
             ((2, 3, 7, 6), (0, 1, 0)), ((0, 2, 6, 4), (0, 0, -1)), ((1, 3, 7, 5), (0, 0, 1))]
    cy, sy = math.cos(math.radians(35)), math.sin(math.radians(35))
    iso = lambda p: (p[0] * cy - p[2] * sy, p[1], p[0] * sy + p[2] * cy)
    S0 = 17 / max(1.0, SIZES[size]["length"] / 24) * (1.8 if size == "private" else 1.0)
    views = [
        (lambda p: p, lambda p: (p[0], -p[2], p[1]), (300, 420), S0),
        (lambda p: p, lambda p: (-p[2], -p[1], p[0]), (1150, 200), S0 * 1.2),
        (lambda p: p, lambda p: (p[0], -p[1], p[2]), (1150, 430), S0 * 1.2),
        (iso, lambda p: (p[0], -p[1] * 0.8 + p[2] * 0.35, p[2] * 0.8 + p[1] * 0.35), (850, 780), S0 * 1.4),
    ]
    light = (0.3, 0.8, 0.5)
    for rot, proj, (ox, oy), S in views:
        polys = []
        for p in parts:
            cs = [rot(q) for q in p.corners()]
            for f, n in faces:
                nn = rot(qrot(p.q, n))
                sh = 0.55 + 0.45 * max(0.0, sum(nn[i] * light[i] for i in range(3)))
                pts = [proj(cs[i]) for i in f]
                k = sum(q[2] for q in pts) / 4
                col = tuple(int(v * sh) for v in COLORS.get(p.block, (255, 0, 255)))
                polys.append((k, [(ox + q[0] * S, oy + q[1] * S) for q in pts], col))
        for k, pts, col in sorted(polys, key=lambda t: t[0]):
            d.polygon(pts, fill=col)
    sz = SIZES[size]
    d.text((20, 20), f"{livery} {size}: {len(parts)} parts, length {sz['length']}, span {sz['span']}, "
                     f"height {sz['height']}, seat {sz['seat']}, ghast scale {sz['scale']}", fill=(0, 0, 0))
    out = out or os.path.join(HERE, f"preview_{livery}_{size}.png")
    img.save(out)
    return out


if __name__ == "__main__":
    cnt = build_pack()
    for cn, cs in CLASS_SPEED.items():
        print(cn, {k: f"fs {v/1000} -> {top_bpt(v/1000):.2f} b/t = {top_bpt(v/1000)*20:.0f} b/s" for k, v in cs.items()})
    for s, v in SIZES.items():
        print(s, {k: v[k] for k in ("seat", "scale", "nose", "length", "span", "height")})
    print("parts per build:", sorted(set(cnt.values())))
    if "--preview" in sys.argv:
        for lv, c in LIVERIES.items():
            print(preview(lv, c["size"]))
